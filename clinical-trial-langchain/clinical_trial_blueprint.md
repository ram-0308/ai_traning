# Clinical Trial LangChain Blueprint

## Executive Summary
This document outlines a production-ready LangChain application for clinical trial workflows, focusing on protocol management, patient recruitment, and regulatory compliance. The MVP handles document processing, patient matching, and adverse event summarization with built-in HIPAA considerations.

## 1. Clinical Trial Use Case Selection

### Primary Use Case: Patient Recruitment and Protocol Matching
- **Audience**: Clinical trial coordinators, patient recruitment teams
- **Problem**: Manual review of protocols and EHR data to identify eligible patients is time-consuming and error-prone
- **Solution**: Automated matching of patient profiles against trial inclusion/exclusion criteria using LangChain agents and vector search

### Secondary Use Cases (In Scope for MVP):
1. **Protocol Extraction**: Parse trial protocols (PDFs) to extract eligibility criteria, enrollment targets, and safety requirements
2. **Adverse Event Summarization**: Extract and categorize safety events from clinical notes
3. **Eligibility Verification**: Validate patient data against structured criteria with explanation

## 2. System Architecture

### High-Level Overview
```
User Input (PDF, EHR Data)
    ↓
Document Processor (PyPDF2/PDFPlumber)
    ↓
LangChain Agent (Protocol/Patient Analyzer)
    ↓
Tools: OCR, Regex Parser, Vector DB Lookup, Compliance Checker
    ↓
Memory Manager (Persistent Session + Knowledge Base)
    ↓
Output: Structured JSON + Audit Log
```

### Core Components

#### 2.1 LangChain Agents
- **ProtocolAgent**: Extracts eligibility criteria and safety requirements from trial protocols
- **PatientMatchingAgent**: Compares patient profiles against criteria
- **SafetyAgent**: Identifies and categorizes adverse events
- **RegulatoryAgent**: Validates HIPAA compliance and generates audit logs

#### 2.2 Tools (Custom LangChain Tools)
```python
Tools:
- PDFParser: Extract text from clinical trial protocols
- EHRExtractor: Parse patient EHR summaries
- CriteriaValidator: Check eligibility match with explanation
- AuditLogger: Log all decisions with timestamps and user info
- PII_Masker: Remove/encrypt sensitive data
```

#### 2.3 Memory System
- **ConversationBuffer**: Maintain context within a session
- **Persistent Store**: SQLite for previous decisions and audit trails
- **Vector DB**: FAISS or Pinecone for semantic search of protocols and patient profiles

#### 2.4 LLM and Embeddings
- **Primary LLM**: OpenAI GPT-4 (or GPT-4o-mini for cost efficiency)
- **Embeddings**: OpenAI text-embedding-3-small for biomedical text
- **Fallback**: Local embeddings (sentence-transformers) for air-gapped environments

## 3. Data Inputs and Processing

### Input Format 1: Clinical Trial Protocols (PDF)
```
Input: protocol.pdf
Processing:
  1. Extract raw text (PyPDF2)
  2. Parse sections: Objective, Eligibility, Safety, Enrollment
  3. Vectorize eligibility criteria
  4. Store in vector DB for semantic search
Output: Structured JSON with extracted criteria
```

### Input Format 2: Patient Data (CSV/EHR Summary)
```
Input: patient_data.csv (columns: age, conditions, medications, labs)
Processing:
  1. Clean and validate patient data
  2. Create patient profile embedding
  3. Compare against protocol criteria vectors
  4. Generate match score + explanation
Output: JSON with match results and reasoning
```

### Input Format 3: Clinical Notes (Text)
```
Input: adverse_event_note.txt
Processing:
  1. Identify AE signals using LLM
  2. Categorize by severity and relatedness
  3. Log with timestamp and reporter info
Output: Structured adverse event record
```

## 4. Recommended Models and Tools

### LLM Configuration
- **Model**: GPT-4 for clinical reasoning
- **Temperature**: 0.1 (low randomness for consistency)
- **Max Tokens**: 1024 (balance completeness vs. cost)

### Embeddings
- **Model**: text-embedding-3-small
- **Dimension**: 1536
- **Use Case**: Semantic search across protocols and patient data

### Vector Database
- **Development**: FAISS (local, free)
- **Production**: Pinecone or Weaviate (managed, scalable)

### Supporting Libraries
- `langchain` - Framework
- `openai` - LLM API
- `pypdf` or `pdfplumber` - Document parsing
- `faiss-cpu` - Vector search
- `sqlalchemy` - Database ORM
- `cryptography` - Data encryption

## 5. Compliance and Security

