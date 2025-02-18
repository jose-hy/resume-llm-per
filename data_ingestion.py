import logging
# import azure.functions as func
import requests
import os
import ast
import re
import pandas as pd
# import configparser
from dotenv import load_dotenv
import json
from sentence_transformers import SentenceTransformer
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
# Jun: save job postings info before cleaning to check how to clean the data
from pathlib import Path
from datetime import datetime
from tqdm import tqdm as tqdm

load_dotenv()
    
job_titles = [
    "AI Machine Learning",
    "Data Scientist",
    # IT Support & Help Desk Jobs (General IT Roles)
    "IT Support Specialist",
    "Help Desk Technician",
    "Technical Support Specialist",
    "IT Helpdesk Analyst",
    "IT Support Technician",
    "Computer Support Technician",
    "IT Service Desk Technician",
    "IT Customer Support Specialist",
    "IT Associate",
    "IT Field Technician",

    # Network Administration & Infrastructure Jobs
    "Network Technician",
    "Network Support Specialist",
    "Network Administrator (Entry-Level)",
    "Junior Network Engineer",
    "IT Infrastructure Technician",
    "Systems Support Technician",
    "IT Operations Specialist",
    "IT Field Support Engineer",
    "Junior VoIP Engineer",
    "Telecommunications Technician",

    # System Administration & IT Engineering Jobs
    "Systems Administrator (Entry-Level)",
    "Junior System Engineer",
    "Junior Systems Analyst",
    "IT Systems Technician",
    "Cloud Support Associate",
    "Cloud Systems Administrator",
    "Cloud Support Engineer (Entry-Level)",
    "Microsoft 365 Support Specialist",
    "IT Operations Engineer",
    "IT Systems Support Analyst",

    # Cybersecurity & IT Security Jobs
    "Security Analyst (Entry-Level)",
    "IT Security Technician",
    "Cybersecurity Support Specialist",
    "SOC Analyst Level 1",
    "IT Compliance Analyst",
    "Risk and Compliance Analyst (IT)",
    "Junior Security Operations Engineer",
    "IT Security Administrator",
    "Junior Information Security Analyst",
    "Incident Response Technician",

    # Remote IT & Technical Support Jobs
    "Remote IT Support Technician",
    "Technical Support Engineer",
    "Remote Help Desk Technician",
    "IT Consultant (Entry-Level)",
    "Virtual IT Support Technician",
    "Remote Desktop Support Specialist",
    "IT Support Engineer (Remote)",
    "Technical Customer Support Specialist",
    "IT Troubleshooting Specialist",
    "IT Support Coordinator",

    # Specialized IT & Hardware Support Jobs
    "IT Hardware Technician",
    "Hardware Support Specialist",
    "Device Support Technician",
    "Printer Support Technician",
    "PC Technician",
    "POS (Point of Sale) Support Technician",
    "Technical Deployment Specialist",
    "IT Rollout Technician",
    "IT Hardware Analyst",
    "IT Asset Management Specialist"
]


# app = func.FunctionApp()

