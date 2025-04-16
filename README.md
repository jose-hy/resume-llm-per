# Resume Matching LLM (Backend)

There are three parts of the backend, API, Vector DB, and Data Ingestion Pipeline.
See VectorDB and Ingestion Pipeline at [HERE](https://github.com/de-data-lab/resume-matching-llm/tree/1-jsearch-dataingestion/data_ingestion#job-posting-data-ingestion) 

## Backend API


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

The API will be available at `http://localhost:80`