### HIPAA Considerations
- **Data Minimization**: Process only necessary data fields
- **Encryption**: Encrypt PII at rest (AES-256) and in transit (TLS 1.3)
- **Access Control**: Role-based access (e.g., only trial coordinators see patient data)
- **Audit Trail**: Log all decisions, data access, and modifications with timestamps
- **Data Retention**: Delete processed data per retention schedule (default: 90 days)

### Compliance Features
1. **PII Masking**: Automatically mask patient names, IDs, and addresses in logs
2. **Audit Logging**: Immutable log of all data access and LLM decisions
3. **Consent Tracking**: Flag when patient consent is required/obtained
4. **Data Breach Notification**: Alert on unusual access patterns

### Regulatory Alignment
- **21 CFR Part 11**: Validates electronic record integrity
- **GDPR**: Right to explanation for automated decisions (included in output)
- **HIPAA**: Business Associate Agreement (BAA) required with OpenAI

## 6. MVP Feature Set

### Tier 1 (Core MVP)
- ✅ Protocol document parsing and criteria extraction
- ✅ Patient eligibility matching with pass/fail + explanation
- ✅ Simple adverse event flagging
- ✅ Audit logging for compliance

### Tier 2 (Nice-to-Have, Post-MVP)
- Document similarity search (find related protocols)
- Multi-criteria weighted matching
- Interactive refinement of criteria
- Bulk patient batch processing

### Out of Scope (Not in MVP)
- ❌ Real-time EHR integration
- ❌ Advanced statistical analysis
- ❌ Clinical trial recruitment portal frontend
- ❌ Advanced drug interaction checking

## 7. Tech Stack

### Backend
- **Language**: Python 3.10+
- **Framework**: FastAPI (for REST API, optional)
- **LangChain**: 0.1.x or later

### Database
- **Metadata**: SQLite (development) → PostgreSQL (production)
- **Vector Store**: FAISS (local) → Pinecone (cloud)

### Frontend (Optional for MVP)
- Simple CLI interface using `click` or `argparse`
- Web UI (Vue/React) can be added post-MVP

### Deployment
- **Local**: Python script + CLI
- **Docker**: Containerized with environment secrets
- **Cloud**: AWS Lambda + RDS, or Azure Container Instances
- **Compliance**: Deploy in HIPAA-eligible AWS regions (encrypted storage, VPC isolation)

## 8. Workflow Explanation

### Workflow A: Patient Eligibility Matching
```
Coordinator uploads protocol PDF and patient list (CSV)
    ↓
ProtocolAgent extracts criteria from PDF
    - Parses age range, diagnoses, lab values, medications
    - Vectorizes criteria for semantic matching
    ↓
PatientMatchingAgent processes each patient
    - Compares patient data against vectorized criteria
    - Generates match score (0-100%) and reasoning
    ↓
Output Report
    - Patient name (masked in audit log)
    - Match status: Eligible / Ineligible / Uncertain
    - Explanation: "Patient matches age criterion (45, range 18-65) and diagnosis (diabetes)"
    ↓
AuditLogger records decision with timestamp, user, and reasoning
```

### Workflow B: Adverse Event Summarization
```
Clinical coordinator pastes adverse event note
    ↓
SafetyAgent analyzes the note
    - Identifies AE signals using medical knowledge
    - Assigns severity (Mild, Moderate, Severe, Life-threatening)
    - Determines relationship to trial drug (Unrelated, Possible, Probable, Definite)
    ↓
Output: Structured AE record
    - Event description, onset date, severity, relatedness
    - Recommended action (none, follow-up labs, hospitalization)
    ↓
AuditLogger stores with full context
```

## 9. Implementation Roadmap

### Phase 1 (Week 1-2)
- Set up LangChain agents, memory, and tools
- Build document parser for protocols
- Create basic patient validator
- Implement SQLite audit logging

### Phase 2 (Week 3-4)
- Integrate OpenAI embeddings and vector DB
- Enhanced eligibility criteria matching
- Adverse event extraction logic
- HIPAA compliance checks

### Phase 3 (Week 5-6)
- Testing and validation with sample data
- Documentation and deployment guides
- Optional: CLI interface refinements
- Optional: API wrapper for integration

## 10. Key Assumptions
- Protocols are in PDF format (not handwritten or scanned images)
- Patient data is available in structured format (CSV or EHR API)
- OpenAI API access is available
- HIPAA compliance is managed at infrastructure level (encrypted storage, VPC, etc.)
- Input data is de-identified before processing (patient ID instead of full name)

## 11. Data Security Checklist
- [ ] All API calls use HTTPS/TLS 1.3
- [ ] PII is masked in logs and error messages
- [ ] Database credentials stored in environment variables (not code)
- [ ] Audit logs are immutable (append-only, timestamped)
- [ ] Encryption key rotated quarterly
- [ ] Access logs reviewed for unusual patterns
- [ ] Data retention policy enforced (auto-delete after 90 days)