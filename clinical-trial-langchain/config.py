# Clinical Trial LangChain Configuration

## Application Settings
APP_NAME = "Clinical Trial LangChain"
VERSION = "0.1.0-beta"
ENVIRONMENT = "development"  # development, staging, production

## LLM Configuration
LLM_MODEL = "gpt-4o-mini"
LLM_TEMPERATURE = 0.1  # Low randomness for clinical consistency
LLM_MAX_TOKENS = 1024

## Embeddings Configuration
EMBEDDINGS_MODEL = "text-embedding-3-small"
EMBEDDINGS_DIMENSION = 1536

## Vector Store Configuration
VECTOR_STORE_TYPE = "FAISS"  # FAISS (local) or Pinecone (cloud)
VECTOR_STORE_PATH = "./vector_store"

## Database Configuration
DATABASE_TYPE = "SQLite"  # SQLite (dev) or PostgreSQL (prod)
DATABASE_PATH = "./clinical_trial.db"
AUDIT_LOG_PATH = "./audit_log.db"

## HIPAA Compliance Settings
ENABLE_PII_MASKING = True
ENABLE_ENCRYPTION = True
DATA_RETENTION_DAYS = 90
AUDIT_LOG_RETENTION_DAYS = 365

## Feature Flags
ENABLE_PATIENT_MATCHING = True
ENABLE_PROTOCOL_PARSING = True
ENABLE_ADVERSE_EVENT_ANALYSIS = True
ENABLE_REGULATORY_CHECKS = True

## Timeout Settings (seconds)
LLM_TIMEOUT = 30
DOCUMENT_PROCESSING_TIMEOUT = 60
BATCH_PROCESSING_TIMEOUT = 120

## Logging
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "./logs/app.log"
AUDIT_LOG_FILE = "./logs/audit.log"
