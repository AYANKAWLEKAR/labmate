import re
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup


class ProjectScraper:
    """Scrapes projects from professor/lab websites."""
    
    def __init__(self, timeout: int = 10):
        """
        Initialize the scraper.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_url(self, url: str) -> Dict:
        """
        Scrape projects from a single URL.
        
        Args:
            url: The URL to scrape
            
        Returns:
            Dictionary with keys:
                - 'url': Original URL
                - 'raw_text': Compiled project text
                - 'projects': List of individual projects (if identifiable)
                - 'method': 'links' or 'text_siblings' indicating how projects were found
                - 'error': Error message if scraping failed
        """
        result = {
            'url': url,
            'raw_text': '',
            'projects': [],
            'method': None,
            'error': None
        }
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find projects section
            projects_section = self._find_projects_section(soup)
            
            if not projects_section:
                result['error'] = 'No projects section found'
                return result
            
            # Try to scrape via links first
            projects_links = self._find_project_links(projects_section)
            
            if projects_links:
                result['raw_text'], result['projects'] = self._scrape_project_links(
                    projects_links, 
                    url
                )
                result['method'] = 'links'
            else:
                # Fall back to text siblings
                result['raw_text'], result['projects'] = self._extract_text_siblings(
                    projects_section
                )
                result['method'] = 'text_siblings'
            
            return result
            
        except requests.RequestException as e:
            result['error'] = f'Request failed: {str(e)}'
            return result
        except Exception as e:
            result['error'] = f'Scraping failed: {str(e)}'
            return result
    
    def _find_projects_section(self, soup: BeautifulSoup) -> Optional[BeautifulSoup]:
        """
        Find the projects section in the page.
        
        Looks for headers (h1-h6) or elements containing "projects" text,
        then returns the section or the element itself.
        """
        # Search for headers with "projects" in text
        headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        for header in headers:
            if 'project' in header.get_text().lower():
                return header
        
        # Search for divs, sections with class or id containing "project"
        for tag in soup.find_all(['div', 'section']):
            class_attr = ' '.join(tag.get('class', []))
            id_attr = tag.get('id', '')
            
            if 'project' in (class_attr + ' ' + id_attr).lower():
                return tag
        
        # Search for any element containing the word "projects"
        for tag in soup.find_all(string=re.compile(r'projects', re.IGNORECASE)):
            parent = tag.parent
            if parent:
                return parent
        
        return None
    
    def _find_project_links(self, section: BeautifulSoup) -> List[Tuple[str, str]]:
        """
        Find links within the projects section.
        
        Returns:
            List of tuples: (link_url, link_text)
        """
        links = []
        
        # Find all anchor tags in the section
        anchors = section.find_all('a', recursive=True)
        
        for anchor in anchors:
            href = anchor.get('href')
            text = anchor.get_text(strip=True)
            
            # Skip empty or non-HTTP links
            if href and text and href.startswith(('http', '/')):
                links.append((href, text))
        
        return links
    
    def _scrape_project_links(
        self, 
        links: List[Tuple[str, str]], 
        base_url: str
    ) -> Tuple[str, List[str]]:
        """
        Follow project links and extract text content.
        
        Args:
            links: List of (url, text) tuples
            base_url: Base URL for resolving relative links
            
        Returns:
            Tuple of (raw_text, project_list)
        """
        raw_text_parts = []
        projects = []
        
        for link_url, link_text in links:
            # Resolve relative URLs
            full_url = urljoin(base_url, link_url)
            
            try:
                response = self.session.get(full_url, timeout=self.timeout)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract paragraphs and text elements
                text = self._extract_text_content(soup)
                
                if text:
                    raw_text_parts.append(f"# {link_text}\n{text}\n")
                    projects.append(link_text)
                    
            except Exception as e:
                # Log error but continue
                raw_text_parts.append(f"# {link_text}\n[Error fetching content: {str(e)}]\n")
        
        raw_text = '\n'.join(raw_text_parts)
        return raw_text, projects
    
    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """
        Extract main text content from a page.
        
        Targets paragraphs, lists, and other text elements while
        removing navigation, scripts, and styling.
        """
        # Remove script and style elements
        for script in soup(['script', 'style']):
            script.decompose()
        
        # Extract paragraphs
        paragraphs = []
        for tag in soup.find_all(['p', 'li', 'div', 'span']):
            text = tag.get_text(strip=True)
            
            # Skip very short or empty text
            if text and len(text) > 10:
                paragraphs.append(text)
        
        return '\n'.join(paragraphs)
    
    def _extract_text_siblings(self, projects_element: BeautifulSoup) -> Tuple[str, List[str]]:
        """
        Extract text from siblings of the projects element.
        
        Looks for lists, text nodes, and structured data that could
        represent a list of projects.
        """
        raw_text_parts = []
        projects = []
        
        # Look for lists after the projects element
        ul_lists = projects_element.find_all_next('ul', recursive=False)
        ol_lists = projects_element.find_all_next('ol', recursive=False)
        
        for ul in ul_lists:
            for li in ul.find_all('li', recursive=False):
                text = li.get_text(strip=True)
                if text:
                    raw_text_parts.append(f"- {text}")
                    projects.append(text)
        
        for ol in ol_lists:
            for li in ol.find_all('li', recursive=False):
                text = li.get_text(strip=True)
                if text:
                    raw_text_parts.append(f"- {text}")
                    projects.append(text)
        
        # If no lists found, extract sibling text elements
        if not raw_text_parts:
            for sibling in projects_element.find_next_siblings():
                if sibling.name in ['p', 'div']:
                    text = sibling.get_text(strip=True)
                    if text and len(text) > 10:
                        raw_text_parts.append(text)
                elif sibling.name in ['h1', 'h2', 'h3']:
                    # Stop if we hit another major heading
                    break
        
        raw_text = '\n'.join(raw_text_parts)
        return raw_text, projects
    
    def scrape_multiple(self, urls: List[str]) -> List[Dict]:
        """
        Scrape multiple URLs.
        
        Args:
            urls: List of URLs to scrape
            
        Returns:
            List of result dictionaries
        """
        results = []
        for url in urls:
            result = self.scrape_url(url)
            results.append(result)
            print(f"✓ Scraped {url} ({result['method'] or 'failed'})")
        
        return results


def print_results(results: List[Dict]) -> None:
    """Pretty print scraping results."""
    for result in results:
        print("\n" + "="*80)
        print(f"URL: {result['url']}")
        print(f"Method: {result['method']}")
        
        if result['error']:
            print(f"Error: {result['error']}")
        else:
            print(f"\nRAW TEXT:\n{result['raw_text']}\n")
            
            if result['projects']:
                print(f"EXTRACTED PROJECTS ({len(result['projects'])}):")
                for project in result['projects']:
                    print(f"  • {project}")



class MachineLearningProjectScraper:

    #chunk site and use llm to extract gist of the page. Can either be done on the main page or on the projects page
    