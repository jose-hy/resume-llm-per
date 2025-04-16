import logging
import requests
import os
import ast
import re
import pandas as pd
import json
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
from pathlib import Path
from datetime import datetime
from tqdm import tqdm as tqdm
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import gc
import torch

load_dotenv()

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Set all cache directories to /tmp
os.environ['TRANSFORMERS_CACHE'] = '/tmp/huggingface'
os.environ['HF_HOME'] = '/tmp/huggingface'
os.environ['HF_DATASETS_CACHE'] = '/tmp/huggingface'
os.environ['XDG_CACHE_HOME'] = '/tmp/huggingface'

milvus_index_name = "job_listings1"

# Create data_ingest_tmp directory if it doesn't exist
data_dir = Path("/tmp/data_ingest_tmp")  # Use /tmp for Lambda
data_dir.mkdir(exist_ok=True)

# Initialize the embedding model with optimized settings
try:
    logger.info("Initializing embedding model...")
    # Create cache directory if it doesn't exist
    os.makedirs('/tmp/huggingface', exist_ok=True)
    
    # Set environment variables to disable CPU info checks
    os.environ['OMP_NUM_THREADS'] = '1'
    os.environ['MKL_NUM_THREADS'] = '1'
    os.environ['OPENBLAS_NUM_THREADS'] = '1'
    os.environ['VECLIB_MAXIMUM_THREADS'] = '1'
    os.environ['NUMEXPR_NUM_THREADS'] = '1'
    
    # Disable PyTorch's CPU info checks
    torch.backends.cudnn.enabled = False
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    
    # Initialize model with minimal settings and force CPU device
    embedder = SentenceTransformer('all-MiniLM-L6-v2', 
                                 cache_folder='/tmp/huggingface',
                                 device='cpu')
    
    # Force model to use single thread
    if hasattr(embedder, 'model'):
        embedder.model.to('cpu')
        embedder.model.eval()
    
    logger.info("Embedding model initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize embedding model: {str(e)}")
    raise

def process_job_chunk(job_postings_chunk, embedder, collection):
    """Process a chunk of job postings and insert into Milvus"""
    try:
        # Process each job in the chunk individually to minimize memory usage
        for _, row in job_postings_chunk.iterrows():
            try:
                logger.info(f"Processing job ID: {row['job_id']}")
                
                # Clear memory before processing each job
                gc.collect()
                
                # Truncate job description if too long
                job_description = row['job_description'][:10000] if len(row['job_description']) > 10000 else row['job_description']
                
                # Generate embedding with memory optimization
                with torch.no_grad():  # Disable gradient computation
                    try:
                        logger.info(f"Generating embedding for job {row['job_id']}")
                        job_description_vector = embedder.encode(
                            job_description,
                            convert_to_tensor=True,
                            normalize_embeddings=True,
                            show_progress_bar=False
                        ).cpu().numpy().tolist()
                        logger.info(f"Embedding generated successfully for job {row['job_id']}")
                    except Exception as e:
                        logger.error(f"Error generating embedding for job {row['job_id']}: {str(e)}")
                        continue
                
                # Truncate job_apply_link if needed
                job_link = row['job_apply_link'][:255] if len(row['job_apply_link']) > 255 else row['job_apply_link']
                
                # Process degree requirement
                degree_requirement = 'required' if row['degree_requirement'] == 'Degree required (Bachelor degree or above)' else \
                                   'no_degree' if row['degree_requirement'] == 'No degree required' else None
                
                # Convert job_posted_at_datetime_utc to timestamp
                try:
                    posted_at = datetime.fromisoformat(row['job_posted_at_datetime_utc'].replace('Z', '+00:00'))
                    timestamp = int(posted_at.timestamp() * 1000)  # Convert to milliseconds
                except Exception as e:
                    logger.error(f"Error converting datetime for job {row['job_id']}: {str(e)}")
                    timestamp = int(datetime.now().timestamp() * 1000)  # Use current time as fallback
                
                # Insert single job into Milvus
                try:
                    logger.info(f"Attempting to insert job {row['job_id']} into Milvus")
                    collection.upsert([
                        [row['job_id']],
                        [job_description_vector],
                        [job_description],
                        # [row['info']],
                        [row['job_title']],
                        [row['employer_name']],
                        [row['job_location']],
                        [degree_requirement],
                        [row['remote or not']],
                        [row['job_state']],
                        [row['job_employment_type']],
                        [row['citizenship']],
                        [job_link],
                        [timestamp],
                        [row['job_posted_at_datetime_utc']],
                        [datetime.now().isoformat()]
                    ])
                    logger.info(f"Successfully inserted job {row['job_id']} into Milvus")
                    
                    # Verify insertion
                    try:
                        search_result = collection.query(
                            expr=f'job_id == "{row["job_id"]}"',
                            output_fields=["job_id", "job_title"]
                        )
                        if search_result:
                            logger.info(f"Verified job {row['job_id']} exists in database")
                        else:
                            logger.warning(f"Job {row['job_id']} not found in database after insertion")
                    except Exception as e:
                        logger.error(f"Error verifying job {row['job_id']} insertion: {str(e)}")
                    
                except Exception as e:
                    logger.error(f"Error inserting job {row['job_id']} into Milvus: {str(e)}")
                    continue
                
                # Clear memory after each job
                del job_description_vector
                gc.collect()
                
            except Exception as e:
                logger.error(f"Error processing job {row['job_id']}: {str(e)}")
                continue
        
    except Exception as e:
        logger.error(f"Error processing chunk: {str(e)}")
        raise

