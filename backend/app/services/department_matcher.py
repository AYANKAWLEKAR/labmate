from typing import List, Optional, Dict
from bert_score import score as bert_score


DEPARTMENT_CATALOG: List[Dict[str, str]] = [
    {
        "institution": "Rutgers",
        "department": "Computer Science",
        "url": "https://www.cs.rutgers.edu/people/professors",
        "keywords": "computer science cs programming software algorithms ai machine learning data systems",
    }
]


def match_research_interests_to_department(
    research_interests: List[str], institution: str
) -> Optional[str]:
    """
    Match research interests to a department URL using semantic similarity.
    Returns the department URL if a match is found, otherwise None.
    """
    if not research_interests:
        return None

    interests_text = " ".join([interest.strip() for interest in research_interests if interest.strip()])
    if not interests_text:
        return None

    candidates = [d for d in DEPARTMENT_CATALOG if d["institution"] == institution]
    if not candidates:
        return None

    # Use BERTScore for semantic matching
    try:
        candidate_texts = [c["keywords"] for c in candidates]
        _, _, f1 = bert_score(
            cands=[interests_text] * len(candidate_texts),
            refs=candidate_texts,
            lang="en",
            verbose=False,
            rescale_with_baseline=True,
        )
        best_idx = int(f1.argmax().item())
        best_score = float(f1[best_idx].item())
        # Simple threshold to avoid weak matches
        if best_score < 0.2:
            return None
        return candidates[best_idx]["url"]
    except Exception:
        # Fallback to keyword matching if BERTScore fails
        interests_lower = interests_text.lower()
        for candidate in candidates:
            if any(keyword in interests_lower for keyword in candidate["keywords"].split()):
                return candidate["url"]

    return None
