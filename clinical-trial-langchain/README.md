# Clinical Trial LangChain Application

A production-ready LangChain application for clinical trial document processing and patient recruitment workflows.

## Project Structure
- `clinical_trial_blueprint.md` - Complete system design and architecture
- `clinical_trial_app.py` - Main LangChain application
- `agents.py` - Custom LangChain agents and tools
- `memory_manager.py` - Session and knowledge memory handling
- `requirements.txt` - Python dependencies

## Quick Start

### 1. Setup
```bash
python -m pip install -r requirements.txt
```

### 2. Set API Keys
```powershell
$env:OPENAI_API_KEY = "your_api_key_here"
```

### 3. Run the Application
```bash
# Process a clinical trial document
python clinical_trial_app.py --document "path/to/protocol.pdf"

# Run patient matching
python clinical_trial_app.py --mode "patient_matching" --criteria "age>18,condition:diabetes"

# Interactive mode
python clinical_trial_app.py --interactive
```

## Features
- **Protocol Management**: Extract and summarize clinical trial protocols
- **Patient Recruitment**: Match patient data against inclusion/exclusion criteria
- **Data Extraction**: Parse unstructured clinical documents
- **Adverse Event Reporting**: Summarize and categorize safety events
- **Regulatory Compliance**: HIPAA-compliant processing with audit trails

## Architecture
- **Framework**: LangChain with OpenAI GPT-4
- **Memory**: ConversationBufferMemory with persistent storage
- **Tools**: Custom agents for document processing, data extraction, compliance checks
- **Database**: SQLite for metadata, vector embeddings for semantic search
- **Compliance**: HIPAA audit logging, data encryption, role-based access control

## Notes
All data is processed locally and securely. PII is masked during logging.
