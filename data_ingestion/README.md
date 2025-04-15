# Job Posting Data Ingestion

This directory contains scripts for ingesting job posting data from the JSearch API into different databases.

## Available Scripts

- `data_ingestion.py`: Ingests job postings into Milvus/Zilliz vector database
- `data_ingestion_aws.py`: Ingests job postings into AWS DynamoDB

## Environment Setup

1. Create a `.env` file in the root directory with the following variables:

```
# JSearch API Configuration
JSEARCH_URL=https://jsearch.p.rapidapi.com/search
JSEARCH_API_KEY=your_jsearch_api_key_here

# Milvus/Zilliz Configuration (for data_ingestion.py)
ZILLZ_URI=your_zilliz_uri_here
ZILLZ_TOKEN=your_zilliz_token_here

# AWS Credentials (for data_ingestion_aws.py when running locally)
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_REGION=us-east-1
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Milvus/Zilliz Integration

To ingest job postings into Milvus/Zilliz:

```bash
python data_ingestion/data_ingestion.py
```

### AWS DynamoDB Integration

To ingest job postings into AWS DynamoDB:

```bash
python data_ingestion/data_ingestion_aws.py
```

## DynamoDB Table Structure

The DynamoDB table `job_listings` has the following structure:

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

### IAM Role Configuration

When deploying to Lambda, you need to create an IAM role with the following permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:PutItem",
                "dynamodb:GetItem",
                "dynamodb:DescribeTable",
                "dynamodb:CreateTable"
            ],
            "Resource": "arn:aws:dynamodb:*:*:table/job_listings"
        }
    ]
}
```

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