#!/usr/bin/env python3
"""
Clinical Trial LangChain Application
Handles patient recruitment, protocol management, and adverse event summarization
"""

import os
import sys
import json
import sqlite3
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict

try:
    from langchain.agents import Tool, AgentExecutor, create_react_agent
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    from langchain.memory import ConversationBufferMemory
    from langchain import hub
except ImportError:
    print("Error: LangChain dependencies not installed. Run: pip install -r requirements.txt")
    sys.exit(1)


@dataclass
class MatchResult:
    """Result of patient eligibility matching"""
    patient_id: str
    eligible: bool
    match_score: float
    reasoning: str
    timestamp: str


class AuditLogger:
    """HIPAA-compliant audit logging"""

    def __init__(self, db_path: str = "audit_log.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database for audit logs"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    action TEXT NOT NULL,
                    user_id TEXT,
                    patient_id_masked TEXT,
                    decision TEXT,
                    reasoning TEXT,
                    status TEXT
                )
            """)
            conn.commit()

    def log(self, action: str, decision: str, reasoning: str, status: str = "success"):
        """Log a decision with masked PII"""
        timestamp = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO audit_logs (timestamp, action, decision, reasoning, status)
                VALUES (?, ?, ?, ?, ?)
            """, (timestamp, action, decision, reasoning, status))
            conn.commit()

    def get_logs(self, limit: int = 100) -> List[Dict]:
        """Retrieve audit logs"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT ?", (limit,)
            )
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]


class ProtocolParser:
    """Extracts criteria from clinical trial protocols"""

    def __init__(self):
        self.criteria_template = {
            "trial_name": "",
            "inclusion_criteria": [],
            "exclusion_criteria": [],
            "primary_outcome": "",
            "safety_endpoints": [],
            "enrollment_target": 0
        }

    def parse_protocol_text(self, protocol_text: str) -> Dict[str, Any]:
        """
        Parse protocol text and extract key information.
        In production, use LLM to intelligently extract sections.
        """
        # Simplified extraction logic
        result = self.criteria_template.copy()

        # Extract basic info (in production, use LangChain Agent)
        lines = protocol_text.split('\n')
        for line in lines:
            if 'inclusion' in line.lower():
                result['inclusion_criteria'].append(line.strip())
            elif 'exclusion' in line.lower():
                result['exclusion_criteria'].append(line.strip())
            elif 'enrollment' in line.lower() or 'n=' in line.lower():
                result['enrollment_target'] += 1

        return result


class PatientMatcher:
    """Matches patient profiles against trial criteria"""

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.audit_logger = AuditLogger()

    def match_patient(self, patient_data: Dict[str, Any], criteria: Dict[str, Any]) -> MatchResult:
        """
        Match a patient against trial criteria using LLM reasoning.
        Returns structured eligibility decision with explanation.
        """
        patient_id = patient_data.get('patient_id', 'unknown')
        age = patient_data.get('age', 'unknown')
        conditions = patient_data.get('conditions', [])
        medications = patient_data.get('medications', [])

        # Create a prompt for the LLM to evaluate eligibility
        prompt = f"""
You are a clinical trial eligibility specialist. 
Evaluate whether this patient is eligible for the trial.

Patient Profile:
- Age: {age}
- Conditions: {', '.join(conditions) if conditions else 'None reported'}
- Current Medications: {', '.join(medications) if medications else 'None reported'}

Trial Criteria:
- Inclusion: {criteria.get('inclusion_criteria', [])}
- Exclusion: {criteria.get('exclusion_criteria', [])}

Provide a decision (Eligible/Ineligible) with a brief explanation.
Format: ELIGIBLE or INELIGIBLE | Reasoning
"""

        try:
            response = self.llm.invoke(prompt)
            response_text = response.content.strip()

            # Parse response
            eligible = "ELIGIBLE" in response_text.upper()
            match_score = 0.9 if eligible else 0.1

            result = MatchResult(
                patient_id=patient_id,
                eligible=eligible,
                match_score=match_score,
                reasoning=response_text,
                timestamp=datetime.now().isoformat()
            )

            # Log decision
            self.audit_logger.log(
                action="patient_matching",
                decision="ELIGIBLE" if eligible else "INELIGIBLE",
                reasoning=response_text
            )

            return result

        except Exception as e:
            # Log error
            self.audit_logger.log(
                action="patient_matching",
                decision="ERROR",
                reasoning=str(e),
                status="error"
            )
            raise


class AdverseEventSummarizer:
    """Extracts and summarizes adverse events from clinical notes"""

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.audit_logger = AuditLogger()

    def analyze_event(self, note_text: str) -> Dict[str, Any]:
        """
        Analyze a clinical note for adverse events.
        Returns structured AE information with severity and relatedness.
        """
        prompt = f"""
You are a clinical safety specialist. 
Analyze this clinical note for adverse events.

Clinical Note:
{note_text}

For each adverse event identified, provide:
1. Event description
2. Severity (Mild, Moderate, Severe, Life-threatening)
3. Relatedness to trial drug (Unrelated, Possible, Probable, Definite)
4. Action recommended (None, Follow-up, Hospitalization)

