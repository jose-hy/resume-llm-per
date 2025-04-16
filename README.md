# Resume Matching LLM (Backend)

There are three parts of the backend, API, Vector DB, and Data Ingestion Pipeline.

See VectorDB and Ingestion Pipeline at [HERE](https://github.com/de-data-lab/resume-matching-llm/tree/1-jsearch-dataingestion/data_ingestion#job-posting-data-ingestion) 

## Backend API

The backend API is built with FastAPI and provides endpoints for resume matching, job search, and resume analysis. The API is available at `/api/v1/`.

### Quick Start
```bash
pip install -r requirements.txt
fastapi dev app/main.py
```

### API Documentation

Once the server is running, you can access:
- Swagger UI documentation at `/api/v1/docs`
- ReDoc documentation at `/api/v1/redoc`
- OpenAPI schema at `/api/v1/openapi.json`

### Available Endpoints

#### Job Search
- `POST /api/v1/search_jobs`
  - Upload a resume (PDF) and search for matching jobs
  - Supports filtering by degree requirements, location, remote work, and employment type
  - Returns ranked job matches based on resume content

#### Resume Analysis
- `POST /api/v1/analyze/disqualification`
  - Analyze why a resume might be disqualified for a specific job
  - Requires job description and resume (PDF)

- `POST /api/v1/analyze/improvement`
  - Get suggestions for improving a resume for a specific job
  - Requires job description and resume (PDF)

#### Cover Letter Generation
- `POST /api/v1/generate/cover-letter`
  - Generate a cover letter based on the resume and job description
  - Requires job description and resume (PDF)

#### Latest Jobs
- `GET /api/v1/latest_jobs`
  - Get the most recent job listings
  - Optional `limit` parameter to control number of results (default: 10)

### Setup Requirements

1. Environment Variables:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   COHERE_API_KEY=your_cohere_api_key
   ZILLZ_URI=your_zilliz_uri
   ZILLZ_TOKEN=your_zilliz_token
   ```

2. Python Dependencies:
   - Python 3.11
   - FastAPI
   - PyPDF2
   - Google Generative AI
   - Sentence Transformers
   - Cohere
   - PyMilvus

## Deployment Instructions

### Local Docker Deployment

1. Build the Docker image:
```bash
docker build -t <repo_name>/jobmatchapi:latest .
```

2. Push the image to Docker Hub:
```bash
docker push <repo_name>/jobmatchapi:latest
```

Note: Replace `<repo_name>` with your Docker Hub repository name.

### Running the Container Locally

To run the container:
```bash
docker run -p 80:80 <repo_name>/jobmatchapi:latest
```

The API will be available at `http://localhost:80`

### AWS Deployment

#### 1. Build Container with AWS ECR

1. Install and configure AWS CLI:
```bash
# Install AWS CLI
brew install awscli  # For macOS
# or
pip install awscli   # Using pip

# Configure AWS credentials
aws configure
```

2. Create an ECR repository (if not exists):
```bash
aws ecr create-repository --repository-name jobmatchapi
```

3. Authenticate Docker to ECR:
```bash
aws ecr get-login-password --region <your-region> | docker login --username AWS --password-stdin <your-account-id>.dkr.ecr.<your-region>.amazonaws.com
```

4. Build and tag the image for ECR:
```bash
docker build -t jobmatchapi .
docker tag jobmatchapi:latest <your-account-id>.dkr.ecr.<your-region>.amazonaws.com/jobmatchapi:latest
```

5. Push the image to ECR:
```bash
docker push <your-account-id>.dkr.ecr.<your-region>.amazonaws.com/jobmatchapi:latest
```

#### 2. Deploy on AWS ECS

1. Create a task definition file (`task-definition.json`):
```json
{
    "family": "jobmatchapi",
    "networkMode": "awsvpc",
    "requiresCompatibilities": ["FARGATE"],
    "cpu": "256",
    "memory": "512",
    "executionRoleArn": "arn:aws:iam::your-account-id:role/ecsTaskExecutionRole",
    "containerDefinitions": [
        {
            "name": "jobmatchapi",
            "image": "your-account-id.dkr.ecr.your-region.amazonaws.com/jobmatchapi:latest",
            "portMappings": [
                {
                    "containerPort": 80,
                    "protocol": "tcp"
                }
            ],
            "environment": [
                {
                    "name": "GEMINI_API_KEY",
                    "value": "your_gemini_api_key"
                },
                {
                    "name": "COHERE_API_KEY",
                    "value": "your_cohere_api_key"
                },
                {
                    "name": "ZILLZ_URI",
                    "value": "your_zilliz_uri"
                },
                {
                    "name": "ZILLZ_TOKEN",
                    "value": "your_zilliz_token"
                }
            ],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "/ecs/jobmatchapi",
                    "awslogs-region": "your-region",
                    "awslogs-stream-prefix": "ecs"
                }
            }
        }
    ]
}
```

2. Create an ECS cluster and deploy the task:
```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name jobmatchapi-cluster --region your-region

# Register task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json --region your-region
```

Then create a service with the task definiation and wait for few minutes for deployment.

The API will be available at the task's public IP address on port 80. IP can be found at: ECS --> Clusters --> jobmatchapi-cluster --> Tasks --> Networking --> Public IP.


#### 3. customize url with our own domain

