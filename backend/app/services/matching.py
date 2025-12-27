import pandas as pd
from bert_score import score
from typing import Dict, List
import torch
from resume_parser import ParsedResume


def create_resume_text(resume: ParsedResume) -> str:
    """Create a concatenated text representation of the resume."""
    skills = " ".join(resume.skills_section)
    
    experiences = " ".join(resume.experience_section)
    
    return f"skills: {skills}  experiences: {experiences}".strip()


def create_professor_text(professor_row: pd.Series) -> str:
    """Create a concatenated text representation of a professor."""
    name = professor_row.get("name", "")
    department = professor_row.get("department", "")
    research = professor_row.get("research_focus", "")
    lab_group = professor_row.get("lab_group", "") or ""
    
    return f"{name} {department} {research} {lab_group}".strip()


def rank_professors(
    resume_profile: ParsedResume, professors_df: pd.DataFrame, top_k: int = 3
) -> List[Dict]:
    """
    Rank professors by semantic similarity to resume using BERTScore.
    
    Args:
        resume_profile: Parsed resume dictionary
        professors_df: DataFrame with professor information
        top_k: Number of top matches to return
    
    Returns:
        List of top_k professor dictionaries
    """
    if professors_df.empty:
        return []
    
    # Create reference text from resume
    resume_text= create_resume_text(resume_profile)
    
  
    
    # Create candidate texts from professors
    candidate_texts = [
        create_professor_text(row) for _, row in professors_df.iterrows()
    ]
    
    if not candidate_texts or not any(c.strip() for c in candidate_texts):
        return []
    
    try:
        # Compute BERTScore
        # Use CPU if CUDA not available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        P, R, F1 = score(
            cands=candidate_texts,
            refs=[resume_text] * len(candidate_texts),
            lang="en",
            verbose=False,
            device=device,
            rescale_with_baseline=True,
        )
        
        # Use F1 score for ranking
        similarity_scores = F1.cpu().numpy()
        
    except Exception as e:
        print(f"BERTScore computation failed: {e}")
        # Fallback: simple keyword matching
        resume_lower = resume_text.lower()
        similarity_scores = [
            sum(1 for word in cand.lower().split() if word in resume_lower)
            for cand in candidate_texts
        ]
        similarity_scores = [float(s) / max(len(c.split()), 1) for s, c in zip(similarity_scores, candidate_texts)]
    
    # Add similarity scores to dataframe
    professors_df = professors_df.copy()
    professors_df["similarity"] = similarity_scores
    
    # Sort by similarity (descending)
    professors_df = professors_df.sort_values("similarity", ascending=False)
    
    # Get top k
    top_professors = professors_df.head(top_k)
    
    # Convert to list of dictionaries
    result = []
    for _, row in top_professors.iterrows():
        result.append({
            "id": str(row.get("id", "")),
            "name": str(row.get("name", "")),
            "institution": str(row.get("institution", "")),
            "department": str(row.get("department", "")),
            "research_focus": str(row.get("research_focus", "")),
            "lab_group": str(row.get("lab_group", "")) if pd.notna(row.get("lab_group")) else None,
            "profile_url": str(row.get("profile_url", "")) if pd.notna(row.get("profile_url")) else None,
        })
    
    return result

