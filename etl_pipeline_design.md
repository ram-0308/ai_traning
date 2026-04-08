# Production-Ready ETL Data Pipeline

## Overview
An ETL (Extract, Transform, Load) pipeline is a structured process for ingesting raw data from diverse sources, cleaning and transforming it to a consistent format, and loading it into a target system for analytics or machine learning. This document outlines a 3-stage pipeline design with practical implementation details, error handling, and data quality controls.

---

## Stage 1: EXTRACT

### Purpose
Ingest raw data from source systems (APIs, databases, files, data lakes) into a staging area while maintaining data integrity and audit trails.

### Sub-Steps

1. **Source Identification**
   - Define all data sources (APIs, databases, flat files, streaming)
   - Document source schema, update frequency, and access patterns
   - Classify by volatility (static, daily, real-time)

2. **Connection Setup**
   - Establish secure connections with credentials stored in vaults (AWS Secrets Manager, HashiCorp Vault)
   - Use connection pooling for database sources
   - Implement retry logic and circuit breakers for API calls

3. **Data Extraction**
   - Full load: First-time pull of entire dataset
   - Incremental load: Pull only new/modified records (using timestamps, change data capture, or watermarks)
   - Batch extraction: Schedule at off-peak hours to minimize source system load
   - Streaming extraction: Real-time ingestion for high-velocity data

4. **Data Staging**
   - Write raw data to staging zone (cloud storage: S3, GCS, or local data lake)
   - Maintain original format without modification
   - Generate extraction metadata (timestamp, record count, hash for integrity)

### Tools & Technologies
- **Extraction Tools**: Apache Airflow, Talend, Informatica, Apache NiFi
- **Data Sources**: REST APIs (requests, aiohttp), SQL databases (SQLAlchemy, psycopg2), CSV/JSON files, Kafka, Google Cloud Pub/Sub
- **Staging Storage**: AWS S3, Google Cloud Storage, Azure Data Lake, HDFS
- **Metadata Tracking**: Airflow DAGs, dbt manifest files, data catalog (Apache Atlas, Collibra)

### Example: Extract Customer Data

```python
import requests
import pandas as pd
from datetime import datetime
import logging

def extract_customer_api(source_url, batch_size=1000):
    """Extract customer data from REST API with pagination"""
    all_records = []
    page = 1
    extraction_start = datetime.now()
    
    try:
        while True:
            # API call with retry logic
            response = requests.get(
                f"{source_url}/customers?page={page}&limit={batch_size}",
                headers={"Authorization": "Bearer token"},
                timeout=30
            )
            response.raise_for_status()
            
            records = response.json()['data']
            if not records:
                break  # No more pages
            
            all_records.extend(records)
            page += 1
        
        # Save to staging
        df = pd.DataFrame(all_records)
        staging_path = f"s3://data-lake/staging/customers/{extraction_start.isoformat()}.parquet"
        df.to_parquet(staging_path)
        
        # Log extraction metadata
        logging.info(f"Extracted {len(all_records)} records to {staging_path}")
        return {
            "record_count": len(all_records),
            "timestamp": extraction_start,
            "path": staging_path,
            "status": "success"
        }
    
    except Exception as e:
        logging.error(f"Extraction failed: {e}")
        raise
```

### Error Handling & Data Quality Checks

| Issue | Check | Action |
|-------|-------|--------|
| API timeouts | Retry mechanism (exponential backoff) | Retry up to 3 times, then alert |
| Incomplete data | Record count validation | Compare to expected row count ±5% |
| Corrupted files | File hash/checksum validation | Flag and quarantine suspicious files |
| Missing fields | Schema validation | Reject batch if required fields are null |
| Duplicate extracts | Deduplication flag | Skip if data already in current batch |

---

## Stage 2: TRANSFORM

### Purpose
Standardize, clean, and enrich raw data into a consistent, validated format suitable for analytics and ML models.

### Sub-Steps

