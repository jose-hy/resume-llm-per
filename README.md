# Resume Matching LLM (Backend)

There are three parts of the backend, API, Vector DB, and Data Ingestion Pipeline.

See VectorDB and Ingestion Pipeline at [HERE](https://github.com/de-data-lab/resume-matching-llm/tree/1-jsearch-dataingestion/data_ingestion#job-posting-data-ingestion) 

## Backend API

The backend API is built with FastAPI and provides endpoints for resume matching, job search, and resume analysis. The API is available at `/api/v1/`.

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

### Building and Pushing Docker Image

1. Build the Docker image:
```bash
docker build -t <repo_name>/jobmatchapi:latest .
```

2. Push the image to Docker Hub:
```bash
docker push <repo_name>/jobmatchapi:latest
```

Note: Replace `<repo_name>` with your Docker Hub repository name.

### Running the Container

To run the container:
```bash
docker run -p 80:80 <repo_name>/jobmatchapi:latest
```
