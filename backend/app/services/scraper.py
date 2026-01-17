import pandas as pd
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import asyncio
import re
from urllib.parse import urljoin
from datetime import datetime, timezone
from dotenv import load_dotenv
from llama_index.core import SummaryIndex, Settings
from llama_index.readers.web import SimpleWebPageReader
from llama_index.llms.groq import Groq
import os

from .department_matcher import match_research_interests_to_department
from ..db import get_prisma

load_dotenv()

# Load GROQ API key from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# Institution-specific scraping configurations
INSTITUTION_CONFIGS = {
    "Rutgers": {
        "base_url": " https://www.cs.rutgers.edu/people/professors",
        "method": "beautifulsoup",  # or "selenium"
        "selectors": {
            "professor_container": "div.faculty-member",
            "name": "h3, h4, .name",
            "department": ".department, .dept",
            "research": ".research, .interests, .focus",
            "profile_link": "a",
        },
    },

    "Princeton": {
        "base_url": "https://www.cs.princeton.edu/people/faculty",
        "method": "beautifulsoup",
        "selectors": {
            "professor_container": "div.faculty, div.person",
            "name": "h2, h3",
            "department": ".department",
            "research": ".research, .interests",
            "profile_link": "a",
        },
    },

    "TCNJ": {
        "base_url": "https://computerscience.tcnj.edu/faculty-profiles/",
        "method": "beautifulsoup",
        "selectors": {
            "professor_container": "div.faculty, article",
            "name": "h2, h3",
            "department": ".department",
            "research": ".research, .interests",
            "profile_link": "a",
        },
    },

    }

MODEL_NAME="llama-3.1-8b-instant"

SUMMARY_PROMPT="""

You are a helpful assistant that summarizes research lab or professor's personal websites.
Identify any distinct projects that this research lab or professor is working on and their main focus.
This includes past publications
Return a concise summary of the projects with important details. Return in a list format.

"""




class Scraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        self.client = httpx.AsyncClient(timeout=30.0, headers=self.headers)

    async def find_projects_from_website(self, url: str) -> str:
        print(f"\n[DEBUG] find_projects_from_website called with URL: {url}")
        
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set")

        try:
            # Run synchronous llama_index operations in thread pool
            def _process_website():
                llm = Groq(
                    model=MODEL_NAME,
                    temperature=0.1,
                    api_key=GROQ_API_KEY
                )
                Settings.llm = llm

                print(f"[DEBUG] Loading documents from URL...")
                documents = SimpleWebPageReader(html_to_text=True).load_data([url])
                print(f"[DEBUG] Documents loaded: {len(documents)} documents")
                
                index = SummaryIndex(documents, show_progress=True)
                query_engine = index.as_query_engine(response_mode="tree_summarize")
                summary = query_engine.query(SUMMARY_PROMPT)
                return summary
            
            summary = await asyncio.to_thread(_process_website)
            print(f"[DEBUG] Summary generated successfully")
            return str(summary)
        except Exception as e:
            print(f"[ERROR] find_projects_from_website failed: {type(e).__name__}: {e}")
            return ""

    async def scrapeRutgers(self, method: str = "beautifulsoup", department_url: Optional[str] = None) -> List[Dict]:
        print(f"\n[DEBUG] Starting scrapeRutgers with method: {method}")

        async def scrape_labs(groups: List[str]) -> tuple:
            print(f"\n[DEBUG] scrape_labs called with {len(groups)} groups")
            research_focus = []
            assosciated_labs = []
            
            for idx, lab in enumerate(groups[:1]):
                print(f"[DEBUG] Processing lab {idx + 1}/{len(groups[:1])}: {lab}")
                try:
                    response = await self.client.get(lab)
                    response.raise_for_status()
                    print(f"[DEBUG] Lab page loaded successfully")
                    
                    lab_parser = BeautifulSoup(response.text, "html.parser")
                    body = lab_parser.find("div", class_="article-body")
                    
                    if body is None:
                        print(f"[WARNING] No div with class 'article-body' found for lab: {lab}")
                        continue
                    
                    print(f"[DEBUG] Found article-body div")
                    all_labs_header = body.find_all("h2")
                    
                    if not all_labs_header:
                        print(f"[WARNING] No h2 tags found in article-body for lab: {lab}")
                        continue
                    
                    print(f"[DEBUG] Found {len(all_labs_header)} h2 tags")
                    last_header = all_labs_header[-1]
                    lab_ps = last_header.find_next_siblings("p")
                    print(f"[DEBUG] Found {len(lab_ps)} p tags after last h2")
                    
                    for p_idx, p in enumerate(lab_ps):
                        link = p.find("a", href=True)
                        if link:
                            lab_name = link.text.strip()
                            lab_href = link["href"]
                            print(f"[DEBUG] Found lab link {p_idx + 1}: {lab_name} -> {lab_href}")
                            assosciated_labs.append(lab_name)
                            research_focus = await self.find_projects_from_website(lab_href)
                        else:
                            print(f"[DEBUG] No link found in p tag {p_idx + 1}")
                            
                except Exception as e:
                    print(f"[ERROR] Failed to scrape lab {lab}: {type(e).__name__}: {e}")
                    
            return research_focus, assosciated_labs

        professors = []
        base_url = "https://www.cs.rutgers.edu/"
        faculty_url = department_url or "https://www.cs.rutgers.edu/people/professors"
        
        if method == "beautifulsoup":
            print(f"\n[DEBUG] Fetching faculty page: {faculty_url}")
            
            try:
                response = await self.client.get(faculty_url)
                response.raise_for_status()
                print(f"[DEBUG] Faculty page loaded successfully")
            except Exception as e:
                print(f"[ERROR] Failed to load faculty page: {type(e).__name__}: {e}")
                return professors

            link_parser = BeautifulSoup(response.text, "html.parser")
            all_links = set()
            
            for link in link_parser.find_all("a", href=True):
                href = link['href']
                if "/people/professors/details/" in href:
                    full_url = urljoin(base_url, href)
                    all_links.add(full_url)
            
            print(f"[DEBUG] Found {len(all_links)} professor profile links")
            
            prisma = await get_prisma()
            for link_idx, link in enumerate(all_links, 1):
                print(f"\n[DEBUG] ===== Processing professor {link_idx}/{len(all_links)} =====")
                print(f"[DEBUG] Profile URL: {link}")
                
                name = None
                website = None
                groups = []
                description = None

                try:
                    response = await self.client.get(link)
                    response.raise_for_status()
                    print(f"[DEBUG] Professor page loaded successfully")
                except Exception as e:
                    print(f"[ERROR] Failed to load professor page: {type(e).__name__}: {e}")
                    continue

                prof_parser = BeautifulSoup(response.text, "html.parser")
                values_list = prof_parser.find("ul", class_="fields-container")
                
                if values_list is None:
                    print(f"[WARNING] No ul with class 'fields-container' found")
                    continue
                
                print(f"[DEBUG] Found fields-container ul")
                
                for li in values_list.find_all("li"):
                    li_class = li.get("class",[])
                    print(f"[DEBUG] Processing li... elements found: {len(li_class)}...")
                    has_name=False
                    for c in li_class:
                      
                      if "name" in c.lower():
                          field_value = li.find("span", "field-value")
                          if field_value is None:
                              print(f"[WARNING] 'name' field found but no span with class 'field-value'")
                          else:
                              name = field_value.text.strip()
                              print(f"[DEBUG] Found name: {name}")
                      
                      elif "website" in c.lower():
                          field_value = li.find("span", "field-value")

                          if field_value is None:
                              print(f"[WARNING] 'website' field found but no span with class 'field-value'")
                          else:
                              weblink = field_value.find("a",href=True)
                              website=weblink["href"]
                              print(f"[DEBUG] Found website: {website}")
                      
                      elif "groups" in c.lower():
                          list_groups = li.find_all("a",href=True)
                          print(f"[DEBUG] Found {len(list_groups)} group links")
                          for group in list_groups:
                              group_text = group["href"]
                              groups.append(group_text)
                              print(f"[DEBUG] Added group: {group_text}")
                      

                
                # Find description
                paragraphs_after_ul = []
                for sibling in values_list.find_next_siblings():
                    if sibling.name == "p":
                        paragraphs_after_ul.append(sibling)
                
                if paragraphs_after_ul:
                    description = " ".join([p.get_text(strip=True) for p in paragraphs_after_ul])
                    print(f"[DEBUG] Found description: {description[:100]}...")
                else:
                    print(f"[DEBUG] No description paragraphs found")
                
                if name:
                    cached_professor = await prisma.professor.find_first(
                        where={
                            "name": name,
                            "department": "Computer Science",
                            "institution": "Rutgers",
                        }
                    )
                    if cached_professor:
                        print(f"[DEBUG] Professor cached, skipping scrape: {name}")
                        professors.append({
                            "name": cached_professor.name,
                            "assosciated_labs": cached_professor.labGroup.split(", ") if cached_professor.labGroup else [],
                            "raw_research_focus": cached_professor.researchFocus,
                        })
                        await asyncio.sleep(0.1)
                        continue

                    print(f"[DEBUG] Processing professor: {name}")
                    
                    if website:
                        print(f"[DEBUG] Professor has website: {website}")
                        if groups:
                            print(f"[DEBUG] Professor has groups, scraping labs...")
                            research_focus, assosciated_labs = await scrape_labs(groups)
                            professors.append({
                                "name": name,
                                "assosciated_labs": assosciated_labs,
                                "raw_research_focus": research_focus
                            })
                        else:
                            print(f"[DEBUG] No groups, scraping website directly...")
                            research_focus = await self.find_projects_from_website(website)
                            professors.append({
                                "name": name,
                                "assosciated_labs": [],
                                "raw_research_focus": research_focus
                            })
                    else:
                        print(f"[DEBUG] Professor has no website")
                        if groups:
                            print(f"[DEBUG] Has groups, scraping labs...")
                            research_focus, assosciated_labs = await scrape_labs(groups)
                            professors.append({
                                "name": name,
                                "assosciated_labs": assosciated_labs,
                                "raw_research_focus": research_focus
                            })
                        elif description:
                            print(f"[DEBUG] Using description as research focus")
                            research_focus = description
                            professors.append({
                                "name": name,
                                "assosciated_labs": [],
                                "raw_research_focus": research_focus
                            })
                        else:
                            print(f"[WARNING] Professor has no website, groups, or description - skipping")
                            continue
                    
                    print(f"[DEBUG] Added professor: {name}")
                else:
                    print(f"[WARNING] No name found for professor - skipping")
                    continue
                
                await asyncio.sleep(1)  # Rate limiting
                print(f"[DEBUG] Total professors collected so far: {len(professors)}")

        print(f"\n[DEBUG] ===== scrapeRutgers completed =====")
        print(f"[DEBUG] Total professors collected: {len(professors)}")
        return professors

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()


