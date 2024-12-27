# __import__('pysqlite3')
import sys
# sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
# from dotenv import load_dotenv
import json
import os, time
from os import path, listdir
import numpy as np
import pandas as pd
import PyPDF2 as pdf
import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import chromadb
import cohere
from chromadb.utils import embedding_functions
from parse_resume import resume_parser

#--------------------------------------------LLM (Gemini pro) API-----------------------------------------------------------#
# load gemini pro LLM model API from environment variable
# load_dotenv() not needed as it is already stored environment variable in my system, use os.environ
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_gemini_response(input,pdf_content,prompt):
    # the higher temperature, more creative responses you will get
    generation_config = {
        "temperature": 0.0
    }
    # remove automated response blocking
    safety_settings={
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE
    }
    model=genai.GenerativeModel('gemini-pro')

    results = ''
    try:
        if input:
        # The output is a single piece of generated text that takes into account all the input components provided in the list.
            response=model.generate_content([prompt,'job description:'+input,'resume:'+pdf_content], generation_config=generation_config)
        else:
            response=model.generate_content([prompt, 'resume:'+pdf_content], safety_settings=safety_settings)
        results = response.text
    # for some prompts Gemini will avoid generating the results even if you set all the filters to none.
    except ValueError:
        # If the response doesn't contain text, check if the prompt was blocked.
        st.write(response.prompt_feedback)
        # Also check the finish reason to see if the response was blocked, if so, will show 'FinishReason.SAFETY'
        st.write(response.candidates[0].finish_reason)
        # If the finish reason was SAFETY, the safety ratings have more details.
        st.write(response.candidates[0].safety_ratings)
        results = 'Encounter Error with Gemini AI Model'
    # except InternalServerError:
    #     st.write(response.prompt_feedback)
    #     results = 'Encounter Error with Gemini AI Model'
    except Exception as err:
        st.write(err)
        results = 'Encounter Error with Gemini AI Model'	    
    return results

# Generate prompts to generate resume revision and cover letter template
input_prompt_resume_summary = """
You are an skilled Applicant Tracking System scanner with a deep understanding of Applicant Tracking System functionality, please 
read the following resume carefully and summarize it within 500 word to include the following information in the resume step by step.
If there is a summary included, copy the summary directly to your response and append the following contents.
Please first find the important skills and tools included in the resume. 
Then conclude the background including all the work experience, do not need to include the specific number in each experience.
and projects in the resume. Finally summarize the education background with the highest degree level and the area of study and double 
check to omit the university or school attended. In other words, do not include the university attended.
"""

input_prompt_resume1 = """
You are a skilled Applicant Tracking System scanner with a deep understanding of Applicant Tracking System functionality, 
your task is to evaluate the resume against the provided job description. 
Find out the requirements that make this resume disqualified for this job in a list. Please first check the required or basic qualification,
then move on to the preferred qualifications.
Please limit the list no more than four most important bullet points and no more than 30 words for each bullet points.
"""

input_prompt_resume2 = """
You are submitting a resume to a job with the provided job description. 
Find out the requirements in the job description you should add to make you qualify for this job.
Please limit the list no more than three most important bullet points and no more than 30 words for each bullet points.
"""

input_prompt_cover_letter = """
You are the applicant who applied for this job and want to compose a strong but concise cover letter to convince the employer you have the skills and the experience for this job.
The first paragraph of the  cover letter must briefly discuss the your background, including both experience and projects. 
The second paragraph discuss how the applicant fit this role based on your skillsets matches the job requirements. Do not include the skillset not in the applicant's resume.
The third paragraph discuss the your interest in this role and thanks for the consideration.
Please limit the word count of cover letter no more than 300 words.
"""
#---------------------------------------------------Vector Database-------------------------------------------------------#

# Get vector database collection from local storage
chroma_client = chromadb.PersistentClient(path='.')
default_ef = embedding_functions.DefaultEmbeddingFunction()
collection = chroma_client.get_collection(name="job_postings")