1. **Schema Validation**
   - Verify incoming data conforms to expected schema (column names, data types)
   - Use schema enforcement tools (Great Expectations, dbt tests)
   - Log and quarantine records with schema violations

2. **Data Cleaning**
   - **Missing Values**: Drop rows with critical nulls, forward-fill for time series, mean/median imputation for numerical fields
   - **Duplicates**: Remove exact duplicates using all columns; handle near-duplicates with fuzzy matching (Levenshtein distance)
   - **Outliers**: Detect using IQR, Z-score, or isolation forests; flag or cap extreme values
   - **Inconsistencies**: Standardize case (uppercase/lowercase), trim whitespace, normalize units

3. **Type Conversion & Normalization**
   - Cast columns to correct data types (string → datetime, int → float)
   - Normalize numerical fields (min-max scaling for ML, log transformation for skewed data)
   - Standardize categorical values (map inconsistent labels to canonical values)
   - Encode categorical variables for ML (one-hot, ordinal encoding)

4. **Enrichment & Feature Engineering**
   - Join with reference tables (e.g., customer demographics, product catalogs)
   - Create derived fields (e.g., age from birthdate, revenue per user)
   - Add metadata columns (data source, extraction timestamp, record version)

5. **Data Validation**
   - Check business rule compliance (e.g., order quantity > 0, email format valid)
   - Perform referential integrity checks (foreign key validation)
   - Generate data quality metrics (completeness, accuracy, consistency scores)

### Tools & Technologies
- **Transformation Frameworks**: Apache Spark, Pandas, Dask (distributed pandas), PySpark
- **Orchestration**: Apache Airflow, Dagster, Prefect
- **Data Quality**: Great Expectations, dbt tests, custom Spark SQL validators
- **Languages**: Python, SQL, PySpark SQL

### Example: Transform Customer & Order Data

```python
import pandas as pd
import numpy as np
from datetime import datetime
import warnings

def transform_customer_orders(df_customers, df_orders):
    """
    Clean and enrich customer and order data.
    Handles missing values, deduplication, and joins.
    """
    
    # Step 1: Validate schema
    required_cols = ['customer_id', 'email', 'signup_date']
    if not all(col in df_customers.columns for col in required_cols):
        raise ValueError(f"Missing required columns: {required_cols}")
    
    # Step 2: Clean customer data
    df_customers['email'] = df_customers['email'].str.lower().str.strip()
    df_customers['email'] = df_customers['email'][df_customers['email'].str.contains('@')]  # Valid emails
    df_customers.drop_duplicates(subset=['customer_id'], keep='first', inplace=True)
    
    # Handle missing signup_date
    df_customers['signup_date'] = pd.to_datetime(
        df_customers['signup_date'], 
        errors='coerce'
    )
    df_customers['signup_date'].fillna(df_customers['signup_date'].min(), inplace=True)
    
    # Step 3: Clean order data
    df_orders['order_amount'] = pd.to_numeric(df_orders['order_amount'], errors='coerce')
    df_orders = df_orders[df_orders['order_amount'] > 0]  # Valid amounts only
    
    # Detect and cap outliers (IQR method)
    Q1 = df_orders['order_amount'].quantile(0.25)
    Q3 = df_orders['order_amount'].quantile(0.75)
    IQR = Q3 - Q1
    upper_bound = Q3 + 1.5 * IQR
    df_orders['order_amount'] = df_orders['order_amount'].clip(upper=upper_bound)
    
    # Step 4: Enrich with customer data
    df_merged = df_orders.merge(
        df_customers[['customer_id', 'email', 'signup_date']],
        on='customer_id',
        how='left'
    )
    
    # Feature engineering
    df_merged['days_since_signup'] = (
        pd.to_datetime(df_merged['order_date']) - df_merged['signup_date']
    ).dt.days
    
    # Step 5: Data quality checks
    quality_metrics = {
        "total_records": len(df_merged),
        "null_count": df_merged.isnull().sum().sum(),
        "duplicate_orders": df_merged.duplicated(subset=['order_id']).sum(),
        "valid_emails": df_merged['email'].notna().sum(),
        "completeness": (1 - df_merged.isnull().sum().sum() / df_merged.size) * 100
    }
    
    print(f"Data Quality Metrics: {quality_metrics}")
    
    # Validation assertions
    assert df_merged['order_amount'].min() > 0, "Negative order amounts found"
    assert df_merged['completeness'] > 95, "Data completeness below 95%"
    
    return df_merged, quality_metrics
```

