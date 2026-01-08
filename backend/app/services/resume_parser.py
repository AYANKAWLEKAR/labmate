import re
import fitz  # PyMuPDF
import spacy
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from dataclasses import dataclass
import base64
import json


@dataclass
class ParsedResume:
    """Data class for parsed resume content"""
    skills_section: str
    experience_section: str
    skills_raw_text: List[str]
    experience_raw_text: List[str]
    all_sections: Dict[str, str]
    section_mapping: Dict[str, str]  # Detected section name -> normalized type


class ResumeParser:
  
    
    def __init__(self):
        """Initialize parser with spaCy model for NLP processing"""
        # Load English model for NLP
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("⚠️  spaCy model not found. Installing...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"], 
                         capture_output=True)
            self.nlp = spacy.load("en_core_web_sm")
        
        # Keywords for section identification
        self.skills_keywords = {
            'skills', 'technical skills', 'core competencies', 'competencies',
            'technologies', 'tools', 'programming', 'languages', 'expertise',
            'capabilities', 'proficiencies', 'technical expertise', 'toolbox'
        }
        
        self.experience_keywords = {
            'experience', 'work experience', 'professional experience',
            'employment', 'career', 'work history', 'positions',
            'professional background', 'internships', 'internship',
            'projects', 'professional experience', 'roles'
        }
        
        self.education_keywords = {
            'education', 'academic', 'degree', 'qualification',
            'university', 'college', 'school', 'credentials'
        }
        
        # TF-IDF vectorizer for semantic similarity
        self.tfidf_vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words='english',
            ngram_range=(1, 2)
        )
    
    def extract_text_from_pdf(self, file) -> Tuple[str, Dict]:
        """
        Extract text from PDF file-like object with structure preservation.
        
        Args:
            file: a file-like object containing the PDF (e.g., from Flask's request.files["file"])
            
        Returns:
            Tuple of (full_text, block_info with positions)
        """
        # Read from file object (buffer), fitz can read from bytes
        file.seek(0)
        pdf_document = fitz.open(stream=file.read(), filetype="pdf")
        full_text = ""
        block_info = defaultdict(list)
        
        # Extract text block by block to preserve structure
        for page_num, page in enumerate(pdf_document):
            # Get text blocks with bounding boxes
            blocks = page.get_text("blocks")
            
            for block in blocks:
                if block[4]:  # Text block (not image)
                    text = block[4].strip()
                    if text:
                        # Store text with vertical position (Y-coordinate)
                        # Y-coordinate helps identify section hierarchy
                        y_position = block[1]
                        block_info[y_position].append(text)
                        full_text += text + "\n"
        
        pdf_document.close()
        return full_text, block_info

    def split_into_sections(self, text: str) -> Dict[str, str]:
        """
        Split resume text into logical sections.
        
        Uses regex to identify section headers (usually capitalized lines
        with minimal content followed by content).
        
        Args:
            text: Full resume text
            
        Returns:
            Dictionary mapping section names to section content
        """
        sections = {}
        
        # Regex to identify section headers
        # Matches lines that are: all caps/title case, relatively short, 
        # followed by content
        section_pattern = r'^([A-Z][A-Z\s\-&]+?):\s*$|^([A-Z][A-Z\s\-&]+)\s*$'
        
        # Split by potential headers
        lines = text.split('\n')
        current_section = "HEADER"
        current_content = []
        
        for line in lines:
            # Check if line is a section header
            if self._is_section_header(line):
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                current_section = line.strip()
                current_content = []
            else:
                # Add to current section if not empty
                if line.strip():
                    current_content.append(line)
        
        # Don't forget last section
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def _is_section_header(self, line: str) -> bool:
        """
        Determine if a line is likely a section header.
        
        Heuristics:
        - Short line (< 50 chars)
        - Mostly uppercase or title case
        - No special characters (except hyphen, &, spaces)
        - Not a date or number
        """
        line = line.strip()
        
        if not line or len(line) > 50:
            return False
        
        # Check if mostly uppercase or title case
        upper_ratio = sum(1 for c in line if c.isupper()) / len([c for c in line if c.isalpha()])
        if upper_ratio < 0.6:
            return False
        
        # Exclude pure numbers and dates
        if re.match(r'^\d+.*\d+$', line):
            return False
        
        return True
    
    def identify_section_type(self, section_name: str, section_content: str) -> str:
      
        section_name_lower = section_name.lower()
        
        # Direct keyword matching (highest confidence)
        for keyword in self.skills_keywords:
            if keyword in section_name_lower:
                return "SKILLS"
        
        for keyword in self.experience_keywords:
            if keyword in section_name_lower:
                return "EXPERIENCE"
        
        for keyword in self.education_keywords:
            if keyword in section_name_lower:
                return "EDUCATION"
        
        # Semantic similarity fallback
        section_type = self._semantic_section_matching(section_name, section_content)
        return section_type
    
    def _semantic_section_matching(self, section_name: str, section_content: str) -> str:
        """
        Use NLP-based semantic similarity to match section type.
        
        Compares section header to known keyword sets using spaCy word vectors.
        Falls back to content analysis if header is unclear.
        """
        # Use spaCy to process section name
        doc_name = self.nlp(section_name.lower())
        
        if not doc_name.has_vector:
            # If no vector, use simple keyword matching fallback
            return self._content_based_matching(section_name, section_content)
        
        # Calculate similarity to keyword sets
        skills_doc = self.nlp(" ".join(self.skills_keywords))
        experience_doc = self.nlp(" ".join(self.experience_keywords))
        
        skills_sim = doc_name.similarity(skills_doc)
        experience_sim = doc_name.similarity(experience_doc)
        
        if skills_sim > experience_sim and skills_sim > 0.3:
            return "SKILLS"
        elif experience_sim > 0.3:
            return "EXPERIENCE"
        else:
            # Analyze content if header is ambiguous
            return self._content_based_matching(section_name, section_content)
    
    def _content_based_matching(self, section_name: str, section_content: str) -> str:
        """
        Analyze section content to infer type.
        
        Heuristics:
        - Skills: Short lines, technical terms, comma/slash separation
        - Experience: Company names, dates, bullet points, descriptions
        """
        lines = [l.strip() for l in section_content.split('\n') if l.strip()]
        
        # Check for common patterns
        # Skills often have: bullet points with short items, commas, slashes
        skill_indicators = 0
        experience_indicators = 0
        
        for line in lines:
            # Skills patterns: comma-separated, slash-separated, short
            if ',' in line or '/' in line or (len(line) < 60 and not re.search(r'\d{4}', line)):
                skill_indicators += 1
            
            # Experience patterns: dates, action verbs, company names
            if re.search(r'\d{4}', line):  # Years
                experience_indicators += 1
            if re.search(r'\b(developed|managed|led|designed|implemented)\b', line.lower()):
                experience_indicators += 1
        
        if skill_indicators > experience_indicators:
            return "SKILLS"
        elif experience_indicators > 0:
            return "EXPERIENCE"
        else:
            return "OTHER"
    
    def extract_skills(self, text: str) -> List[str]:
      
        if not text:
            return []
        
        # Remove bullet points and special characters
        text = re.sub(r'^[\s•\-\*]+', '', text, flags=re.MULTILINE)
        
        # Split by common delimiters
        if ',' in text:
            # Comma-separated
            skills = [s.strip() for s in text.split(',')]
        elif '/' in text and '\n' not in text:
            # Slash-separated (but not mixed with newlines)
            skills = [s.strip() for s in text.split('/')]
        else:
            # Line-separated or mixed
            skills = [s.strip() for s in text.split('\n') if s.strip()]
        
        # Clean and filter
        skills = [s for s in skills if s and len(s) < 100]
        return skills
    
    def extract_experiences(self, text: str) -> List[str]:
        """
        Extract individual experience entries from experience section.
        
        Handles multiple formats:
        - Structured: "Company | Position | Date\nDescription"
        - Bullet format: "Position at Company (Date)\n• Responsibility"
        - Free-form: Paragraphs with job information
        
        Args:
            text: Experience section text
            
        Returns:
            List of experience entries
        """
        if not text:
            return []
        
        experiences = []
        
        # Split by common delimiters (date patterns, position indicators)
        # Split by lines starting with capital letters (likely new entry)
        entries = re.split(r'\n(?=[A-Z])', text)
        
        for entry in entries:
            entry = entry.strip()
            if entry and len(entry) > 20:  # Filter short entries
                experiences.append(entry)
        
        return experiences
    
    def parse(self, pdf_file) -> ParsedResume:
        """
        Main parsing pipeline.

        Args:
            pdf_file: File-like object representing the uploaded resume PDF

        Returns:
            ParsedResume object with extracted information
        """
        print(f"📄 Parsing resume: {getattr(pdf_file, 'filename', str(pdf_file))}")

        # Step 1: Extract text from PDF
        # Assumes self.extract_text_from_pdf can handle file-like objects
        full_text, block_info = self.extract_text_from_pdf(pdf_file)
        print(f"✓ Extracted text ({len(full_text)} characters)")
        
        # Step 2: Split into sections
        sections = self.split_into_sections(full_text)
        print(f"✓ Identified {len(sections)} sections")
        
        # Step 3: Identify section types
        section_mapping = {}
        skills_section_name = None
        experience_section_name = None
        skills_text = ""
        experience_text = ""
        
        for section_name, section_content in sections.items():
            section_type = self.identify_section_type(section_name, section_content)
            section_mapping[section_name] = section_type
            
            print(f"  → {section_name}: {section_type}")
            
            if section_type == "SKILLS":
                skills_section_name = section_name
                skills_text = section_content
            elif section_type == "EXPERIENCE":
                experience_section_name = section_name
                experience_text = section_content
        
        # Step 4: Extract structured data
        skills = self.extract_skills(skills_text)
        experiences = self.extract_experiences(experience_text)
        
        print(f"✓ Extracted {len(skills)} skills")
        print(f"✓ Extracted {len(experiences)} experience entries")
        
        return ParsedResume(
            skills_section=skills_section_name or "NOT FOUND",
            experience_section=experience_section_name or "NOT FOUND",
            skills_raw_text=skills,
            experience_raw_text=experiences,
            all_sections=sections,
            section_mapping=section_mapping
        )


