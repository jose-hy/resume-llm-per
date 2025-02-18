from typing import Annotated
from .parse_resume import resume_parser
import PyPDF2 as pdf
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from pymilvus import connections, Collection
from sentence_transformers import SentenceTransformer

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from .query import *
import cohere

load_dotenv()

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# loading configs
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

milvus_uri = os.getenv('ZILLZ_URI')
token = os.getenv('ZILLZ_TOKEN')
connections.connect("default", uri=milvus_uri, token=token)
collection = Collection("job_listings") 
embedder = SentenceTransformer('all-MiniLM-L6-v2')


cohere_api_key=os.getenv("COHERE_API_KEY")
co = cohere.Client(cohere_api_key)

def get_gemini_response(input,pdf_content,prompt, verbose=False):
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
        if verbose:
            # If the response doesn't contain text, check if the prompt was blocked.
            print(response.prompt_feedback)
            # Also check the finish reason to see if the response was blocked, if so, will show 'FinishReason.SAFETY'
            print(response.candidates[0].finish_reason)
            # If the finish reason was SAFETY, the safety ratings have more details.
            print(response.candidates[0].safety_ratings)
        results = 'Encounter Error with Gemini AI Model'
    # except InternalServerError:
    #     st.write(response.prompt_feedback)
    #     results = 'Encounter Error with Gemini AI Model'
    except Exception as err:
        if verbose:
            print(err)
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

# Find the most relevant job description and return the job posting information 
# def get_relevant_ids(query, collection, count=3, citizen_required=False, year_min=0, year_max=30):
def get_relevant_ids(query, collection, count=10, offset=10, exclude_citizen_only=False, degree=list[None], remote=None, location_state=list[None], employment_type=list[None]):
    # Define search parameters
    query_vector = embedder.encode(query).tolist()
    
    search_params = {
        "metric_type": "COSINE",  # Use appropriate metric, e.g., "L2" or "IP" based on your use case
        "params": {"nprobe": 10},  # Adjust nprobe for efficiency/accuracy tradeoff
        "offset": offset,
    }
    
    bool_expr = []

    if exclude_citizen_only:
        bool_expr.append(f"citizenship == {False}")
    if degree:
        bool_expr.append(f"degree in {degree}")
    if remote:
        bool_expr.append(f"remote == {remote}")
    if location_state and 'All' not in location_state:
        bool_expr.append(f"location_state in {location_state}")
    if employment_type and ('Full-time' in employment_type or 'Part-time' in employment_type):
        bool_expr.append(f"employment_type in {employment_type} or employment_type == 'Full-time and Part-time'")

    bool_expr = " and ".join(bool_expr)
    
    print(bool_expr)

    search_results = collection.search(
        data=[query_vector],  # Query vector
        anns_field="job_description_vector",  # Replace with the name of your vector field
        param=search_params,
        limit=count,  # Number of results to retrieve
        expr=bool_expr,  # Filter expression
        output_fields=["*"]  # Replace with actual field names
    )
    
    # Parse results
    ids, distances, docs, metadatas = [], [], [], []
    for hit in search_results[0]:
        ids.append(hit.id)
        distances.append(hit.distance)
        docs.append(hit.entity.get("job_description_raw"))  
        metadata={"info": hit.entity.get('info'),
                  "degree": hit.entity.get('degree'),
                  "remote": hit.entity.get('remote'),
                  "location_state": hit.entity.get('location_state'),
                  "employment_type": hit.entity.get('employment_type'),
                  "citizen": hit.entity.get('citizenship'),
                  "link": hit.entity.get('job_apply_link'),
                  "job_post_date": hit.entity.get('job_posted_at_datetime_utc'),
                 }
        metadatas.append(metadata)  

    return ids, distances, docs, metadatas

def rerank_results(co, query, docs, n=3):
    if not docs:
        print("No documents available for reranking.")
        return None  # Return None if no documents
    results = co.rerank(model='rerank-english-v2.0', query=query, documents=docs, top_n=n)
    return results

@app.post("/search_jobs")
async def search_jobs(
        file: UploadFile, 
        params: JobSearchVars = Depends(JobSearchVars.as_form),
    ):
    reader=pdf.PdfReader(file.file)
    text=""
    for page in range(len(reader.pages)):
        page=reader.pages[page]
        text+=str(page.extract_text())

    # Parse and summarize the resume
    resume_parsed = resume_parser(text)
    resume_summary = get_gemini_response(input=None, pdf_content=resume_parsed, prompt=input_prompt_resume_summary)

    location_state = [state.value for state in params.location_state] if params.location_state else None
    degree = [degree.value for degree in params.degree] if params.degree else None
    employment_type = [employment_type.value for employment_type in params.employment_type] if params.employment_type else None

    exclude_citizen_only = params.exclude_citizen_only if params.exclude_citizen_only else None
    remote = params.remote if params.remote else None
    rerank = params.remote if params.remote else True
    # Query the vector database with the updated filters
    ids, scores, doc, meta = get_relevant_ids(
        query=resume_summary,
        collection=collection,
        count=params.limit,
        offset=params.offset,
        exclude_citizen_only=exclude_citizen_only,
        remote=remote,  # Fixed remote variable
        degree=degree,  # Directly pass the degree_filter
        location_state=location_state,
        employment_type=employment_type
    )

    if not doc:
        return {"message","No matching jobs found."}
    
    reranked = None
    if rerank:
        reranked = rerank_results(co, query=resume_summary, docs=doc, n=(params.limit-params.offset))

    res = []
    for index in range(len(reranked.results)):
        i = reranked.results[index].index
        score = reranked.results[index].relevance_score
        job_id = ids[i]
        info = meta[i]['info']
        link = meta[i]['info']
        post_date = meta[i]['job_post_date']
        description = doc[i]

        res.append({"job_id": job_id,
                    "job_info": info,
                    "job_post_date": post_date,
                    "description": description,
                    "link":link,
                    "score": score})
    return meta


@app.get("/")
async def root():
    return {"message": "Hello World"}