from fastapi import APIRouter, UploadFile, File, Depends, Form, Query
from typing import List, Optional
import PyPDF2 as pdf

from ...schemas.job_search import (
    JobSearchVars, JobSearchResponse, ErrorResponse, JobSearchResults,
    AnalysisResponse, AnalysisResults
)
from ...services.ai_service import get_gemini_response, PROMPTS
from ...services.search_service import get_relevant_ids, rerank_results, collection, get_latest_jobs
from ...services.resume_service import resume_parser

router = APIRouter()

async def read_pdf_content(file: UploadFile) -> str:
    """Helper function to read PDF content"""
    reader = pdf.PdfReader(file.file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text

@router.post("/search_jobs", response_model=JobSearchResults)
async def search_jobs(
    file: UploadFile = File(...),
    params: JobSearchVars = Depends(JobSearchVars.as_form),
):
    """
    Search for relevant jobs based on resume and filters
    """
    # Read and parse PDF
    text = await read_pdf_content(file)

    # Parse and summarize resume
    resume_parsed = resume_parser(text)
    resume_summary = get_gemini_response(
        input=None,
        pdf_content=resume_parsed,
        prompt=PROMPTS["resume_summary"]
    )

    # Get relevant job listings
    ids, _, docs, meta = get_relevant_ids(
        query=resume_summary,
        collection=collection,
        count=params.limit,
        offset=params.offset,
        exclude_citizen_only=params.exclude_citizen_only,
        degree=[d.value for d in params.degree] if params.degree else None,
        remote=params.remote,
        location_state=[s.value for s in params.location_state] if params.location_state else None,
        employment_type=[t.value for t in params.employment_type] if params.employment_type else None
    )

    if not docs:
        return ErrorResponse(message="No matching jobs found for your resume and filters.")

    # Always rerank to get consistent scoring
    reranked = rerank_results(query=resume_summary, docs=docs, n=len(docs))
    
    # Format response
    response = []
    for result in reranked.results:
        i = result.index
        response.append(
            JobSearchResponse(
                job_id=ids[i],
                job_title=meta[i]['job_title'],
                job_location=meta[i]['job_location'],
                company=meta[i]['company'],
                description=docs[i],
                score=result.relevance_score,
                degree=meta[i]['degree'],
                remote=meta[i]['remote'],
                location_state=meta[i]['location_state'],
                employment_type=meta[i]['employment_type'],
                citizen=meta[i]['citizen'],
                link=meta[i]['link'],
                job_post_date=meta[i]['job_post_date'],
                job_posted_at=meta[i]['job_posted_at']
            )
        )
    
    # If reranking was not requested, maintain original order but keep Cohere scores
    if not params.rerank:
        response.sort(key=lambda x: ids.index(x.job_id))
    
    return response

@router.post("/analyze/disqualification", response_model=AnalysisResults)
async def disqualification_analysis(
    job_description: str = Form(...),
    resume: UploadFile = File(...)
):
    """
    Analyze why a resume might be disqualified for a specific job
    """
    try:
        # Read and parse resume
        text = await read_pdf_content(resume)
        resume_parsed = resume_parser(text)
        
        # Get analysis from AI
        analysis = get_gemini_response(
            input=job_description,
            pdf_content=resume_parsed,
            prompt=PROMPTS["resume_disqualifications"]
        )
        
        return AnalysisResponse(analysis=analysis)
    except Exception as e:
        return ErrorResponse(message=f"Error analyzing resume: {str(e)}")

@router.post("/analyze/improvement", response_model=AnalysisResults)
async def resume_improvement(
    job_description: str = Form(...),
    resume: UploadFile = File(...)
):
    """
    Get suggestions for improving a resume for a specific job
    """
    try:
        # Read and parse resume
        text = await read_pdf_content(resume)
        resume_parsed = resume_parser(text)
        
        # Get improvement suggestions from AI
        analysis = get_gemini_response(
            input=job_description,
            pdf_content=resume_parsed,
            prompt=PROMPTS["resume_improvements"]
        )
        
        return AnalysisResponse(analysis=analysis)
    except Exception as e:
        return ErrorResponse(message=f"Error generating improvement suggestions: {str(e)}")

@router.post("/generate/cover-letter", response_model=AnalysisResults)
async def cover_letter_generation(
    job_description: str = Form(...),
    resume: UploadFile = File(...)
):
    """
    Generate a cover letter based on the resume and job description
    """
    try:
        # Read and parse resume
        text = await read_pdf_content(resume)
        resume_parsed = resume_parser(text)
        
        # Generate cover letter
        cover_letter = get_gemini_response(
            input=job_description,
            pdf_content=resume_parsed,
            prompt=PROMPTS["cover_letter"]
        )
        
        return AnalysisResponse(analysis=cover_letter)
    except Exception as e:
        return ErrorResponse(message=f"Error generating cover letter: {str(e)}")

@router.get("/latest_jobs", response_model=List[JobSearchResponse])
async def get_latest_job_listings(
    limit: Optional[int] = Query(10, description="Number of jobs to return", ge=1, le=50)
):
    """
    Get the latest job listings without any filtering.
    This endpoint is designed for the default page view.
    """
    try:
        jobs = get_latest_jobs(collection=collection, limit=limit)
        return [JobSearchResponse(**job) for job in jobs]
    except Exception as e:
        return ErrorResponse(message=f"Error fetching latest jobs: {str(e)}")

@router.get("/")
async def root():
    return {"message": "Hello World"} 