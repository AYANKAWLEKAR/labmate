from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

from .services.resume_parser import parse_resume
from .services.scraper import scrape_institutions
from .services.matching import rank_professors
from .services.email_generator import generate_cold_email
from .db import get_prisma, close_prisma

load_dotenv()

app = FastAPI(title="Labmate API", version="1.0.0")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup Logic ---
    """Initialize Prisma connection on startup."""
    await get_prisma()
    
    yield  # The app runs while this yield is active
    
    # --- Shutdown Logic ---
    """Close Prisma connection on shutdown."""
    await close_prisma()

app = FastAPI(title="Labmate API", version="1.0.0", lifespan=lifespan)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_INSTITUTIONS = [
    "Rutgers",
    "NJIT",
    "Princeton",
    "Stevens Institute of Technology",
    "TCNJ",
    "Seton Hall",
]


class Professor(BaseModel):
    id: str
    name: str
    institution: str
    department: str
    research_focus: str
    lab_group: Optional[str] = None
    profile_url: Optional[str] = None


class MatchResponse(BaseModel):
    resume_profile: dict
    top_professors: List[Professor]


class EmailRequest(BaseModel):
    resume_profile: dict
    professor: Professor
    user_name: str


class EmailResponse(BaseModel):
    email_text: str


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/match", response_model=MatchResponse)
async def match_professors(
    institutions: List[str] = Query(..., description="List of institutions to search"),
    resume: UploadFile = File(..., description="Resume PDF file"),
    user_id: Optional[str] = Header(None, alias="X-User-Id", description="User ID from session"),
):
    """
    Match user's resume with professors from selected institutions.
    Returns top 3 matches ranked by semantic similarity.
    Also saves the parsed resume to the database if user_id is provided.
    """
    # Validate institutions
    invalid = [inst for inst in institutions if inst not in ALLOWED_INSTITUTIONS]
    if invalid:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid institutions: {invalid}. Allowed: {ALLOWED_INSTITUTIONS}",
        )

    # Read resume file
    resume_bytes = await resume.read()
    if not resume_bytes:
        raise HTTPException(status_code=400, detail="Resume file is empty")

    # Parse resume and save to database if user_id is provided
    try:
        if user_id:
            resume_profile = await parse_resume(resume_bytes, user_id)
        else:
            # Fallback: parse without saving to database
            from io import BytesIO
            from .services.resume_parser import ResumeParser
            parser = ResumeParser()
            pdf_file = BytesIO(resume_bytes)
            resume_profile = parser.parse(pdf_file)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to parse resume: {str(e)}"
        )

    # Scrape institutions
    try:
        professors_df = await scrape_institutions(institutions)
        if professors_df.empty:
            raise HTTPException(
                status_code=500,
                detail="No professors found. Scraping may have failed.",
            )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to scrape institutions: {str(e)}"
        )

    # Rank professors
    try:
        top_professors = rank_professors(resume_profile, professors_df, top_k=3)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to rank professors: {str(e)}"
        )

    return MatchResponse(
        resume_profile=resume_profile,
        top_professors=[Professor(**prof) for prof in top_professors],
    )


@app.post("/generate_email", response_model=EmailResponse)
async def generate_email(payload: EmailRequest):
    """
    Generate a personalized cold email for the selected professor.
    """
    try:
        email_text = await generate_cold_email(
            resume_profile=payload.resume_profile,
            professor=payload.professor.model_dump(),
            user_name=payload.user_name,
        )
        return EmailResponse(email_text=email_text)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate email: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

