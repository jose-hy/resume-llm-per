# Job Posting Data Ingestion

This directory contains scripts for ingesting job posting data from the JSearch API into Milvus Vector DB hosted on (Zilliz)[https://cloud.zilliz.com/orgs/org-zocumtftvqemtejqpopiek/projects/proj-1a3103822ea4307031154a/clusters/in03-3acf9d8039d538c/collections/job_listings1].

## Scripts

- `data_ingestion.py`: Ingests job postings into Milvus/Zilliz vector database
- `job_titles.json`: Job titles for searching jobs and indexing to Vector DB

## Environment Setup (if running locally)

1. Create a `.env` file in the root directory with the following variables:

```
# JSearch API Configuration
JSEARCH_URL=https://jsearch.p.rapidapi.com/search
JSEARCH_API_KEY=your_jsearch_api_key_here

# Milvus/Zilliz Configuration (for data_ingestion.py)
ZILLZ_URI=your_zilliz_uri_here
ZILLZ_TOKEN=your_zilliz_token_here
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Usage

### Milvus/Zilliz Integration

To ingest job postings into Milvus/Zilliz:

```bash
python data_ingestion/data_ingestion.py
```


## Data Table Structure

The table `job_listings` has the following structure:

- **Primary Key**: `job_id` (String)
- **Attributes**:
  - `job_description_vector`: List of numbers (embedding vector)
  - `job_description_raw`: String (raw job description)
  - `job_title`: String
  - `employer_name`: String
  - `job_location`: String
  - `degree`: String (required, no_degree, unknown)
  - `remote`: Boolean
  - `location_state`: String
  - `employment_type`: String
  - `citizenship`: Boolean
  - `job_apply_link`: String
  - `job_posted_at`: Number (timestamp in milliseconds)
  - `job_posted_at_datetime`: String (ISO format)
  - `insert_time`: String (ISO format)

## AWS Lambda Deployment

Both scripts can be deployed as AWS Lambda functions. The `lambda_handler` function in each script is designed to be triggered by AWS Lambda.

### Lambda Configuration

1. **Memory**: Set to at least 1024 MB (1 GB) for optimal performance
2. **Timeout**: Set to at least 5 minutes (300 seconds) as the script may take time to process all jobs
3. **Environment Variables**: Configure the following environment variables in Lambda:
   - `JSEARCH_URL`
   - `JSEARCH_API_KEY`
   - `ZILLZ_TOKEN`
   - `ZILLZ_URI`

### Lambda vs. Local Execution

The script automatically detects whether it's running in Lambda or locally:
- In Lambda: Uses IAM role for authentication
- Locally: Uses AWS credentials from .env file

## Notes

- The scripts process job postings in chunks to minimize memory usage
- Embeddings are generated using the SentenceTransformer model 'all-MiniLM-L6-v2'
- Job descriptions are truncated to 10,000 characters if they exceed this length
- The scripts include error handling and logging for robust operation
- When running in Lambda, the script uses the /tmp directory for temporary storage 