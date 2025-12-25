import fitz  # PyMuPDF
import spacy
from typing import Dict, List
import re


def load_spacy_model():
    """Load spaCy model, fallback to blank if not available."""
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        # Fallback to blank English model
        nlp = spacy.blank("en")
        nlp.add_pipe("sentencizer")
        return nlp


nlp = load_spacy_model()


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract text from PDF using PyMuPDF."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


def extract_skills(text: str) -> List[str]:
    """Extract skills using spaCy noun chunks and keyword patterns."""
    doc = nlp(text)
    skills = []
    
    # Common technical skills patterns
    skill_keywords = [
        "python", "java", "javascript", "c++", "r", "matlab", "sql",
        "machine learning", "data analysis", "statistics", "research",
        "laboratory", "experiment", "publication", "presentation",
        "latex", "git", "linux", "statistical analysis", "data visualization"
    ]
    
    # Extract noun phrases that might be skills
    for chunk in doc.noun_chunks:
        chunk_text = chunk.text.lower()
        if any(keyword in chunk_text for keyword in skill_keywords):
            if chunk_text not in skills:
                skills.append(chunk_text)
    
    # Also look for capitalized technical terms
    for token in doc:
        if token.is_upper and len(token.text) > 2:
            if token.text.lower() not in skills:
                skills.append(token.text.lower())
    
    return skills[:15]  # Limit to top 15


def extract_interests(text: str) -> List[str]:
    """Extract research interests from resume text."""
    doc = nlp(text)
    interests = []
    
    # Look for sections that might contain interests
    interest_keywords = [
        "interest", "research interest", "focus", "specialization",
        "field", "area", "domain", "topic"
    ]
    
    sentences = [sent.text for sent in doc.sents]
    for sent in sentences:
        sent_lower = sent.lower()
        if any(keyword in sent_lower for keyword in interest_keywords):
            # Extract meaningful phrases from these sentences
            sent_doc = nlp(sent)
            for chunk in sent_doc.noun_chunks:
                if len(chunk.text) > 5 and chunk.text.lower() not in interests:
                    interests.append(chunk.text)
    
    return interests[:10]  # Limit to top 10


def extract_experiences(text: str) -> List[str]:
    """Extract work/research experiences from resume."""
    doc = nlp(text)
    experiences = []
    
    # Look for experience indicators
    exp_keywords = [
        "experience", "worked", "research", "intern", "assistant",
        "project", "publication", "presented", "collaborated"
    ]
    
    sentences = [sent.text for sent in doc.sents]
    for sent in sentences:
        sent_lower = sent.lower()
        if any(keyword in sent_lower for keyword in exp_keywords):
            # Clean and extract meaningful experience descriptions
            cleaned = re.sub(r'\s+', ' ', sent.strip())
            if len(cleaned) > 20 and cleaned not in experiences:
                experiences.append(cleaned[:200])  # Limit length
    
    return experiences[:8]  # Limit to top 8


def parse_resume(pdf_bytes: bytes) -> Dict:
    """
    Parse resume PDF and extract structured information.
    
    Returns:
        {
            "raw_text": str,
            "skills": List[str],
            "interests": List[str],
            "experiences": List[str]
        }
    """
    # Extract raw text
    raw_text = extract_text_from_pdf(pdf_bytes)
    
    if not raw_text.strip():
        raise ValueError("No text extracted from PDF")
    
    # Extract structured information
    skills = extract_skills(raw_text)
    interests = extract_interests(raw_text)
    experiences = extract_experiences(raw_text)
    
    return {
        "raw_text": raw_text[:5000],  # Limit raw text length
        "skills": skills,
        "interests": interests,
        "experiences": experiences,
    }
