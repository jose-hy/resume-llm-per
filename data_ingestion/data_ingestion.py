import os
import json
import re
import time
import random
import logging
from pathlib import Path
from datetime import datetime

import pandas as pd
import requests
import psycopg2
from psycopg2.extras import execute_batch
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Paths
BASE_DIR = Path(__file__).resolve().parent
TITLES_PATH = BASE_DIR / "job_titles.json"

# JSearch API config
JSEARCH_API_KEY = os.getenv("JSEARCH_API_KEY")
JSEARCH_URL = os.getenv("JSEARCH_URL")

# PostgreSQL config
PG_HOST = os.getenv("PG_HOST")
PG_PORT = os.getenv("PG_PORT", "5432")
PG_DATABASE = os.getenv("PG_DATABASE")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")


def load_job_titles():
    if not TITLES_PATH.exists():
        raise FileNotFoundError(f"Missing job_titles.json at: {TITLES_PATH}")

    with open(TITLES_PATH, "r") as f:
        data = json.load(f)

    if "job_titles" not in data:
        raise ValueError("job_titles.json missing 'job_titles' key.")

    return data["job_titles"]


def fetch_jobs_from_api(job_title):
    params = {
        "query": job_title,
        "page": "1",
        "num_pages": "3",
        "date_posted": "3days",
        "employment_types": "FULLTIME, CONTRACTOR, PARTTIME, INTERN",
        "job_requirements": "under_3_years_experience, no_experience, no_degree",
        "exclude_job_publishers": "Dice, jooble, Clearance Jobs, Geebo, Talent.com"
    }

    headers = {
        "X-RapidAPI-Key": JSEARCH_API_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }

    max_attempts = 1
    for attempt in range(max_attempts):
        response = requests.get(JSEARCH_URL, headers=headers, params=params)

        if response.status_code == 429:
            wait = 2 ** attempt + random.random()
            logger.warning(f"Rate limited for '{job_title}'. Retrying in {wait:.2f}s...")
            time.sleep(wait)
            continue

        try:
            response.raise_for_status()
        except Exception:
            logger.error(f"Error fetching '{job_title}': {response.text}")
            return []

        return response.json().get("data", [])

    logger.error(f"Failed after {max_attempts} attempts fetching '{job_title}'.")
    return []


def fetch_all_jobs(job_titles):
    frames = []

    for title in job_titles:
        logger.info(f"Fetching jobs for: {title}")
        time.sleep(1.5)
        rows = fetch_jobs_from_api(title)

        if rows:
            df = pd.DataFrame(rows)
            df["query_keywords"] = title
            frames.append(df)

    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def clean_job_postings(df):

    def safe(col):
        return df[col] if col in df.columns else ""

    df["job_location"] = safe("job_city").fillna("") + ", " + safe("job_state").fillna("")
    df["job_location"] = df["job_location"].str.strip(", ")

    df["info"] = (
        safe("job_title").fillna("") + "|" +
        df["job_location"].fillna("") + "|" +
        safe("employer_name").fillna("")
    )

    df = df.drop_duplicates(subset="info")
    df = df.drop_duplicates(subset="job_description")

    df["citizenship"] = safe("job_description").str.contains(
        r"clearance|SCI|U\.S\. citizenship|US citizenship|US Citizen",
        case=False, na=False
    )

    def classify_degree(txt):
        if pd.isna(txt):
            return "No degree required"
        if re.search(r"(PhD|Master|Bachelor|MBA|BA|BS|university degree|college degree)", txt, re.IGNORECASE):
            return "Degree required (Bachelor degree or above)"
        return "No degree required"

    df["degree"] = safe("job_description").apply(classify_degree)

    df["remote"] = safe("job_is_remote").astype(str).str.lower() == "true"

    df["employment_type"] = safe("job_employment_type").fillna("")

    return df


def pg_connect():
    return psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        database=PG_DATABASE,
        user=PG_USER,
        password=PG_PASSWORD
    )

def insert_into_postgres(df, embedder):
    conn = pg_connect()
    cur = conn.cursor()

    sql = """
    INSERT INTO job_listings (
        job_id, job_description_vector, job_description_raw,
        job_title, employer_name, job_location, degree, remote,
        location_state, employment_type, citizenship, job_apply_link,
        job_posted_at, job_posted_at_datetime
    )
    VALUES (
        %(job_id)s, %(vector)s, %(job_description_raw)s,
        %(job_title)s, %(employer_name)s, %(job_location)s, %(degree)s, %(remote)s,
        %(location_state)s, %(employment_type)s, %(citizenship)s, %(job_apply_link)s,
        %(job_posted_at)s, %(job_posted_at_datetime)s
    )
    ON CONFLICT (job_id) DO NOTHING;
    """

    rows_to_insert = []
    inserted_count = 0

    for _, row in df.iterrows():
        text = (row.get("job_description", "") or "")[:10000]

        # Disable progress bars from SentenceTransformer
        vector = embedder.encode(text, show_progress_bar=False).tolist()

        if len(vector) != 384:
            continue

        try:
            dt = datetime.fromisoformat(row["job_posted_at_datetime_utc"].replace("Z", "+00:00"))
            ts = int(dt.timestamp() * 1000)
        except:
            dt = datetime.utcnow()
            ts = int(dt.timestamp() * 1000)

        rows_to_insert.append({
            "job_id": row.get("job_id"),
            "vector": vector,
            "job_description_raw": text,
            "job_title": row.get("job_title", ""),
            "employer_name": row.get("employer_name", ""),
            "job_location": row.get("job_location", ""),
            "degree": row.get("degree", ""),
            "remote": bool(row.get("remote", False)),
            "location_state": row.get("job_state", None),
            "employment_type": row.get("employment_type", ""),
            "citizenship": bool(row.get("citizenship", False)),
            "job_apply_link": row.get("job_apply_link", "")[:500],
            "job_posted_at": ts,
            "job_posted_at_datetime": dt
        })

    if rows_to_insert:
        execute_batch(cur, sql, rows_to_insert, page_size=75)
        inserted_count = cur.rowcount

    conn.commit()
    conn.close()

    logger.info(f"Inserted {inserted_count} new job listings into PostgreSQL.")


def run_ingestion():
    logger.info("Loading job titles...")
    job_titles = load_job_titles()

    logger.info(f"Processing {len(job_titles)} job titles from job_titles.json.")

    logger.info("Fetching job postings from API...")
    df = fetch_all_jobs(job_titles)

    if df.empty:
        logger.warning("No job data returned.")
        return

    logger.info("Cleaning dataset...")
    df = clean_job_postings(df)

    logger.info("Loading embedding model...")
    embedder = SentenceTransformer("all-MiniLM-L6-v2")

    logger.info("Inserting into PostgreSQL...")
    insert_into_postgres(df, embedder)

    logger.info("Ingestion complete.")


if __name__ == "__main__":
    run_ingestion()