# Find the most relevant job description and return the job posting information 
def get_relevant_ids(query, db, count=3, exclude_citizen_only=False, degree=None, remote=None, location_state=None, employment_type=None):
    # Filter initialization
    where = {"$and": []}
    
    # Apply Boolean filters for citizenship and remote work
    if exclude_citizen_only:
        where["$and"].append({"citizen": {"$eq": False}})
    
    if remote is not None:  # Handles both True and False explicitly
        where["$and"].append({"remote": {"$eq": remote}})
        
    
    # Add degree filter
    if degree:
        # Map user-friendly options to database values
        degree_map = {
            "No degree required": "No degree required",
            "Degree required (Bachelor degree or above)": "Degree required (Bachelor degree or above)"
        }
        # Map the selected degrees to their database values
        degree_values = [degree_map[d] for d in degree if d in degree_map]
        where["$and"].append({"degree": {"$in": degree_values}})
    
    # Add location filter
    if location_state and "All" not in location_state:
        where["$and"].append({"location_state": {"$in": location_state}})
    
    # Add employment type filter
    if employment_type:  # Check if employment_type is not empty or None
        where["$and"].append({"employment_type": {"$in": employment_type}})
    
    # Remove "$and" if no filters are applied
    if not where["$and"]:
        where = None
    # Query the database
    try:
        passage = db.query(
            query_texts=[query],
            n_results=count,
            include=["distances", "documents", "metadatas"],
            where=where
        )
        # Extract the results
        ids = passage['ids'][0]
        cos = passage['distances'][0]
        doc = passage['documents'][0]
        metadata = passage['metadatas'][0]
        return ids, cos, doc, metadata
    except Exception as e:
        st.error(f"Query failed: {e}")
        return [], [], [], []
    

# query results example
# {
#  'documents': [[
#      'This is a job description for a Data Scientist role requiring Python and SQL expertise.',
#      'This is a job description for a Machine Learning Engineer role requiring TensorFlow and PyTorch experience.',
#      'This is a job description for an AI Research Scientist role focused on NLP and Generative AI.'
#  ]],
#  'ids': [['job1', 'job2', 'job3']],
#  'distances': [[0.234, 0.567, 0.876]],
#  'uris': None,
#  'data': None,
#  'metadatas': [[
#     {
#          'info': 'Data Scientist | San Francisco, CA | TechCorp',
#          'degree': 'Graduate degree required',
#         'remote': True,
#          'location_state': 'CA',
#          'employment_type': 'FULLTIME',
#          'citizen': False,
#          'link': 'https://example.com/job1'
#      }


# Upload resume
resume = ''
@st.cache_data
def input_pdf_text(uploaded_file):
    reader=pdf.PdfReader(uploaded_file)
    text=""
    for page in range(len(reader.pages)):
        page=reader.pages[page]
        text+=str(page.extract_text())
    return text
#---------------------------------------------------Rerank---------------------------------------------------------#
cohere_api_key=os.getenv("COHERE_API_KEY")
co = cohere.Client(cohere_api_key)

# New Code - Jun
#def rerank_results(co, query, docs, metadatas, n=3):
    # Prepare reranking documents with metadata for context
#    contextualized_docs = [
#        f"{meta['info']} | Degree: {meta['degree']} | Remote: {'Yes' if meta['remote'] else 'No'} | "
#        f"Location: {meta.get('location_state', 'Unknown')} | Employment Type: {meta['employment_type']} | {doc}"
#        for doc, meta in zip(docs, metadatas)
#    ]
#    results = co.rerank(model='rerank-english-v2.0', query=query, documents=contextualized_docs, top_n=n)
#    return results

def rerank_results(co, query, docs, n=3):
    if not docs:
        st.warning("No documents available for reranking.")
        return None  # Return None if no documents
    results = co.rerank(model='rerank-english-v2.0', query=query, documents=docs, top_n=n)
    return results

# Original Code
#def rerank_results(co, query, docs, n = 3):
#    results = co.rerank(model = 'rerank-english-v2.0', query = query, documents = docs, top_n = n)
#    return results

#--------------------------------------------------- Streamlit Website---------------------------------------------------------#
# Page setup
st.title("Data Science Job Matching and Resume Enhancement")
st.markdown("Powered by Gemini Pro and Chroma vector database to help you find the most relevant \
         job openings and provide specific resume revision suggestions and cover letter templates.")