def delete_old_jobs(collection):
    """Delete jobs older than a week from the Milvus database"""
    try:
        logger.info("Deleting jobs older than a week...")
        
        # Calculate timestamp for one week ago
        one_week_ago = int((datetime.now().timestamp() - 7 * 24 * 60 * 60) * 1000)  # Convert to milliseconds
        
        # Delete jobs older than a week
        expr = f"job_posted_at < {one_week_ago}"
        collection.delete(expr)
        
        logger.info(f"Successfully deleted jobs older than a week")
    except Exception as e:
        logger.error(f"Error deleting old jobs: {str(e)}")
        raise

def run_daily():
    try:
        milvus_uri = os.getenv("ZILLZ_URI")
        milvus_token = os.getenv("ZILLZ_TOKEN")
        
        if not milvus_uri or not milvus_token:
            raise ValueError("Missing required environment variables: ZILLZ_URI or ZILLZ_TOKEN")

        logger.info(f"Connecting to Milvus at {milvus_uri}")
        # Connect to Milvus
        connections.connect("default", uri=milvus_uri, token=milvus_token)
        logger.info("Successfully connected to Milvus")

        # Get or create collection
        collection_name = milvus_index_name
        if collection_name not in utility.list_collections():
            logger.info(f"Creating new collection: {collection_name}")
            # Define Milvus collection schema
            fields = [
                FieldSchema(name="job_id", dtype=DataType.VARCHAR, is_primary=True, max_length=100),
                FieldSchema(name="job_description_vector", dtype=DataType.FLOAT_VECTOR, dim=384),
                FieldSchema(name="job_description_raw", dtype=DataType.VARCHAR, max_length=50000),
                # FieldSchema(name="info", dtype=DataType.VARCHAR, max_length=255),
                FieldSchema(name="job_title", dtype=DataType.VARCHAR, max_length=255),
                FieldSchema(name="employer_name", dtype=DataType.VARCHAR, max_length=255),
                FieldSchema(name="job_location", dtype=DataType.VARCHAR, max_length=255),

                FieldSchema(name="degree", dtype=DataType.VARCHAR, max_length=255,enable_analyzer=True,enable_match=True),
                FieldSchema(name="remote", dtype=DataType.BOOL, max_length=100),
                FieldSchema(name="location_state", dtype=DataType.VARCHAR, max_length=255,enable_analyzer=True,enable_match=True),
                FieldSchema(name="employment_type", dtype=DataType.VARCHAR, max_length=255,enable_analyzer=True,enable_match=True),
                FieldSchema(name="citizenship", dtype=DataType.BOOL, max_length=100),
                FieldSchema(name="job_apply_link", dtype=DataType.VARCHAR, max_length=255),
                FieldSchema(name="job_posted_at", dtype=DataType.INT64),  # Unix timestamp in milliseconds
                FieldSchema(name="job_posted_at_datetime", dtype=DataType.VARCHAR, max_length=50),  # Human readable datetime
                FieldSchema(name="insert_time", dtype=DataType.VARCHAR, max_length=50)
            ]
            
            schema = CollectionSchema(fields, description="Job listing data with job description embeddings and metadata")
            
            job_collection = Collection(name=collection_name, schema=schema)
            logger.info(f"Created new collection: {collection_name}")
        else:
            logger.info(f"Using existing collection: {collection_name}")
            job_collection = Collection(name=collection_name)

        # Load collection into memory
        logger.info("Loading collection into memory")
        job_collection.load()
        logger.info("Collection loaded successfully")
        
        # Delete old jobs before ingesting new ones
        delete_old_jobs(job_collection)

        # Check if data files already exist
        first_job_file = data_dir / f"{str(job_titles[0]).replace(' ','-')}.json"
        if not first_job_file.exists():
            logger.info("No existing data found. Fetching from Jsearch API...")
            jsearch_url = os.getenv("JSEARCH_URL")
            jsearch_api_key = os.getenv("JSEARCH_API_KEY")

            querystring = {
                "page": "1",
                "num_pages": "10",
                "date_posted": "week",
                "employment_types": "FULLTIME, CONTRACTOR, PARTTIME, INTERN",
                "job_requirements": "under_3_years_experience, no_experience, no_degree",
                "exclude_job_publishers": "Dice, jooble, Clearance Jobs, Geebo, Talent.com"
            }

            headers = {
                "X-RapidAPI-Key": jsearch_api_key,
                "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
            }

            logger.info("Calling Jsearch API...")
            for job in job_titles:
                querystring['query'] = job
                response = requests.get(jsearch_url, headers=headers, params=querystring)
                job_postings_json = response.json()
                file_path = data_dir / f"{str(job).replace(' ','-')}.json"
                with open(file_path, "w") as f:
                    json.dump(job_postings_json['data'], f)
        else:
            logger.info("Found existing data files. Skipping API calls...")

        logger.info("Concatenating API responses...")
        df_jobs = pd.DataFrame()
        for job in job_titles:
            file_path = data_dir / f"{str(job).replace(' ','-')}.json"
            df_each_job = pd.read_json(file_path, encoding='utf-8')
            df_each_job['query_keywords'] = job
            df_jobs = pd.concat([df_jobs, df_each_job], axis=0)

        logger.info(f"{len(df_jobs)} jobs information are processed!")
        
        df_select = df_jobs[
            ['query_keywords','job_id','job_title', 'employer_name', 'job_location', 'employer_logo', 'employer_website',
            'job_publisher', 'job_employment_type',
            'job_apply_link', 'job_description',
            'job_is_remote', 'job_city', 'job_state',
            'job_latitude', 'job_longitude', 'job_benefits',
            'job_highlights', 'job_posted_at_datetime_utc']
        ].copy()

        # Save to before_clean.csv in data_ingest_tmp directory
        filepath = data_dir / 'before_clean.csv'
        df_select.to_csv(filepath)

        def convert_to_dict(val):
            if isinstance(val, dict):
                return val  # It's already a dictionary, so return as is
            elif isinstance(val, str):
                try:
                    return ast.literal_eval(val)  # Convert string to dictionary
                except (ValueError, SyntaxError):
                    return None  # Handle any errors gracefully
            return None  # In case of any unexpected type

        def clean_job_postings(df):
            # Combine job city and state into a single location column
            df['job_location'] = df['job_city'] + ', ' + df['job_state']
            # Create a unique identifier for job postings
            df['info'] = df['job_title'] + '|' + df['job_location'] + '|' + df['employer_name']
            # Remove duplicate job postings based on 'info' and 'job_description'
            df = df.drop_duplicates(subset='info', ignore_index=True)  # Reset index after removing duplicates
            df = df.drop_duplicates(subset='job_description', ignore_index=True)
            # Filter out job postings from unwanted publishers
            df = df[~df['job_publisher'].str.contains('Geebo', na=False)]  # Exclude 'Geebo' postings
            
            # Identify citizenship requirements based on specific keywords
            df['citizenship'] = df['job_description'].str.contains(r'clearance|SCI|US citizenship|US Citizen|U.S. citizenship', case=False, na=False)
            
            # Define a helper function to classify degree requirements
            def classify_degree_requirement(job_description):
                """
                Classify the degree requirement into two categories:
                - "No degree required"
                - "Degree required (Bachelor degree or above)"
                """
                if pd.isna(job_description):
                    return "No degree required"
                
                # Check for any degree requirement (Bachelor's, Master's, PhD, etc.)
                if re.search(r"PhD|doctoral|doctorate|Master's|Master|MBA|M\.Sc\.|MA|MS|Bachelor's|Bachelor|B\.Sc\.|BA|BS|college degree|university degree|academic qualification|graduate degree|undergraduate degree|postgraduate degree", 
                        job_description, re.IGNORECASE):
                    return "Degree required (Bachelor degree or above)"
                
                # Default case
                return "No degree required"

            # Apply the helper function to the 'job_description' column    
            df['degree_requirement'] = df['job_description'].apply(classify_degree_requirement)
            
            df['remote or not'] = df['job_is_remote'].apply(lambda x: str(x).strip().lower() == 'true')

            return df

        # don't forget to read_csv!
        df_select = clean_job_postings(pd.read_csv(filepath)) 

        # Set up the DataFrame
        job_postings = df_select
        job_postings = job_postings.dropna(subset=['info', 'job_description'])
        job_postings = job_postings.fillna('') # na is not filled if use in clean_job_postings
        job_postings.to_csv(data_dir / 'jobs.csv', index=False)

        # Process jobs in chunks
        CHUNK_SIZE = 50  # Adjust based on available memory
        logger.info(f"Processing jobs in chunks of {CHUNK_SIZE}")
        
        # Process jobs in chunks
        for i in range(0, len(job_postings), CHUNK_SIZE):
            chunk = job_postings.iloc[i:i+CHUNK_SIZE]
            logger.info(f"Processing chunk {i//CHUNK_SIZE + 1} of {(len(job_postings) + CHUNK_SIZE - 1)//CHUNK_SIZE}")
            process_job_chunk(chunk, embedder, job_collection)
            
            # Clear memory after each chunk
            gc.collect()

        logger.info("All chunks processed successfully")
        logging.info('Python timer trigger function executed.')
        
        # Clean up data files after processing
        logger.info("Cleaning up data files...")
        for job in job_titles:
            file_path = data_dir / f"{str(job).replace(' ','-')}.json"
            if file_path.exists():
                try:
                    file_path.unlink()
                    logger.info(f"Removed data file: {file_path}")
                except Exception as e:
                    logger.error(f"Error removing data file {file_path}: {str(e)}")
        
        # Also remove the CSV files
        csv_files = ['before_clean.csv', 'jobs.csv']
        for csv_file in csv_files:
            file_path = data_dir / csv_file
            if file_path.exists():
                try:
                    file_path.unlink()
                    logger.info(f"Removed CSV file: {file_path}")
                except Exception as e:
                    logger.error(f"Error removing CSV file {file_path}: {str(e)}")
        
        logger.info("Data files cleanup completed")

    except Exception as e:
        logger.error(f"Error in run_daily: {str(e)}")
        raise
    finally:
        # Clean up
        gc.collect()
        if 'job_collection' in locals():
            job_collection.release()

def lambda_handler(event, context):
    """
    AWS Lambda handler function
    """
    try:
        logger.info('Starting job ingestion...')
        run_daily()
        return {
            'statusCode': 200,
            'body': json.dumps('Job ingestion completed successfully')
        }
    except Exception as e:
        logger.error(f'Error in job ingestion: {str(e)}')
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error in job ingestion: {str(e)}')
        }