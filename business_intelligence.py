"""
Business Intelligence Analyzer
Extracts comprehensive business information from websites and scores leads
based on ideal customer profile (ICP) criteria.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import re
from urllib.parse import urljoin
import time
import logging

logger = logging.getLogger(__name__)


class BusinessIntelligenceAnalyzer:
    """
    Analyzes business websites to extract comprehensive business intelligence
    and score leads based on ideal customer profile (ICP) criteria.
    """
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.timeout = 10
    
    def extract_business_info(self, website_url: str) -> Dict:
        """
        Extract comprehensive business information from website.
        
        Args:
            website_url: URL of the company website
        
        Returns:
            Dictionary containing business intelligence data
        """
        try:
            response = requests.get(website_url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract various business signals
            business_info = {
                'company_description': self._extract_description(soup),
                'services_products': self._extract_products_services(soup),
                'target_audience': self._extract_target_audience(soup),
                'pricing_info': self._extract_pricing(soup),
                'testimonials': self._extract_testimonials(soup),
                'case_studies': self._extract_case_studies(soup),
                'team_size_indicators': self._extract_team_info(soup),
                'technology_stack': self._extract_tech_stack(soup),
                'partnerships': self._extract_partnerships(soup),
                'awards_certifications': self._extract_awards(soup),
                'blog_activity': self._check_blog_activity(soup, website_url),
                'careers_page': self._check_careers_page(soup, website_url),
                'about_page_quality': self._analyze_about_page(soup, website_url),
                'contact_accessibility': self._analyze_contact_accessibility(soup),
                'social_proof': self._analyze_social_proof(soup),
                'website_quality_score': self._calculate_website_quality(soup)
            }
            
            return business_info
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"Error fetching website {website_url}: {str(e)}")
            return {'error': str(e)}
        except Exception as e:
            logger.error(f"Unexpected error analyzing {website_url}: {str(e)}")
            return {'error': str(e)}
    
    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract company description from meta tags and hero sections"""
        # Try meta description first
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content']
        
        # Try Open Graph description
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            return og_desc['content']
        
        # Try hero section
        hero = soup.find(['section', 'div'], class_=re.compile('hero|banner|intro', re.I))
        if hero:
            text = hero.get_text(strip=True)
            if len(text) > 50:
                return text[:500]
        
        return None
    
    def _extract_products_services(self, soup: BeautifulSoup) -> List[str]:
        """Extract products/services from website"""
        services = []
        
        # Look for services/products sections
        service_sections = soup.find_all(['section', 'div'], 
                                        class_=re.compile('service|product|offering|solution', re.I))
        
        for section in service_sections:
            headings = section.find_all(['h2', 'h3', 'h4'])
            for heading in headings:
                text = heading.get_text(strip=True)
                if text and len(text) < 100:
                    services.append(text)
        
        return list(set(services[:10]))  # Return top 10 unique
    
    def _extract_target_audience(self, soup: BeautifulSoup) -> List[str]:
        """Extract target audience indicators"""
        audience_keywords = [
            'enterprise', 'sme', 'startup', 'small business', 
            'b2b', 'b2c', 'non-profit', 'government', 'ngo'
        ]
        
        found_audiences = []
        page_text = soup.get_text().lower()
        
        for keyword in audience_keywords:
            if keyword in page_text:
                found_audiences.append(keyword)
        
        return found_audiences
    
    def _extract_pricing(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract pricing information"""
        pricing_section = soup.find(['section', 'div'], 
                                   class_=re.compile('pricing|price|plan', re.I))
        
        if pricing_section:
            # Look for price indicators
            price_pattern = r'\$[\d,]+|€[\d,]+|£[\d,]+|KES\s?[\d,]+|USD\s?[\d,]+'
            prices = re.findall(price_pattern, pricing_section.get_text())
            
            if prices:
                return {
                    'has_pricing_page': True,
                    'price_indicators': prices[:5]
                }
        
        return None
    
    def _extract_testimonials(self, soup: BeautifulSoup) -> int:
        """Count testimonials/reviews"""
        testimonial_sections = soup.find_all(['section', 'div'], 
                                           class_=re.compile('testimonial|review|client', re.I))
        return len(testimonial_sections)
    
    def _extract_case_studies(self, soup: BeautifulSoup) -> int:
        """Count case studies"""
        case_study_links = soup.find_all('a', href=re.compile('case.study|success.story|case-study', re.I))
        return len(case_study_links)
    
    def _extract_team_info(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract team size indicators"""
        team_section = soup.find(['section', 'div'], 
                               class_=re.compile('team|about.team|our.team', re.I))
        
        if team_section:
            # Count team member mentions
            team_members = team_section.find_all(['div', 'article'], 
                                                class_=re.compile('member|employee|staff', re.I))
            return {
                'has_team_page': True,
                'team_member_count': len(team_members)
            }
        
        return None
    
    def _extract_tech_stack(self, soup: BeautifulSoup) -> List[str]:
        """Extract technology stack indicators"""
        tech_keywords = [
            'api', 'cloud', 'saas', 'ai', 'machine learning', 
            'blockchain', 'mobile app', 'web app', 'api integration'
        ]
        
        found_tech = []
        page_text = soup.get_text().lower()
        
        for tech in tech_keywords:
            if tech in page_text:
                found_tech.append(tech)
        
        return found_tech
    
    def _extract_partnerships(self, soup: BeautifulSoup) -> int:
        """Count partnership mentions"""
        partnership_sections = soup.find_all(['section', 'div'], 
                                            class_=re.compile('partner|integration', re.I))
        return len(partnership_sections)
    
    def _extract_awards(self, soup: BeautifulSoup) -> int:
        """Count awards/certifications"""
        award_sections = soup.find_all(['section', 'div'], 
                                     class_=re.compile('award|certification|recognition', re.I))
        return len(award_sections)
    
    def _check_blog_activity(self, soup: BeautifulSoup, base_url: str) -> Dict:
        """Check if company has active blog"""
        blog_links = soup.find_all('a', href=re.compile('blog|news|article', re.I))
        
        if blog_links:
            return {
                'has_blog': True,
                'blog_links_found': len(blog_links)
            }
        
        return {'has_blog': False}
    
    def _check_careers_page(self, soup: BeautifulSoup, base_url: str) -> bool:
        """Check if company has careers page (indicates growth)"""
        careers_links = soup.find_all('a', href=re.compile('career|job|hiring', re.I))
        return len(careers_links) > 0
    
    def _analyze_about_page(self, soup: BeautifulSoup, base_url: str) -> Dict:
        """Analyze about page quality"""
        about_links = soup.find_all('a', href=re.compile('about', re.I))
        
        if about_links:
            return {
                'has_about_page': True,
                'about_page_quality': 'high' if len(about_links) > 0 else 'medium'
            }
        
        return {'has_about_page': False}
    
    def _analyze_contact_accessibility(self, soup: BeautifulSoup) -> Dict:
        """Analyze how easy it is to contact the company"""
        contact_indicators = {
            'has_contact_page': len(soup.find_all('a', href=re.compile('contact', re.I))) > 0,
            'has_phone': len(re.findall(r'\+?[\d\s\-\(\)]{10,}', soup.get_text())) > 0,
            'has_email': len(re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', soup.get_text())) > 0,
            'has_contact_form': len(soup.find_all('form', class_=re.compile('contact', re.I))) > 0
        }
        
        score = sum(contact_indicators.values())
        return {
            **contact_indicators,
            'accessibility_score': score,
            'accessibility_level': 'high' if score >= 3 else 'medium' if score == 2 else 'low'
        }
    
    def _analyze_social_proof(self, soup: BeautifulSoup) -> Dict:
        """Analyze social proof indicators"""
        social_proof = {
            'testimonials_count': self._extract_testimonials(soup),
            'case_studies_count': self._extract_case_studies(soup),
            'awards_count': self._extract_awards(soup),
            'partnerships_count': self._extract_partnerships(soup),
            'has_client_logos': len(soup.find_all('img', alt=re.compile('client|customer|partner', re.I))) > 0
        }
        
        total_score = (
            social_proof['testimonials_count'] * 2 +
            social_proof['case_studies_count'] * 3 +
            social_proof['awards_count'] * 2 +
            social_proof['partnerships_count'] * 2 +
            (5 if social_proof['has_client_logos'] else 0)
        )
        
        return {
            **social_proof,
            'social_proof_score': total_score,
            'social_proof_level': 'high' if total_score >= 15 else 'medium' if total_score >= 8 else 'low'
        }
    
    def _calculate_website_quality(self, soup: BeautifulSoup) -> Dict:
        """Calculate overall website quality score"""
        quality_indicators = {
            'has_meta_description': soup.find('meta', attrs={'name': 'description'}) is not None,
            'has_og_tags': soup.find('meta', attrs={'property': 'og:title'}) is not None,
            'has_favicon': soup.find('link', rel='icon') is not None,
            'has_structured_data': len(soup.find_all('script', type='application/ld+json')) > 0,
            'mobile_responsive': 'viewport' in str(soup.find('meta', attrs={'name': 'viewport'})),
            'has_sitemap': soup.find('link', rel='sitemap') is not None
        }
        
        score = sum(quality_indicators.values())
        
        return {
            **quality_indicators,
            'quality_score': score,
            'quality_level': 'high' if score >= 5 else 'medium' if score >= 3 else 'low'
        }
    
    def score_lead(self, company_data: Dict, business_info: Dict, 
                   ideal_customer_profile: Optional[Dict] = None) -> Dict:
        """
        Score a lead based on business intelligence and ICP criteria.
        
        Args:
            company_data: Original company data from AI generation
            business_info: Extracted business intelligence
            ideal_customer_profile: Optional ICP criteria (e.g., {'min_employees': 50, 'has_pricing': True})
        
        Returns:
            Dictionary with lead score and recommendations
        """
        score = 0
        max_score = 100
        scoring_details = {}
        
        # Skip scoring if there was an error in business info
        if 'error' in business_info:
            return {
                'lead_score': 0,
                'quality_tier': 'Unknown',
                'recommendation': 'Unable to analyze - website error',
                'scoring_breakdown': {},
                'max_possible_score': max_score,
                'business_intelligence': business_info
            }
        
        # 1. Website Quality (20 points)
        website_quality = business_info.get('website_quality_score', {})
        quality_score = website_quality.get('quality_score', 0)
        website_points = min(20, (quality_score / 6) * 20) if quality_score > 0 else 0
        score += website_points
        scoring_details['website_quality'] = round(website_points, 1)
        
        # 2. Contact Accessibility (15 points)
        contact_info = business_info.get('contact_accessibility', {})
        contact_score = contact_info.get('accessibility_score', 0)
        contact_points = min(15, (contact_score / 4) * 15) if contact_score > 0 else 0
        score += contact_points
        scoring_details['contact_accessibility'] = round(contact_points, 1)
        
        # 3. Social Proof (20 points)
        social_proof = business_info.get('social_proof', {})
        social_score = social_proof.get('social_proof_score', 0)
        social_points = min(20, (social_score / 30) * 20) if social_score > 0 else 0
        score += social_points
        scoring_details['social_proof'] = round(social_points, 1)
        
        # 4. Business Activity (15 points)
        activity_score = 0
        if business_info.get('blog_activity', {}).get('has_blog'):
            activity_score += 5
        if business_info.get('careers_page'):
            activity_score += 5
        if business_info.get('about_page_quality', {}).get('has_about_page'):
            activity_score += 5
        score += activity_score
        scoring_details['business_activity'] = activity_score
        
        # 5. Company Size Indicators (15 points)
        # Based on original company data
        company_size = company_data.get('company_size', '')
        if company_size:
            if '1000+' in company_size or '10,000+' in company_size or '10000+' in company_size:
                size_points = 15
            elif '100+' in company_size or '500+' in company_size:
                size_points = 10
            elif '50+' in company_size:
                size_points = 7
            else:
                size_points = 3
        else:
            size_points = 0
        score += size_points
        scoring_details['company_size'] = size_points
        
        # 6. Revenue Indicators (15 points)
        revenue = company_data.get('revenue_market_cap', '')
        if revenue:
            # Extract numbers from revenue string
            revenue_nums = re.findall(r'[\d.]+', revenue.replace(',', ''))
            if revenue_nums:
                try:
                    revenue_value = float(revenue_nums[0])
                    if 'billion' in revenue.lower() or revenue_value >= 1000:
                        revenue_points = 15
                    elif 'million' in revenue.lower() or revenue_value >= 10:
                        revenue_points = 10
                    else:
                        revenue_points = 5
                except:
                    revenue_points = 5
            else:
                revenue_points = 5
        else:
            revenue_points = 0
        score += revenue_points
        scoring_details['revenue'] = revenue_points
        
        # ICP Matching (if provided)
        if ideal_customer_profile:
            icp_bonus = 0
            if ideal_customer_profile.get('target_industries'):
                company_industry = company_data.get('key_products_services', '').lower()
                for target_industry in ideal_customer_profile['target_industries']:
                    if target_industry.lower() in company_industry:
                        icp_bonus += 5
                        break
            
            if ideal_customer_profile.get('min_employees'):
                # Extract employee count from company_size
                emp_nums = re.findall(r'\d+', company_size.replace(',', ''))
                if emp_nums:
                    try:
                        emp_count = int(emp_nums[0])
                        if emp_count >= ideal_customer_profile['min_employees']:
                            icp_bonus += 5
                    except:
                        pass
            
            score += min(icp_bonus, 10)  # Max 10 bonus points
            scoring_details['icp_match'] = min(icp_bonus, 10)
        
        # Calculate final score percentage
        final_score = min(100, round(score))
        
        # Determine lead quality tier
        if final_score >= 80:
            quality_tier = 'Premium'
            recommendation = 'High Priority - Excellent match'
        elif final_score >= 60:
            quality_tier = 'High'
            recommendation = 'Good match - Worth pursuing'
        elif final_score >= 40:
            quality_tier = 'Medium'
            recommendation = 'Moderate match - Consider if aligned'
        else:
            quality_tier = 'Low'
            recommendation = 'Low priority - May not be ideal'
        
        return {
            'lead_score': final_score,
            'quality_tier': quality_tier,
            'recommendation': recommendation,
            'scoring_breakdown': scoring_details,
            'max_possible_score': max_score,
            'business_intelligence': business_info
        }


def analyze_company_intelligence(company_data: Dict) -> Dict:
    """
    Convenience function to analyze a single company's business intelligence.
    
    Args:
        company_data: Company data dictionary with website_url
    
    Returns:
        Dictionary with business intelligence and lead score
    """
    analyzer = BusinessIntelligenceAnalyzer()
    website_url = company_data.get('website_url')
    
    if not website_url:
        return {
            'lead_score': 0,
            'quality_tier': 'Unknown',
            'recommendation': 'No website URL provided',
            'business_intelligence': {}
        }
    
    # Extract business intelligence
    business_info = analyzer.extract_business_info(website_url)
    
    # Score the lead
    lead_scoring = analyzer.score_lead(company_data, business_info)
    
    return lead_scoring