st.markdown("Please be patient while waiting for the LLM-generated suggestions.") 
st.divider()

# Sidebar for user interaction
submit = False
exclude_citizen_only = True
resume_summary = ''

with st.sidebar:
    # File uploader for resume
    uploaded_file = st.file_uploader("Upload Your Resume", type="pdf", help="Please upload a PDF. The app won't save your resume.")
    
    if uploaded_file is not None:
        st.write("PDF Uploaded Successfully")
        # Extract text from uploaded resume
        resume = input_pdf_text(uploaded_file)
        # Parse and summarize the resume
        resume_parsed = resume_parser(resume)
        resume_summary = get_gemini_response(input=None, pdf_content=resume_parsed, prompt=input_prompt_resume_summary)

    # Number of results to display
    result_count = st.number_input('Results count', 1, 100, 20)
    st.write('')  # Insert a blank line for spacing

    # Citizenship filter
    citizenship_included = st.checkbox('Include US citizen-only jobs')
    exclude_citizen_only = not citizenship_included

    # Remote job filter
    remote_included = st.checkbox('Include remote jobs only')
    remote_filter = True if remote_included else None  # Set to True if checked, otherwise None

    # Degree requirement filter (multi-select)
    degree_options = ['No degree required', 'Degree required (Bachelor degree or above)']
    selected_degrees = st.multiselect('Select Degree Requirements', degree_options, default=degree_options)


    # Location filter (multi-select)
    location_options = [
        'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware', 'Florida', 
        'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 
        'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 
        'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 
        'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 
        'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming', 
        'District of Columbia', 'All'
    ]
    selected_locations = st.multiselect('Select Locations', location_options, default=['All'])

    # Employment type filter (multi-select)
    employment_types = ['FULLTIME', 'PARTTIME', 'CONTRACT', 'INTERN']
    selected_employment_types = st.multiselect('Select Employment Types', employment_types, default=employment_types)

    # Submit button
    submit = st.button("Generate LLM-powered results")
    
    if submit and resume_summary != '':
        st.markdown('## Resume Summary:')
        st.markdown(resume_summary)

# Display results (outside the sidebar)
if submit and resume_summary != '':
    # Convert 'All' in location to None (no filter)
    location_filter = None if 'All' in selected_locations else selected_locations

    # Query the vector database with the updated filters
    results, scores, doc, meta = get_relevant_ids(
        query=resume_summary,
        db=collection,
        count=result_count,
        exclude_citizen_only=exclude_citizen_only,
        remote=remote_filter,  # Fixed remote variable
        degree=selected_degrees,  # Directly pass the degree_filter
        location_state=location_filter,
        employment_type=selected_employment_types
    )

    # Initialize reranked to avoid NameError
    reranked = None
    
    if not doc:
        st.warning("No matching jobs found.")
    else:
        reranked = rerank_results(co, query=resume_summary, docs=doc, n=result_count)

    if reranked:
        st.markdown('## Matched Jobs')
        with st.container():
            for index in range(len(reranked.results)):
                i = reranked.results[index].index
                score = reranked.results[index].relevance_score

                # Expandable container for each job
                with st.expander(meta[i]['info']):
                    st.markdown(f'Similarity score: {score:.2f}')
                    st.markdown('**Job Description**')
                    st.write(doc[i])
                    st.link_button("Apply Here", meta[i]['link'], type="primary")

                    # Generate LLM-powered suggestions
                    response = get_gemini_response(doc[i], resume, input_prompt_resume1)
                    st.subheader("Disqualifications")
                    st.write(response)

                    response = get_gemini_response(doc[i], resume, input_prompt_resume2)
                    st.subheader("Skills to Add")
                    st.write(response)

                    response = get_gemini_response(doc[i], resume, input_prompt_cover_letter)
                    st.subheader("Cover Letter")
                    st.write(response)

                    # Add delay to prevent API throttling
                    if i % 5 == 0:
                        time.sleep(5)
    else:
        st.warning("No reranked jobs available.")

    