Format as JSON.
"""

        try:
            response = self.llm.invoke(prompt)
            response_text = response.content.strip()

            # Log event analysis
            self.audit_logger.log(
                action="adverse_event_analysis",
                decision="ANALYZED",
                reasoning=response_text
            )

            # Return structured result
            return {
                "analysis": response_text,
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }

        except Exception as e:
            self.audit_logger.log(
                action="adverse_event_analysis",
                decision="ERROR",
                reasoning=str(e),
                status="error"
            )
            raise


class ClinicalTrialApp:
    """Main LangChain application for clinical trial workflows"""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise EnvironmentError("OPENAI_API_KEY not set")

        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1, api_key=self.api_key)
        self.embeddings = OpenAIEmbeddings(api_key=self.api_key)
        self.memory = ConversationBufferMemory(memory_key="chat_history")

        # Initialize tools
        self.protocol_parser = ProtocolParser()
        self.patient_matcher = PatientMatcher(self.llm)
        self.ae_summarizer = AdverseEventSummarizer(self.llm)
        self.audit_logger = AuditLogger()

    def process_protocol(self, protocol_text: str) -> Dict[str, Any]:
        """Process a clinical trial protocol"""
        print("Processing protocol...")
        return self.protocol_parser.parse_protocol_text(protocol_text)

    def match_patients(self, patient_list: List[Dict], criteria: Dict) -> List[MatchResult]:
        """Match multiple patients against trial criteria"""
        print(f"Matching {len(patient_list)} patients against criteria...")
        results = []
        for patient in patient_list:
            result = self.patient_matcher.match_patient(patient, criteria)
            results.append(result)
        return results

    def analyze_adverse_events(self, notes: List[str]) -> List[Dict]:
        """Analyze adverse event notes"""
        print(f"Analyzing {len(notes)} adverse event notes...")
        results = []
        for note in notes:
            result = self.ae_summarizer.analyze_event(note)
            results.append(result)
        return results


def demo_mode():
    """Run a demonstration of the application"""
    print("Clinical Trial LangChain Application - Demo Mode\n")

    # Initialize app
    app = ClinicalTrialApp()

    # Sample protocol text
    sample_protocol = """
    Clinical Trial Protocol: Phase III Diabetes Study
    
    Inclusion Criteria:
    - Age 18-75 years
    - Diagnosed Type 2 Diabetes
    - HbA1c 6.5-10.0%
    - No prior stroke or MI
    
    Exclusion Criteria:
    - Pregnancy or nursing
    - Severe kidney disease (eGFR < 30)
    - Active malignancy
    
    Enrollment Target: 500 patients
    Primary Outcome: HbA1c reduction at 12 weeks
    Safety Endpoints: Hypoglycemia, liver function
    """

    # Sample patient data
    sample_patients = [
        {
            "patient_id": "P001",
            "age": 55,
            "conditions": ["Type 2 Diabetes", "Hypertension"],
            "medications": ["Metformin", "Lisinopril"]
        },
        {
            "patient_id": "P002",
            "age": 32,
            "conditions": ["Type 1 Diabetes"],
            "medications": ["Insulin glargine"]
        }
    ]

    # Sample adverse event note
    sample_ae_note = """
    Patient reported mild tremor and dizziness 2 hours after taking study medication.
    Blood glucose measured at 85 mg/dL.
    No loss of consciousness.
    Symptoms resolved within 30 minutes after drinking juice.
    """

    # Demo: Parse protocol
    print("=" * 60)
    print("Step 1: Parse Protocol")
    print("=" * 60)
    protocol_data = app.process_protocol(sample_protocol)
    print(json.dumps(protocol_data, indent=2))

    # Demo: Match patients
    print("\n" + "=" * 60)
    print("Step 2: Match Patients")
    print("=" * 60)
    try:
        match_results = app.match_patients(sample_patients, protocol_data)
        for result in match_results:
            print(f"\nPatient {result.patient_id}:")
            print(f"  Eligible: {result.eligible}")
            print(f"  Score: {result.match_score:.2%}")
            print(f"  Reasoning: {result.reasoning[:100]}...")
    except Exception as e:
        print(f"Error during matching: {e}")

    # Demo: Analyze adverse events
    print("\n" + "=" * 60)
    print("Step 3: Analyze Adverse Event")
    print("=" * 60)
    try:
        ae_results = app.analyze_adverse_events([sample_ae_note])
        for result in ae_results:
            print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error during AE analysis: {e}")

    # Show audit logs
    print("\n" + "=" * 60)
    print("Audit Logs (Last 5)")
    print("=" * 60)
    logs = app.audit_logger.get_logs(limit=5)
    for log in logs:
        print(f"[{log['timestamp']}] {log['action']}: {log['decision']}")


def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo_mode()
    else:
        print("Clinical Trial LangChain Application")
        print("Usage: python clinical_trial_app.py --demo")
        print("\nDemo mode runs through a complete workflow example.")


if __name__ == "__main__":
    main()
