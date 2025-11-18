# Resume Matching LLM — Data Ingestion Pipeline

This repository contains a Python-based ingestion pipeline that fetches job listings from the **JSearch API**, cleans them, generates **384-dim embeddings** using **SentenceTransformers (MiniLM-L6-v2)**, and stores them in a **PostgreSQL vector database** (`pgvector`).

This script is designed to run locally and will later be deployed to **AWS Lambda** as a scheduled nightly job.

---

## Features

- Fetches job listings for multiple job categories
- Cleans and deduplicates job postings
- Generates embeddings using MiniLM-L6-v2
- Inserts new jobs into PostgreSQL using `ON CONFLICT DO NOTHING`
- Ensures no duplicate inserts across runs
- Fully modular and production ready

---

## Project Structure

```
resume-matching-llm/
│
├── data_ingestion/
│   ├── data_ingestion.py         ← main ingestion script
│   ├── job_titles.json
│   ├── README.md                 ← this file
│
├── .env
├── .gitignore
├── requirements.txt
└── venv/                         (ignored in git)
```

---

## Local Setup

### 1. Clone the repo

```bash
git clone https://github.com/your-org/resume-matching-llm.git
cd resume-matching-llm
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root:

```
# JSearch (RapidAPI)
JSEARCH_API_KEY=your_key_here
JSEARCH_URL=https://jsearch.p.rapidapi.com/search

# PostgreSQL
PG_HOST=your-db-host
PG_PORT=5432
PG_USER=postgres
PG_PASSWORD=your_password
PG_DATABASE=postgres
```

Do **not** commit `.env`.  
Add a `.env.example` if sharing config with collaborators.

---

## job_titles.json Format

`job_titles.json` must contain:

```json
{
  "job_titles": [
    "Data Engineer",
    "Machine Learning",
    "Cloud Engineer",
    "Backend Developer"
  ]
}
```

The script will fetch and ingest all job titles in the list.

---

## Running the Ingestion Script

Run from the project root:

```bash
cd data_ingestion
python data_ingestion.py
```

Successful output looks like:

```
INFO - Fetching jobs...
INFO - Cleaning dataset...
INFO - Inserting into PostgreSQL...
INFO - Inserted 143 new job listings into PostgreSQL.
INFO - Ingestion complete.
```

---

## PostgreSQL Table Schema

Make sure your database has:

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE job_listings (
    job_id                  TEXT PRIMARY KEY,
    job_description_vector  vector(384),
    job_description_raw     TEXT,
    job_title               VARCHAR(255),
    employer_name           VARCHAR(255),
    job_location            VARCHAR(255),
    degree                  VARCHAR(255),
    remote                  BOOLEAN,
    location_state          VARCHAR(255),
    employment_type         VARCHAR(255),
    citizenship             BOOLEAN,
    job_apply_link          VARCHAR(500),
    job_posted_at           BIGINT,
    job_posted_at_datetime  TIMESTAMP,
    insert_time             TIMESTAMP DEFAULT NOW()
);
```

---

## Cleaning Actions

The ingestion pipeline automatically:

- Merges city + state into a standardized `job_location`
- Removes duplicates using:
  - job_title + location + employer_name  
  - job_description text
- Flags citizenship/clearance requirements
- Infers whether a degree is required
- Standardizes employment type & remote fields
- Skips malformed or non-384-dim embeddings

---

## Roadmap (Next Steps)

- Deploy to AWS Lambda  
- Add EventBridge daily scheduler  
- Add a DB pre-check to skip existing job_ids before embedding  
- Add automatic pruning of old jobs  
- Store secrets in AWS Secrets Manager  

---

## License

MIT License — free to use, modify, and distribute.a
