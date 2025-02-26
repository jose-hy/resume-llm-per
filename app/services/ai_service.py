from typing import Optional
import google.generativeai as genai
from ..core.config import settings, GEMINI_SAFETY_SETTINGS

# Prompts
PROMPTS = {
    "resume_summary": """
You are an skilled Applicant Tracking System scanner with a deep understanding of Applicant Tracking System functionality, please 
read the following resume carefully and summarize it within 500 word to include the following information in the resume step by step.
If there is a summary included, copy the summary directly to your response and append the following contents.
Please first find the important skills and tools included in the resume. 
Then conclude the background including all the work experience, do not need to include the specific number in each experience.
and projects in the resume. Finally summarize the education background with the highest degree level and the area of study and double 
check to omit the university or school attended. In other words, do not include the university attended.
""",
    "resume_disqualifications": """
You are a skilled Applicant Tracking System scanner with a deep understanding of Applicant Tracking System functionality, 
your task is to evaluate the resume against the provided job description. 
Find out the requirements that make this resume disqualified for this job in a list. Please first check the required or basic qualification,
then move on to the preferred qualifications.
Please limit the list no more than four most important bullet points and no more than 30 words for each bullet points.
""",
    "resume_improvements": """
You are submitting a resume to a job with the provided job description. 
Find out the requirements in the job description you should add to make you qualify for this job.
Please limit the list no more than three most important bullet points and no more than 30 words for each bullet points.
""",
    "cover_letter": """
You are the applicant who applied for this job and want to compose a strong but concise cover letter to convince the employer you have the skills and the experience for this job.
The first paragraph of the  cover letter must briefly discuss the your background, including both experience and projects. 
The second paragraph discuss how the applicant fit this role based on your skillsets matches the job requirements. Do not include the skillset not in the applicant's resume.
The third paragraph discuss the your interest in this role and thanks for the consideration.
Please limit the word count of cover letter no more than 300 words.
"""
}

def get_gemini_response(input: Optional[str], pdf_content: str, prompt: str, verbose: bool = False) -> str:
    """
    Get response from Gemini AI model
    """
    try:
        # Debug: List available models
        print("Available models:")
        for model in genai.list_models():
            print(f"- {model.name}")
            
        # Create model instance
        model = genai.GenerativeModel('gemini-pro')
        # model=genai.GenerativeModel('gemini-1.5-pro')
        # print([print(model) for model in genai.list_models()])
        # Prepare content parts
        
        content = prompt + "\n\n"
        if input:
            content += "Job Description:\n" + input + "\n\n"
        content += "Resume:\n" + pdf_content
        
        # Generate response with appropriate configuration
        response = model.generate_content(
            content,
            generation_config=genai.types.GenerationConfig(
                temperature=settings.GEMINI_TEMPERATURE
            ),
            safety_settings=GEMINI_SAFETY_SETTINGS
        )
        
        if response.prompt_feedback:
            if verbose:
                print("Prompt feedback:", response.prompt_feedback)
            
        if not response.text:
            return "Error: No response generated from AI model"
            
        return response.text
        
    except Exception as e:
        if verbose:
            print(f"Error in Gemini API call: {str(e)}")
        return f"Error with Gemini AI Model: {str(e)}" 