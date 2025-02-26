import spacy
from typing import List

RESUME_SECTIONS = [
    'summary',
    'education',
    'experience',
    'skills',
    'projects',
    'certifications',
    'licenses',
    'awards',
    'honors',
    'publications',
    'references',
]

def clean_text(tokens) -> List:
    """Clean text by removing punctuation, spaces and stop words"""
    return [token for token in tokens if (not token.is_punct and not token.is_space and not token.is_stop)]

def extract_section(doc, section_names: List[str], extract_nouns_only: bool = False) -> str:
    """
    Generic function to extract a section from the resume
    
    Args:
        doc: Spacy doc object
        section_names: List of possible section names
        extract_nouns_only: Whether to extract only nouns and proper nouns
    """
    section_content = []
    in_section = False
    pos_tags = ['NOUN', 'PROPN'] if extract_nouns_only else None

    for token in doc:
        if token.text.lower() in RESUME_SECTIONS and token.text not in RESUME_SECTIONS:
            if any(token.text.upper() == name.upper() for name in section_names):
                in_section = True
            else:
                in_section = False

        if in_section:
            if pos_tags is None or token.pos_ in pos_tags:
                section_content.append(token.text)

    return ' '.join(section_content)

def resume_parser(resume: str) -> str:
    """
    Parse resume text and extract relevant sections
    
    Args:
        resume: Raw text from PDF resume
    
    Returns:
        Processed resume text with extracted sections
    """
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(resume)
    doc = clean_text(doc)

    # Extract sections
    summary = extract_section(doc, ['Summary', 'SUMMARY'])
    skills = extract_section(doc, ['Skills', 'SKILLS', 'Skill', 'SKILL'])
    experience = extract_section(doc, ['Experience', 'EXPERIENCE', 'Projects', 'PROJECTS'])
    education = extract_section(doc, ['Education', 'EDUCATION'], extract_nouns_only=True)

    result = '\n'.join([summary, skills, experience, education])
    return result.lower() 