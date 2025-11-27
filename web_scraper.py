# To run this code you need to install the following dependencies:
# pip install beautifulsoup4 requests

import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from typing import Dict, List, Set, Optional

class WebScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.timeout = 10
        self.visited_urls = set()
        
    def extract_emails(self, text: str) -> Set[str]:
        """Extract email addresses from text using regex"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = set(re.findall(email_pattern, text))
        
        # Filter out common non-contact emails
        excluded_patterns = ['example.com', 'domain.com', 'email.com', 'yourcompany.com', 
                           'company.com', 'test.com', 'sample.com', 'placeholder']
        
        filtered_emails = set()
        for email in emails:
            if not any(pattern in email.lower() for pattern in excluded_patterns):
                # Also filter out image file extensions that might be caught
                if not email.lower().endswith(('.png', '.jpg', '.gif', '.svg')):
                    filtered_emails.add(email)
        
        return filtered_emails
    
    def extract_social_media(self, soup: BeautifulSoup, base_url: str) -> Dict[str, Optional[str]]:
        """Extract social media links from the page"""
        social_media = {
            'linkedin': None,
            'twitter': None,
            'facebook': None,
            'instagram': None,
            'youtube': None
        }
        
        # Find all links
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link['href'].lower()
            
            # LinkedIn
            if 'linkedin.com/company' in href or 'linkedin.com/in' in href:
                if not social_media['linkedin']:
                    social_media['linkedin'] = link['href'] if link['href'].startswith('http') else urljoin(base_url, link['href'])
            
            # Twitter/X
            elif 'twitter.com' in href or 'x.com' in href:
                if not social_media['twitter'] and '/intent/' not in href:
                    social_media['twitter'] = link['href'] if link['href'].startswith('http') else urljoin(base_url, link['href'])
            
            # Facebook
            elif 'facebook.com' in href:
                if not social_media['facebook'] and '/sharer' not in href:
                    social_media['facebook'] = link['href'] if link['href'].startswith('http') else urljoin(base_url, link['href'])
            
            # Instagram
            elif 'instagram.com' in href:
                if not social_media['instagram']:
                    social_media['instagram'] = link['href'] if link['href'].startswith('http') else urljoin(base_url, link['href'])
            
            # YouTube
            elif 'youtube.com' in href or 'youtu.be' in href:
                if not social_media['youtube'] and '/embed/' not in href and '/watch?' not in href:
                    social_media['youtube'] = link['href'] if link['href'].startswith('http') else urljoin(base_url, link['href'])
        
        return social_media
    
    def find_contact_page_urls(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Find potential contact page URLs"""
        contact_urls = []
        contact_keywords = ['contact', 'contact-us', 'contactus', 'about', 'about-us', 
                          'support', 'help', 'get-in-touch', 'reach-us', 'connect']
        
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link['href'].lower()
            link_text = link.get_text().lower()
            
            # Check if it's a contact-related link
            if any(keyword in href or keyword in link_text for keyword in contact_keywords):
                full_url = urljoin(base_url, link['href'])
                
                # Make sure it's from the same domain
                if urlparse(full_url).netloc == urlparse(base_url).netloc:
                    if full_url not in contact_urls and full_url not in self.visited_urls:
                        contact_urls.append(full_url)
        
        return contact_urls[:5]  # Limit to first 5 contact pages
    
    def scrape_page(self, url: str) -> tuple[Set[str], Dict[str, Optional[str]]]:
        """Scrape a single page for emails and social media"""
        emails = set()
        social_media = {
            'linkedin': None,
            'twitter': None,
            'facebook': None,
            'instagram': None,
            'youtube': None
        }
        
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout, allow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract emails from page text and HTML
            page_text = soup.get_text()
            emails = self.extract_emails(page_text)
            
            # Also check mailto links
            mailto_links = soup.find_all('a', href=re.compile(r'^mailto:', re.IGNORECASE))
            for mailto in mailto_links:
                email_match = re.search(r'mailto:([^\?\"\'>\s]+)', mailto['href'], re.IGNORECASE)
                if email_match:
                    emails.add(email_match.group(1))
            
            # Extract social media
            social_media = self.extract_social_media(soup, url)
            
            return emails, social_media
            
        except requests.exceptions.RequestException as e:
            print(f"Error scraping {url}: {str(e)}")
            return emails, social_media
    
    def scrape_website(self, base_url: str) -> Dict:
        """Scrape the entire website for contact info and social media"""
        print(f"\nScraping: {base_url}")
        
        all_emails = set()
        final_social_media = {
            'linkedin': None,
            'twitter': None,
            'facebook': None,
            'instagram': None,
            'youtube': None
        }
        
        self.visited_urls = set()
        
        try:
            # First, scrape the homepage
            self.visited_urls.add(base_url)
            emails, social_media = self.scrape_page(base_url)
            all_emails.update(emails)
            
            # Update social media (keep first found)
            for platform, url in social_media.items():
                if url and not final_social_media[platform]:
                    final_social_media[platform] = url
            
            print(f"  - Homepage scraped: {len(emails)} emails found")
            
            # Get the homepage soup to find contact pages
            response = requests.get(base_url, headers=self.headers, timeout=self.timeout)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find and scrape contact pages
            contact_urls = self.find_contact_page_urls(soup, base_url)
            print(f"  - Found {len(contact_urls)} potential contact pages")
            
            for contact_url in contact_urls:
                time.sleep(0.3)  # Reduced delay - still respectful but faster
                self.visited_urls.add(contact_url)
                
                emails, social_media = self.scrape_page(contact_url)
                all_emails.update(emails)
                
                # Update social media
                for platform, url in social_media.items():
                    if url and not final_social_media[platform]:
                        final_social_media[platform] = url
                
                print(f"  - Scraped {contact_url}: {len(emails)} emails found")
            
            # Convert emails set to list and get the most likely contact email
            email_list = list(all_emails)
            primary_email = None
            
            if email_list:
                # Prioritize emails with contact, info, sales, support keywords
                priority_keywords = ['contact', 'info', 'hello', 'support', 'sales', 'business']
                for email in email_list:
                    if any(keyword in email.lower() for keyword in priority_keywords):
                        primary_email = email
                        break
                
                # If no priority email found, just use the first one
                if not primary_email:
                    primary_email = email_list[0]
            
            print(f"  - Total emails found: {len(all_emails)}")
            print(f"  - Social media accounts found: {sum(1 for v in final_social_media.values() if v)}")
            
            return {
                'contact_email': primary_email,
                'all_emails': email_list,
                'social_media': final_social_media
            }
            
        except Exception as e:
            print(f"  - Error: {str(e)}")
            return {
                'contact_email': None,
                'all_emails': [],
                'social_media': final_social_media
            }

