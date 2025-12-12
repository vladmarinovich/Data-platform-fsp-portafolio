# Salvando Patitas Data Platform

A serverless ELT pipeline designed to ingest, transform, and analyze operational data for the *Salvando Patitas* foundation. The system integrates Supabase (PostgreSQL) sources into a Google Cloud Platform ecosystem, utilizing **Cloud Run Jobs** for orchestrated extraction and **BigQuery + Dataform** for data warehousing and transformations.

## Problem Statement

The foundation faced challenges with operational data fragmentation across its custom CRM application. Accessing historical insights required manual data dumps, leading to inconsistencies and stale reporting. 

This platform addresses these issues by:
*   **Centralizing Data**: Unifying donation, expense, and case management records into a single analytical source of truth.
*   **Ensuring Consistency**: Implementing robust incremental loading strategies to capture all data changes without redundant processing.
*   **Operational Reliability**: automating the pipeline to run daily with minimal maintenance overhead, ensuring traceability and error handling.

## Architecture

The architecture follows a modular ELT pattern, leveraging serverless components to minimize operational costs while maximizing scalability.

```
[Supabase (PostgreSQL)] 
       |
       | (Python ETL Container / Cloud Run Jobs)
       v
[Google Cloud Storage] <--- (State Management / watermarks.json)
(Zone: Raw / Parquet)
       |
       | (External Tables)
       v
[BigQuery: Raw Layer]
       |
       | (Dataform Execution)
       v
[BigQuery: Silver Layer] ---> [Looker Studio Dashboard]
```

### Core Components
1.  **Extraction (Python)**: A containerized Python application extracts data from Supabase.
    *   **Incremental Tables**: Fetches only records modified since the last execution watermark (persisted in GCS).
    *   **Snapshot Tables**: Performs full reloads for small dimension tables to ensure referential integrity.
    *   **Ingestion**: Data is written to GCS in partitioned Parquet format for optimal query performance.
2.  **Storage (GCS & BigQuery)**: Google Cloud Storage acts as the Data Lake. BigQuery mounts these files as External Tables (Raw Layer).
3.  **Transformation (Dataform)**: SQLX pipelines transform Raw data into the Silver layer, applying cleaning, casting, and business logic.
4.  **Orchestration**: Cloud Scheduler triggers the Cloud Run Job daily.

## Production Execution

The pipeline is deployed as a Docker container on **Google Cloud Run Jobs**.

*   **Trigger**: Cloud Scheduler initiates the job daily at **07:00 AM (America/Santiago)**.
*   **Job Execution**:
    1.  The container starts and loads configuration from environment variables.
    2.  It retrieves the current state (`watermarks.json`) from GCS.
    3.  It performs incremental extraction for high-volume tables (`donaciones`, `gastos`, `casos`) and snapshot extraction for catalogs.
    4.  Upon successful upload to GCS, it updates the watermark state.
    5.  (Connected Integration) Dataform executes downstream transformations.
*   **Monitoring**: Execution logs, data volume metrics, and error traces are captured in Cloud Logging.

## Visualization and Documentation

*   **[Looker Studio Dashboard](https://lookerstudio.google.com/u/0/reporting/cb2392ff-d151-4b16-9bc3-49df863ced2c/page/p_97ri4w4xyd)**
    *   Displays the final output of the pipeline. Evaluators can verify data freshness, aggregations, and the practical application of the Gold/Silver data layers.

*   **[Architecture & Systems Diagram (Miro)](https://miro.com/welcomeonboard/UkduTDRzZFZlSW9xek1EL2dwRG1XVG8rQmRvcVFWbGhRMEhjVHBmUnU5MSs0ek5LdlZxSHcyOE15UXNydlNkOHQ1N3ROTEdEd2dQOVhEcDN4MlF6S0d0WEJySWE5c2xhNGNnVHB1WXRGNGl2OWJZNlhydU00bWVoOFRZK095bkNhWWluRVAxeXRuUUgwWDl3Mk1qRGVRPT0hdjE=?share_link_id=538214555000)**
    *   Detailed visual representation of the system components, data flow, and interactions between the CRM, the ETL pipeline, and the visualization layer.

## Key Technical Decisions

*   **Cloud Run Jobs for ETL**: Selected for its serverless nature. Start-up time is fast, and billing is per-second. Unlike Cloud Functions, it handles longer validation timeouts and memory-intensive batch processing gracefully. Unlike Dataproc, it requires zero cluster management.
*   **BigQuery**: Chosen for its separation of storage and compute. It allows querying raw Parquet files directly from GCS without loading costs, and scales effortlessly for analytical queries.
*   **Dataform**: Provides software engineering best practices to SQL transformation (CI/CD, version control, dependency management, and assertion testing), superior to managing raw SQL scripts scheduled via cron.
*   **Incremental Loading with Persistent State**: Essential for scaling. Instead of reloading the entire dataset daily, the system tracks the `last_modified_at` timestamp. This reduces Supabase egress costs and processing time from minutes to seconds for daily deltas.

## Platform Status

*   **Implemented**:
    *   ✅ Full extraction pipeline (Python/Docker).
    *   ✅ Storage layer (GCS Parquet + BigQuery Raw).
    *   ✅ Transformation logic (Dataform Silver Layer).
    *   ✅ Orchestration (Cloud Run + Scheduler).
    *   ✅ Visualization (Basic Dashboard).

*   **Pending**:
    *   🚧 Gold Layer modeling (Star Schema).
    *   🚧 Advanced Data Quality Assertions (Gold Level).
    *   🚧 ML Integration.

## Next Steps (Roadmap)

*   **Gold Layer Implementation**: Develop final dimensional models optimized for BI tools.
*   **Strict Assertions**: Implement row-count and distribution tests to block bad data before it reaches the Gold layer.
*   **Vertex AI Integration**: Deploy ML models to predict donation trends based on historical data.
*   **Agentic Interface**: Implement an LLM-based agent to allow natural language querying of the dataset.
*   **API Exposure**: Create a lightweight API layer to serve processed metrics back to the operational CRM.