def print_results(result: ParsedResume) -> None:
    """Pretty print parsing results"""
    print("\n" + "="*80)
    print("RESUME PARSING RESULTS")
    print("="*80)
    
    print(f"\n📌 SKILLS SECTION: {result.skills_section}")
    print("-" * 40)
    if result.skills_raw_text:
        for i, skill in enumerate(result.skills_raw_text, 1):
            print(f"  {i}. {skill}")
    else:
        print("  No skills found")
    
    print(f"\n💼 EXPERIENCE SECTION: {result.experience_section}")
    print("-" * 40)
    if result.experience_raw_text:
        for i, exp in enumerate(result.experience_raw_text, 1):
            print(f"\n  Experience {i}:")
            # Print first 200 chars of each experience
            preview = exp[:200].replace('\n', ' ')
            print(f"    {preview}...")
    else:
        print("  No experiences found")
    
    print(f"\n📑 ALL SECTIONS DETECTED:")
    print("-" * 40)
    for section_name, section_type in result.section_mapping.items():
        print(f"  • {section_name} → {section_type}")



async def parse_resume(pdf_bytes: bytes, user_id: str) -> ParsedResume:
    """
    Parse resume PDF and extract structured information.
    Saves the parsed resume data to the database for the given user.
    
    Args:
        pdf_bytes: PDF file bytes
        user_id: User ID to associate the resume with
    
    Returns:
        ParsedResume object with extracted information
    """
    from ..db import get_prisma
    
    parser = ResumeParser()
    
    # Create a file-like object from bytes for parsing
    from io import BytesIO
    pdf_file = BytesIO(pdf_bytes)
    
    # Parse the resume (parse() internally calls extract_text_from_pdf)
    parsed_resume = parser.parse(pdf_file)
    print_results(parsed_resume)
    
    # Encode PDF as base64 for storage
    rawpdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
    
    # Prepare experiences as JSON
    experiences_json = json.dumps(parsed_resume.experience_raw_text) if parsed_resume.experience_raw_text else None
    
    # Save to database using Prisma
    prisma = await get_prisma()
    
    # Check if user already has a resume, update or create
    existing_resume = await prisma.resume.find_unique(where={"userId": user_id})
    
    if existing_resume:
        # Update existing resume
        await prisma.resume.update(
            where={"id": existing_resume.id},
            data={
                "rawpdf": rawpdf_base64,
                "skills": parsed_resume.skills_raw_text,
                "experiences": experiences_json,
            }
        )
    else:
        # Create new resume
        await prisma.resume.create(
            data={
                "rawpdf": rawpdf_base64,
                "skills": parsed_resume.skills_raw_text,
                "experiences": experiences_json,
                "userId": user_id,
            }
        )
    
    return parsed_resume
