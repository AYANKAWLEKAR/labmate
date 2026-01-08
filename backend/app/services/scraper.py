import pandas as pd
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict
import time
from pandas._libs.algos import groupsort_indexer
import requests
import re
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from project_scraper import ProjectScraper
import os


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




def get_selenium_driver():
    """Initialize Selenium WebDriver with headless Chrome."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    )
    
    try:
        driver = webdriver.Chrome(options=options)
        return driver
    except WebDriverException:
        # Fallback: try without headless if Chrome not available
        options.remove_argument("--headless")
        try:
            return webdriver.Chrome(options=options)
        except:
            return None


class Scraper:
    def __init__(self, university: str):
        self.university = university
        self.config = INSTITUTION_CONFIGS[university]
        self.url = self.config["base_url"]
        self.method = self.config["method"]
        self.selectors = self.config["selectors"]
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        self.session = requests.Session()


        
    def scrapeRutgers(self,method) -> List[Dict]:


        def scrape_labs(groups: List[str]) -> List[str]:

            research_focus=[]
            assosciated_labs=[]
            for lab in groups[:1]:
                response=requests.get(group)
                response.raise_for_status()
                assosciated_labs=[]
                lab_parser=BeautifulSoup(response.text, "html.parser")
                body=lab_parser.find("div", class_="article-body")
                all_labs_header=body.find_all("h2")[-1]
                lab_ps = all_labs_header.find_next_siblings("p")
                for p in lab_ps:
                    link=p.find("a",href=True)
                    if link:
                        assosciated_labs.append(link.text.strip())
                        research_focus=scrape_website(link["href"])
                return research_focus,assosciated_labs

                    

                
            return ""
            
        def scrape_website(website: str) -> str:
            response=requests.get(website)
            response.raise_for_status()
            website_parser=BeautifulSoup(response.text, "html.parser")
            ps=ProjectScraper()
            raw_text=ps.scrape_url(website)
            
            return projects
            
        professors=[]
        base_url="https://www.cs.rutgers.edu/"
        if method=="beautifulsoup":

            response = requests.get(self.url)
            response.raise_for_status()
            link_parser=BeautifulSoup(response.text, "html.parser")
            all_links=set()
            for link in link_parser.find_all("a", href=True):
                href=link['href']
                if "/people/professors/details/" in href:
                    full_url = urljoin(base_url, href)
                    all_links.add(full_url)
            for link in all_links:
                
                groups=[]
                
                reponse=requests.get(link)
                reponse.raise_for_status()
                prof_parser=BeautifulSoup(reponse.text, "html.parser")
                values_list = prof_parser.find("ul", class_="fields-container")
                for li in values_list.find_all("li"):
                    if "name" in li.text.lower():
                        name=li.find("span","field-value").text.strip()
                    if "website" in li.text.lower():
                        website=li.find("span","field-value").text.strip()
                    if "groups" in li.text.lower():
                        list_groups=li.find_all("a")
                        for group in list_groups:
                            groups.append(group.text.strip())
                if name:
                    #goal is to find specific research focus of the professor
                    #lab group names help with this but in case they aren't listed then we need to scrape the website for the research focus
                    if not website and groups:

                        research_focus=scrape_labs(groups)
                        professors.append({
                            "name": name,
                            #"groups": groups,
                            "assosciated_labs": [],
                            "raw_research_focus": research_focus
                        })
                    if not groups and website:
                        research_focus,assosciated_labs=scrape_website(website)
                        professors.append({
                            "name": name,
                            #"groups":groups,
                            "assosciated_labs": assosciated_labs,
                            "raw_research_focus": research_focus
                        })

                else:
                    continue
                time.sleep(1)

        return professors



            




    def scrapeRutgers(self,method) -> List[Dict]:

    def scrapeTCNJ(self,method) -> List[Dict]:
        






def scrape_with_selenium(url: str, config: Dict) -> List[Dict]:
    """Scrape using Selenium for JavaScript-rendered content."""
    driver = get_selenium_driver()
    if not driver:
        return []
    
    professors = []
    try:
        driver.get(url)
        time.sleep(3)  # Wait for page load
        
        # Wait for professor containers
        wait = WebDriverWait(driver, 10)
        containers = wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, config["selectors"]["professor_container"])
            )
        )
        
        for container in containers[:20]:  # Limit to 20
            try:
                name_elem = container.find_element(
                    By.CSS_SELECTOR, config["selectors"]["name"]
                )
                name = name_elem.text.strip()
                
                dept_elem = container.find_element(
                    By.CSS_SELECTOR, config["selectors"]["department"]
                )
                department = dept_elem.text.strip()
                
                research_elem = container.find_element(
                    By.CSS_SELECTOR, config["selectors"]["research"]
                )
                research = research_elem.text.strip()
                
                link_elem = container.find_element(
                    By.CSS_SELECTOR, config["selectors"]["profile_link"]
                )
                profile_url = link_elem.get_attribute("href") or ""
                
                professors.append({
                    "name": name,
                    "department": department,
                    "research_focus": research,
                    "profile_url": profile_url,
                })
            except Exception:
                continue
                
    except TimeoutException:
        pass
    finally:
        driver.quit()
    
    return professors


async def scrape_with_beautifulsoup(url: str, config: Dict) -> List[Dict]:
    """Scrape using BeautifulSoup for static HTML content."""
    professors = []
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                },
            )
            response.raise_for_status()
            html = response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return professors
    
    soup = BeautifulSoup(html, "lxml")
    
    # Try to find professor containers
    containers = soup.select(config["selectors"]["professor_container"])
    
    if not containers:
        # Fallback: try common patterns
        containers = soup.find_all("div", class_=re.compile(r"faculty|professor|person", re.I))
    
    for container in containers[:20]:  # Limit to 20
        try:
            # Extract name
            name_elem = container.select_one(config["selectors"]["name"])
            if not name_elem:
                name_elem = container.find("h2") or container.find("h3") or container.find("h4")
            name = name_elem.get_text(strip=True) if name_elem else "Unknown"
            
            # Extract department
            dept_elem = container.select_one(config["selectors"]["department"])
            if not dept_elem:
                dept_elem = container.find(class_=re.compile(r"dept|department|school", re.I))
            department = dept_elem.get_text(strip=True) if dept_elem else "Unknown"
            
            # Extract research focus
            research_elem = container.select_one(config["selectors"]["research"])
            if not research_elem:
                research_elem = container.find(class_=re.compile(r"research|interest|focus", re.I))
            research = research_elem.get_text(strip=True) if research_elem else "Research interests not specified"
            
            # Extract profile link
            link_elem = container.select_one(config["selectors"]["profile_link"])
            if link_elem:
                profile_url = link_elem.get("href", "")
                if profile_url and not profile_url.startswith("http"):
                    # Make absolute URL
                    profile_url = urljoin(url, profile_url)
            else:
                profile_url = ""
            
            if name and name != "Unknown":
                professors.append({
                    "name": name,
                    "department": department,
                    "research_focus": research,
                    "profile_url": profile_url,
                })
        except Exception:
            continue
    
    return professors


async def scrape_single_institution(institution: str) -> List[Dict]:
    """Scrape a single institution's faculty page."""
    if institution not in INSTITUTION_CONFIGS:
        return []
    
    config = INSTITUTION_CONFIGS[institution]
    url = config["base_url"]
    method = config.get("method", "beautifulsoup")
    
    if method == "selenium":
        professors = scrape_with_selenium(url, config)
    else:
        professors = await scrape_with_beautifulsoup(url, config)
    
    # Add institution to each professor
    for prof in professors:
        prof["institution"] = institution
        prof["id"] = f"{institution}_{prof['name']}".replace(" ", "_").lower()
        prof["lab_group"] = None  # Can be enhanced later
    
    return professors


async def scrape_institutions(institutions: List[str]) -> pd.DataFrame:
    """
    Scrape multiple institutions and return a pandas DataFrame.
    Limits to 20 professors total across all institutions.
    """
    all_professors = []
    
    for institution in institutions:
        print(f"Scraping {institution}...")
        professors = await scrape_single_institution(institution)
        all_professors.extend(professors)
        time.sleep(2)  # Be respectful with rate limiting
    
    # Convert to DataFrame
    if not all_professors:
        # Return empty DataFrame with expected columns
        return pd.DataFrame(columns=[
            "id", "name", "institution", "department", 
            "research_focus", "lab_group", "profile_url"
        ])
    
    df = pd.DataFrame(all_professors)
    
    # Limit to 20 professors total
    if len(df) > 20:
        df = df.head(20)
    
    # Ensure all required columns exist
    required_cols = ["id", "name", "institution", "department", "research_focus", "lab_group", "profile_url"]
    for col in required_cols:
        if col not in df.columns:
            df[col] = None
    
    return df[required_cols]