### Error Handling & Data Quality Checks

| Issue | Technique | Threshold |
|-------|-----------|-----------|
| Missing values | Log and impute | Allow ≤5% nulls per column |
| Duplicates | Deduplication with exact/fuzzy matching | Remove all exact duplicates |
| Outliers | IQR/Z-score detection | Flag values beyond 1.5×IQR |
| Invalid data types | Type casting with error coercion | Log and quarantine non-convertible rows |
| Business rule violations | Custom SQL/Python validators | Reject rows breaking domain rules |
| Data drift | Statistical tests (Kolmogorov-Smirnov) | Alert if distribution changes >10% |

---

## Stage 3: LOAD

### Purpose
Write cleaned, validated data to target systems (data warehouse, data lake, ML feature store) in an optimized format for downstream consumption.

### Sub-Steps

1. **Target Preparation**
   - Create or update target schema (staging tables, production tables, fact/dimension tables)
   - Set up partitioning strategy (by date, region, customer segment) for scalability
   - Configure compression and indexing for query performance

2. **Data Writing**
   - **Full Load**: Replace entire target table (used for fact tables, reference data)
   - **Incremental Load**: Insert new records or update existing ones (UPSERT) using merge logic
   - **Append**: Add new rows without deleting existing data (used for audit logs, event streams)
   - Choose format based on use case (Parquet for analytics, CSV for BI tools, Delta/Iceberg for ACID compliance)

3. **Transaction Management**
   - Implement atomic writes (all-or-nothing) to prevent partial loads
   - Use staging tables to validate before committing to production
   - Implement rollback mechanisms on failure

4. **Metadata & Audit Logging**
   - Record load timestamp, row counts (inserted/updated/deleted), data quality scores
   - Maintain lineage (source → transform → target) for data governance
   - Store schema versions for backward compatibility

5. **Notification & Monitoring**
   - Alert data consumers that new data is ready
   - Monitor pipeline execution time and resource usage
   - Track SLAs (Service Level Agreements) for data freshness

### Tools & Technologies
- **Data Warehouses**: Snowflake, BigQuery, Redshift, Azure Synapse
- **Data Lakes**: Delta Lake, Apache Iceberg, Apache Hudi (ACID transactions)
- **File Formats**: Parquet (columnar, compressed), ORC, CSV, JSON
- **Loading Tools**: dbt, Spark SQL, cloud-native connectors (Fivetran, Stitch)
- **Orchestration**: Airflow, dbt, Dagster
- **Monitoring**: dbt artifacts, custom logging, Datadog, CloudWatch

### Example: Load to Snowflake

```sql
-- Step 1: Create staging table
CREATE TEMP TABLE stg_customer_orders_new AS
SELECT * FROM transformed_data;

-- Step 2: Incremental load with UPSERT logic
MERGE INTO prod.customer_orders AS target
USING stg_customer_orders_new AS source
  ON target.order_id = source.order_id
WHEN MATCHED AND target.updated_at < source.updated_at THEN
  UPDATE SET 
    customer_id = source.customer_id,
    order_amount = source.order_amount,
    order_date = source.order_date,
    updated_at = CURRENT_TIMESTAMP
WHEN NOT MATCHED THEN
  INSERT (order_id, customer_id, order_amount, order_date, created_at, updated_at)
  VALUES (
    source.order_id,
    source.customer_id,
    source.order_amount,
    source.order_date,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
  );

-- Step 3: Validate load
SELECT 
  COUNT(*) as total_records,
  COUNT(DISTINCT customer_id) as unique_customers,
  SUM(order_amount) as total_revenue,
  MAX(updated_at) as last_updated
FROM prod.customer_orders;

-- Step 4: Log metadata
INSERT INTO audit.load_logs (
  table_name, 
  load_timestamp, 
  rows_inserted, 
  rows_updated, 
  status
)
VALUES (
  'customer_orders',
  CURRENT_TIMESTAMP,
  (SELECT COUNT(*) FROM stg_customer_orders_new WHERE NOT EXISTS 
    (SELECT 1 FROM prod.customer_orders WHERE order_id = stg_customer_orders_new.order_id)),
  (SELECT COUNT(*) FROM stg_customer_orders_new WHERE EXISTS 
    (SELECT 1 FROM prod.customer_orders WHERE order_id = stg_customer_orders_new.order_id)),
  'success'
);
```

