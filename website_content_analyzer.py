"""
Website Content Analyzer
Retrieves and parses website content (HTML, metadata, structured data)
for deep business intelligence extraction.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Set
import re
import json
from urllib.parse import urljoin, urlparse
import logging
from dataclasses import dataclass
import time

logger = logging.getLogger(__name__)


@dataclass
class WebsiteContent:
    """Structured representation of website content"""
    url: str
    title: str
    description: str
    headings: List[str]
    paragraphs: List[str]
    links: List[str]
    images: List[str]
    metadata: Dict
    structured_data: List[Dict]
    text_content: str
    html_structure: Dict


class WebsiteContentAnalyzer:
    """
    Retrieves and parses website content with focus on business intelligence.
    Optimized for speed and accuracy with minimal external dependencies.
    """
    
    def __init__(self, timeout: int = 15, max_pages: int = 3):
        """
        Initialize analyzer.
        
        Args:
            timeout: Request timeout in seconds
            max_pages: Maximum number of pages to analyze
        """
        self.timeout = timeout
        self.max_pages = max_pages
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        self.visited_urls: Set[str] = set()
    
    def fetch_website(self, url: str) -> Optional[WebsiteContent]:
        """
        Fetch and parse website content.
        
        Args:
            url: Website URL to analyze
        
        Returns:
            WebsiteContent object or None if error
        """
        try:
            # Normalize URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            logger.info(f"Fetching website: {url}")
            
            # Fetch main page
            response = requests.get(url, headers=self.headers, timeout=self.timeout, allow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract basic content
            content = self._extract_content(soup, url)
            
            # Fetch additional pages for context
            additional_pages = self._get_important_pages(soup, url)
            for page_url in additional_pages[:self.max_pages - 1]:
                if page_url not in self.visited_urls:
                    try:
                        page_content = self._fetch_page(page_url)
                        if page_content:
                            content = self._merge_content(content, page_content)
                        time.sleep(0.5)  # Be respectful
                    except Exception as e:
                        logger.warning(f"Error fetching {page_url}: {str(e)}")
            
            return content
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching website {url}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error analyzing {url}: {str(e)}")
            return None
    
    def _extract_content(self, soup: BeautifulSoup, base_url: str) -> WebsiteContent:
        """Extract all content from a page"""
        
        # Title
        title = soup.find('title')
        title_text = title.get_text(strip=True) if title else ""
        
        # Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc.get('content', '') if meta_desc else ""
        
        # Open Graph description (often more detailed)
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            description = og_desc.get('content') or description
        
        # Headings (h1-h6)
        headings = []
        for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            for heading in soup.find_all(tag):
                text = heading.get_text(strip=True)
                if text and len(text) > 3:
                    headings.append(text)
        
        # Paragraphs
        paragraphs = []
        for p in soup.find_all('p'):
            text = p.get_text(strip=True)
            if text and len(text) > 20:  # Filter out very short paragraphs
                paragraphs.append(text)
        
        # Links
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            link_text = a.get_text(strip=True)
            if href.startswith('http') or href.startswith('/'):
                full_url = urljoin(base_url, href)
                links.append({'url': full_url, 'text': link_text})
        
        # Images with alt text
        images = []
        for img in soup.find_all('img', src=True):
            alt = img.get('alt', '')
            src = img.get('src', '')
            if alt or src:
                images.append({'src': urljoin(base_url, src), 'alt': alt})
        
        # Metadata
        metadata = self._extract_metadata(soup)
        
        # Structured data (JSON-LD, Microdata, RDFa)
        structured_data = self._extract_structured_data(soup)
        
        # Full text content
        text_content = soup.get_text(separator=' ', strip=True)
        
        # HTML structure analysis
        html_structure = self._analyze_html_structure(soup)
        
        return WebsiteContent(
            url=base_url,
            title=title_text,
            description=description,
            headings=headings,
            paragraphs=paragraphs,
            links=links,
            images=images,
            metadata=metadata,
            structured_data=structured_data,
            text_content=text_content,
            html_structure=html_structure
        )
    
    def _extract_metadata(self, soup: BeautifulSoup) -> Dict:
        """Extract all metadata from page"""
        metadata = {}
        
        # Meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property') or meta.get('itemprop')
            content = meta.get('content')
            if name and content:
                metadata[name] = content
        
        # Open Graph
        og_tags = {}
        for meta in soup.find_all('meta', property=re.compile(r'^og:')):
            prop = meta.get('property', '').replace('og:', '')
            content = meta.get('content')
            if prop and content:
                og_tags[prop] = content
        if og_tags:
            metadata['open_graph'] = og_tags
        
        # Twitter Cards
        twitter_tags = {}
        for meta in soup.find_all('meta', attrs={'name': re.compile(r'^twitter:')}):
            name = meta.get('name', '').replace('twitter:', '')
            content = meta.get('content')
            if name and content:
                twitter_tags[name] = content
        if twitter_tags:
            metadata['twitter'] = twitter_tags
        
        return metadata
    
    def _extract_structured_data(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract structured data (JSON-LD, Microdata)"""
        structured_data = []
        
        # JSON-LD
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                structured_data.append({
                    'type': 'json-ld',
                    'data': data
                })
            except (json.JSONDecodeError, AttributeError):
                continue
        
        # Microdata
        microdata = []
        for item in soup.find_all(attrs={'itemscope': True}):
            item_data = {}
            item_type = item.get('itemtype', '')
            if item_type:
                item_data['type'] = item_type
            
            for prop in item.find_all(attrs={'itemprop': True}):
                prop_name = prop.get('itemprop')
                prop_value = prop.get('content') or prop.get_text(strip=True)
                if prop_name and prop_value:
                    item_data[prop_name] = prop_value
            
            if item_data:
                microdata.append(item_data)
        
        if microdata:
            structured_data.append({
                'type': 'microdata',
                'data': microdata
            })
        
        return structured_data
    
    def _analyze_html_structure(self, soup: BeautifulSoup) -> Dict:
        """Analyze HTML structure for business intelligence"""
        structure = {
            'has_navbar': len(soup.find_all(['nav', 'header'])) > 0,
            'has_footer': len(soup.find_all('footer')) > 0,
            'has_forms': len(soup.find_all('form')) > 0,
            'has_videos': len(soup.find_all(['video', 'iframe'])) > 0,
            'section_count': len(soup.find_all('section')),
            'article_count': len(soup.find_all('article')),
            'button_count': len(soup.find_all('button')),
            'input_count': len(soup.find_all('input')),
            'class_names': list(set([cls for elem in soup.find_all(class_=True) for cls in elem.get('class', [])]))[:20]
        }
        
        return structure
    
    def _get_important_pages(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Get URLs of important pages (About, Products, Services, etc.)"""
        important_keywords = [
            'about', 'product', 'service', 'solution', 'pricing', 
            'contact', 'features', 'benefits', 'how-it-works'
        ]
        
        important_urls = []
        for a in soup.find_all('a', href=True):
            href = a['href'].lower()
            link_text = a.get_text(strip=True).lower()
            
            if any(keyword in href or keyword in link_text for keyword in important_keywords):
                full_url = urljoin(base_url, a['href'])
                if urlparse(full_url).netloc == urlparse(base_url).netloc:
                    important_urls.append(full_url)
        
        return list(set(important_urls))[:5]  # Limit to 5 pages
    
    def _fetch_page(self, url: str) -> Optional[WebsiteContent]:
        """Fetch a single page"""
        try:
            self.visited_urls.add(url)
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            return self._extract_content(soup, url)
        except Exception as e:
            logger.warning(f"Error fetching page {url}: {str(e)}")
            return None
    
    def _merge_content(self, main: WebsiteContent, additional: WebsiteContent) -> WebsiteContent:
        """Merge content from additional pages into main content"""
        # Merge headings (avoid duplicates)
        all_headings = main.headings + [h for h in additional.headings if h not in main.headings]
        
        # Merge paragraphs
        all_paragraphs = main.paragraphs + [p for p in additional.paragraphs if p not in main.paragraphs]
        
        # Merge links
        existing_urls = {link['url'] for link in main.links}
        all_links = main.links + [link for link in additional.links if link['url'] not in existing_urls]
        
        # Merge text content
        combined_text = main.text_content + " " + additional.text_content
        
        # Update main content
        main.headings = all_headings[:50]  # Limit to prevent bloat
        main.paragraphs = all_paragraphs[:100]
        main.links = all_links[:200]
        main.text_content = combined_text[:50000]  # Limit text content
        
        return main


def analyze_website_content(url: str) -> Optional[WebsiteContent]:
    """
    Convenience function to analyze website content.
    
    Args:
        url: Website URL to analyze
    
    Returns:
        WebsiteContent object or None
    """
    analyzer = WebsiteContentAnalyzer()
    return analyzer.fetch_website(url)