#@app.timer_trigger(schedule="0 0 9 * * *", arg_name="myTimer", run_on_startup=False,
#              use_monitor=False) 
def run_daily():#myTimer: func.TimerRequest) -> None:
    #if myTimer.past_due:
    #    logging.info('The timer is past due!')

    # logging.info('Starting job ingestion...')

    milvus_uri = os.getenv("ZILLZ_URI")
    milvus_token = os.getenv("ZILLZ_TOKEN")

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

    print("calling Jsearch API ...")
    for job in tqdm(job_titles):
        querystring['query'] = job
        response = requests.get(jsearch_url, headers=headers, params=querystring)
        job_postings_json = response.json()
        file_path = str(job).replace(" ",'-')+".json"
        with open(file_path, "w") as f:
            json.dump(job_postings_json['data'], f)

    print("concate API responses ...")
    df_jobs = pd.DataFrame()
    for job in job_titles:
        file_path = str(job).replace(" ",'-')+".json"
        df_each_job = pd.read_json(file_path, encoding = 'utf-8')
        df_each_job['query_keywords'] = job
        df_jobs = pd.concat([df_jobs, df_each_job], axis=0)

    print(len(df_jobs), "jobs information are processed!")
    
    df_select = df_jobs[
        ['query_keywords','job_id','job_title', 'employer_name', 'employer_logo', 'employer_website',
        'job_publisher', 'job_employment_type',
        'job_apply_link', 'job_description',
        'job_is_remote', 'job_city', 'job_state',
        'job_latitude', 'job_longitude', 'job_benefits',
        'job_highlights', 'job_posted_at_datetime_utc']
    ].copy()

    # Jun: get the path of vector_db.py
    srcpath = os.path.abspath(__file__)

    # Jun: get the folder where vector_db is located
    srcdir = os.path.dirname(srcpath)

    # Jun: create the file path by combining the folder and the file name
    filepath = Path(os.path.join(srcdir, 'before_clean.csv'))

    # Jun: save the df_select to before_clean.csv
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
        # df['job_required_experience'] = df['job_required_experience'].apply(convert_to_dict) # Jun: convert string to dict
        # df_exp = pd.json_normalize(df['job_required_experience']) # Jun: extract key:value paires as multiple columns
        # required_experience = df_exp['required_experience_in_months'] # Jun: only keep 'required_experience_in_months'
        # df = pd.concat([df.drop(columns=['job_required_experience']), df_exp], axis=1)
        # df = pd.concat([df, required_experience], axis=1) # Jun: add'required_experience_in_months' as a new column to original df
        # df['required_experience_in_months'] = df['required_experience_in_months'].fillna(0.0)
        # df['required_experience'] = df['required_experience_in_months'].astype(int) / 12
        
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
    job_postings.to_csv('jobs.csv', index=False)

    connections.connect("default",
                        uri=milvus_uri,
                        token=milvus_token)
    print(f"Connecting to DB: {milvus_uri}")

    # Initialize embedding model
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Define Milvus collection schema
    fields = [
        FieldSchema(name="job_id", dtype=DataType.VARCHAR, is_primary=True, max_length=100),
        FieldSchema(name="job_description_vector", dtype=DataType.FLOAT_VECTOR, dim=384),
        FieldSchema(name="job_description_raw", dtype=DataType.VARCHAR, max_length=50000),
        FieldSchema(name="info", dtype=DataType.VARCHAR, max_length=255),
        FieldSchema(name="degree", dtype=DataType.VARCHAR, max_length=255,enable_analyzer=True,enable_match=True), # new
        FieldSchema(name="remote", dtype=DataType.BOOL, max_length=100), # new
        FieldSchema(name="location_state", dtype=DataType.VARCHAR, max_length=255,enable_analyzer=True,enable_match=True), # new
        FieldSchema(name="employment_type", dtype=DataType.VARCHAR, max_length=255,enable_analyzer=True,enable_match=True), # new
        FieldSchema(name="citizenship", dtype=DataType.BOOL, max_length=100),
        FieldSchema(name="job_apply_link", dtype=DataType.VARCHAR, max_length=255),
        FieldSchema(name="job_posted_at_datetime_utc", dtype=DataType.VARCHAR, max_length=80),
        FieldSchema(name="insert_time", dtype=DataType.VARCHAR, max_length=50)
    ]
    
    schema = CollectionSchema(fields, description="Job listing data with job description embeddings and metadata")
    
    # Create collection (if it doesn't already exist)
    collection_name = "job_listings"
    if collection_name not in utility.list_collections():
        job_collection = Collection(name=collection_name, schema=schema)
    else:
        job_collection = Collection(name=collection_name)
    
    # Prepare lists for each field in the schema to match Milvus requirements
    id_list = []
    vector_list = []
    description_list = []
    info_list = []
    degree_list = []
    remote_list = []
    location_list = []
    emp_type_list = []
    citizenship_list = []
    link_list = []
    job_post_at_timestamp_list = []
    insert_timestamp_list = []  # NEW

    # Populate lists with DataFrame data
    for index, row in job_postings.iterrows():
        job_description_vector = embedder.encode(row['job_description']).tolist()
        
        # Append data for each field
        id_list.append(row['job_id'])  # Optional if using auto-generated ID in Milvus
        vector_list.append(job_description_vector)
        description_list.append(row['job_description'])
        info_list.append(row['info'])
        degree_requirement = ''
        if row['degree_requirement'] == 'Degree required (Bachelor degree or above)':
            degree_requirement = 'required'
        elif row['degree_requirement'] == 'No degree required':
            degree_requirement = 'no_degree'
        else:
            degree_requirement = None
        degree_list.append(degree_requirement)
        remote_list.append(row['remote or not'])
        location_list.append(row['job_state'])
        emp_type_list.append(row['job_employment_type'])
        citizenship_list.append(row['citizenship'])
        link_list.append(row['job_apply_link'])
        job_post_at_timestamp_list.append(row['job_posted_at_datetime_utc'])
        current_time = datetime.now().isoformat()
        insert_timestamp_list.append(current_time)
    
    # Insert data into Milvus collection
    job_collection.upsert([
        id_list,
        vector_list,
        description_list,
        info_list,
        degree_list,
        remote_list,
        location_list,
        emp_type_list,
        citizenship_list,
        link_list,
        job_post_at_timestamp_list,
        insert_timestamp_list
    ])
    
    print("DataFrame indexed into Milvus successfully.")

    logging.info('Python timer trigger function executed.')


run_daily()