### Python Example with Spark

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp

def load_to_warehouse(df_transformed):
    """Load transformed data to cloud data warehouse with ACID guarantees"""
    
    spark = SparkSession.builder \
        .appName("ETL-Load") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .getOrCreate()
    
    # Add metadata columns
    df_with_metadata = df_transformed.withColumn(
        "load_timestamp", current_timestamp()
    ).withColumn(
        "data_quality_score", 
        col("completeness") * 0.4 + col("accuracy") * 0.6
    )
    
    # Write to Delta Lake (ACID transactions)
    df_with_metadata.write \
        .format("delta") \
        .mode("overwrite") \
        .option("mergeSchema", "true") \
        .partitionBy("load_date") \
        .save("s3://data-warehouse/prod/customer_orders")
    
    # Create or replace table
    spark.sql("""
        CREATE TABLE IF NOT EXISTS prod.customer_orders
        USING DELTA
        LOCATION 's3://data-warehouse/prod/customer_orders'
    """)
    
    # Validate load
    result = spark.sql("""
        SELECT 
            COUNT(*) as total_records,
            COUNT(DISTINCT customer_id) as unique_customers,
            ROUND(AVG(data_quality_score), 2) as avg_quality
        FROM prod.customer_orders
    """)
    
    result.show()
    return result
```

### Error Handling & Data Quality Checks

| Issue | Check | Action |
|-------|-------|--------|
| Load timeouts | Timeout monitoring | Retry with smaller batches, escalate after 3 attempts |
| Schema mismatch | Schema validation before write | Fail fast with clear error message |
| Duplicate keys | Primary key constraint check | Reject batch if duplicates exist |
| Referential integrity | Foreign key validation | Warn if orphaned records detected |
| Transaction failure | Rollback mechanism | Revert to last known good state |
| Data inconsistency | Row count validation | Alert if insert count differs from expected |

---

## End-to-End Pipeline Flow

```
Raw Data Sources
    ↓
[EXTRACT] → Staging Zone
    ↓ (Validation: Schema, Completeness)
[TRANSFORM] → Transformation Layer
    ↓ (Validation: Data Quality, Business Rules)
[LOAD] → Target System (Data Warehouse/Lake)
    ↓
Analytics, ML Models, BI Dashboards
```

---

## Production Considerations

### Scheduling & Orchestration
- Use Airflow DAGs or dbt workflows to run pipeline on schedule (daily, hourly, real-time)
- Implement task dependencies to prevent downstream failures
- Set up alerts for pipeline failures

### Scalability
- Use partitioning and indexing for large datasets (>1TB)
- Implement parallel processing (Spark, Dask) for multi-core/distributed execution
- Consider streaming architecture (Kafka + Spark Streaming) for real-time pipelines

### Compliance & Governance
- Maintain data lineage for audit trails
- Implement row-level security (RLS) and column-level encryption for sensitive data
- Document data dictionary with business definitions
- Track data quality metrics in centralized catalog (Apache Atlas, Collibra)

### Monitoring & Alerting
- Set up dashboards for pipeline execution time, success rates, and data freshness
- Alert on anomalies (delayed loads, quality score drops, row count deviations)
- Maintain SLA targets (expected load time, data availability, accuracy)