def scrape_company_data(company_data: Dict) -> Dict:
    """Enhance company data with scraped information"""
    scraper = WebScraper()
    
    for company in company_data.get('companies', []):
        website_url = company.get('website_url')
        
        if website_url:
            scraped_data = scraper.scrape_website(website_url)
            
            # Store LLM email as separate field before overwriting
            if company.get('contact_email'):
                company['contact_email_llm'] = company['contact_email']
            
            # Update contact email with scraped data (prioritize scraped as it's real-time)
            if scraped_data['contact_email']:
                company['contact_email'] = scraped_data['contact_email']
            
            # Store all emails found
            company['additional_emails'] = scraped_data['all_emails']
            
            # Keep LLM social media in original field
            # Add scraped social media as verified/real-time data
            if scraped_data['social_media']:
                company['social_media_scraped'] = {}
                for platform, url in scraped_data['social_media'].items():
                    if url:
                        company['social_media_scraped'][platform] = url
            
            # Also fill in missing LLM social media with scraped data
            for platform, url in scraped_data['social_media'].items():
                if url and (not company.get('social_media', {}).get(platform)):
                    if 'social_media' not in company:
                        company['social_media'] = {}
                    company['social_media'][platform] = url
            
            # Small delay between companies (reduced for speed)
            time.sleep(0.5)
    
    return company_data


def scrape_company_data_parallel(company_data: Dict, max_workers: int = 3) -> Dict:
    """
    Enhanced version with parallel scraping for faster performance.
    
    Args:
        company_data: Dictionary with companies list
        max_workers: Number of parallel workers (default: 3)
    
    Returns:
        Enhanced company data with scraped information
    """
    from concurrent.futures import ThreadPoolExecutor
    import logging
    
    logger = logging.getLogger(__name__)
    scraper = WebScraper()
    companies = company_data.get('companies', [])
    
    def scrape_single_company(company):
        """Scrape a single company's website"""
        website_url = company.get('website_url')
        if not website_url:
            return company
        
        try:
            scraped_data = scraper.scrape_website(website_url)
            
            # Store LLM email as separate field before overwriting
            if company.get('contact_email'):
                company['contact_email_llm'] = company['contact_email']
            
            # Update contact email with scraped data (prioritize scraped as it's real-time)
            if scraped_data['contact_email']:
                company['contact_email'] = scraped_data['contact_email']
            
            # Store all emails found
            company['additional_emails'] = scraped_data['all_emails']
            
            # Keep LLM social media in original field
            # Add scraped social media as verified/real-time data
            if scraped_data['social_media']:
                company['social_media_scraped'] = {}
                for platform, url in scraped_data['social_media'].items():
                    if url:
                        company['social_media_scraped'][platform] = url
            
            # Also fill in missing LLM social media with scraped data
            for platform, url in scraped_data['social_media'].items():
                if url and (not company.get('social_media', {}).get(platform)):
                    if 'social_media' not in company:
                        company['social_media'] = {}
                    company['social_media'][platform] = url
            
            return company
        except Exception as e:
            logger.warning(f"Error scraping {website_url}: {str(e)}")
            return company
    
    # Use ThreadPoolExecutor for parallel scraping
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(scrape_single_company, companies))
    
    return {'companies': results}

if __name__ == '__main__':
    # Example usage
    scraper = WebScraper()
    
    # Test with a single website
    test_url = "https://www.unitedhealthgroup.com/"
    result = scraper.scrape_website(test_url)
    
    print("\n=== Results ===")
    print(f"Primary Contact Email: {result['contact_email']}")
    print(f"All Emails Found: {result['all_emails']}")
    print(f"Social Media:")
    for platform, url in result['social_media'].items():
        print(f"  - {platform}: {url}")

