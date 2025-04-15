# resume-matching-llm
# Mainly read 3 python files (1.vector_db_1204; 2.parse_resume; 3.app_v2_1204)

Frontend: https://github.com/de-data-lab/resume-matching-frontend

Analytics server: https://github.com/de-data-lab/resume-matching-server

# Resume Matching LLM

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