# Async function to scrape institutions and return DataFrame
async def scrape_institutions(institutions: List[str], research_interests: List[str]) -> pd.DataFrame:
    """
    Scrape professors from specified institutions.
    Currently only supports Rutgers.
    
    Args:
        institutions: List of institution names to scrape
        
    Returns:
        pandas DataFrame with columns: id, name, institution, department, research_focus, lab_group, profile_url
    """
    async with Scraper() as scraper:
        all_professors = []
        prisma = await get_prisma()

        for institution in institutions:
            if institution != "Rutgers":
                print(f"[WARNING] Institution '{institution}' not yet supported. Only 'Rutgers' is supported.")
                continue

            department_url = match_research_interests_to_department(research_interests, institution)
            if not department_url:
                print("[WARNING] No department match found for research interests.")
                continue

            cached_department = await prisma.department.find_unique(
                where={"url": department_url},
                include={"professors": True},
            )

            if cached_department:
                for prof in cached_department.professors:
                    all_professors.append({
                        "id": prof.id,
                        "name": prof.name,
                        "institution": prof.institution,
                        "department": prof.department,
                        "research_focus": prof.researchFocus,
                        "lab_group": prof.labGroup,
                        "profile_url": prof.profileUrl,
                    })
                continue

            professors = await scraper.scrapeRutgers(method="beautifulsoup", department_url=department_url)

            department_record = await save_department_to_db(
                institution=institution,
                department_name="Computer Science",
                url=department_url,
            )

            for prof in professors:
                research_focus = str(prof.get("raw_research_focus", ""))
                if hasattr(research_focus, "response"):
                    research_focus = str(research_focus.response) if hasattr(research_focus, "response") else str(research_focus)

                professor_record = await save_professor_to_db(
                    professor_data={
                        "name": prof.get("name", ""),
                        "institution": "Rutgers",
                        "department": "Computer Science",
                        "research_focus": research_focus,
                        "lab_group": ", ".join(prof.get("assosciated_labs", [])) if prof.get("assosciated_labs") else None,
                        "profile_url": None,
                    },
                    department_id=department_record.id,
                )

                all_professors.append({
                    "id": professor_record.id,
                    "name": professor_record.name,
                    "institution": professor_record.institution,
                    "department": professor_record.department,
                    "research_focus": professor_record.researchFocus,
                    "lab_group": professor_record.labGroup,
                    "profile_url": professor_record.profileUrl,
                })

        if not all_professors:
            return pd.DataFrame(columns=["id", "name", "institution", "department", "research_focus", "lab_group", "profile_url"])

        return pd.DataFrame(all_professors)


async def save_department_to_db(institution: str, department_name: str, url: str):
    prisma = await get_prisma()
    department = await prisma.department.upsert(
        where={"url": url},
        data={
            "create": {
                "institution": institution,
                "departmentName": department_name,
                "url": url,
                "lastScrapedAt": datetime.now(timezone.utc),
            },
            "update": {
                "lastScrapedAt": datetime.now(timezone.utc),
            },
        },
    )
    return department


async def save_professor_to_db(professor_data: Dict, department_id: str):
    prisma = await get_prisma()
    professor = await prisma.professor.upsert(
        where={
            "name_departmentId": {
                "name": professor_data["name"],
                "departmentId": department_id,
            }
        },
        data={
            "create": {
                "name": professor_data["name"],
                "institution": professor_data["institution"],
                "department": professor_data["department"],
                "researchFocus": professor_data["research_focus"],
                "labGroup": professor_data.get("lab_group"),
                "profileUrl": professor_data.get("profile_url"),
                "departmentId": department_id,
            },
            "update": {
                "researchFocus": professor_data["research_focus"],
                "labGroup": professor_data.get("lab_group"),
                "profileUrl": professor_data.get("profile_url"),
            },
        },
    )
    return professor

