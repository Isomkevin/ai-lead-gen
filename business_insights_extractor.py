"""
Business Insights Extractor
Extracts key business attributes from website content for lead generation.
"""

import re
from typing import Dict, List, Optional, Set
from website_content_analyzer import WebsiteContent
import logging

logger = logging.getLogger(__name__)


class BusinessInsightsExtractor:
    """
    Extracts business attributes from website content.
    Analyzes text, structure, and metadata to understand:
    - Industry and product type
    - Offerings and services
    - Value proposition
    - Target audience (ICP)
    - Pricing model
    - Business tone and positioning
    """
    
    def __init__(self):
        # Industry keywords mapping
        self.industry_keywords = {
            'technology': ['software', 'saas', 'platform', 'api', 'cloud', 'digital', 'tech', 'app', 'application'],
            'healthcare': ['health', 'medical', 'hospital', 'clinic', 'patient', 'doctor', 'treatment', 'wellness'],
            'finance': ['financial', 'banking', 'investment', 'payment', 'fintech', 'money', 'credit', 'loan'],
            'education': ['education', 'learning', 'course', 'training', 'school', 'university', 'student'],
            'ecommerce': ['shop', 'store', 'buy', 'cart', 'product', 'retail', 'marketplace', 'sell'],
            'consulting': ['consulting', 'advisory', 'strategy', 'consultant', 'expert', 'services'],
            'real_estate': ['property', 'real estate', 'housing', 'rent', 'buy', 'home', 'apartment'],
            'marketing': ['marketing', 'advertising', 'brand', 'campaign', 'promotion', 'social media'],
            'manufacturing': ['manufacturing', 'production', 'factory', 'industrial', 'machinery'],
            'logistics': ['logistics', 'shipping', 'delivery', 'supply chain', 'transport', 'warehouse']
        }
        
        # Product/Service indicators
        self.product_indicators = [
            'product', 'service', 'solution', 'offering', 'feature', 
            'capability', 'tool', 'platform', 'system', 'software'
        ]
        
        # Pricing indicators
        self.pricing_keywords = [
            'price', 'pricing', 'cost', 'fee', 'subscription', 'plan', 
            'tier', 'package', 'bundle', 'free', 'trial', '$', '€', '£'
        ]
        
        # Target audience indicators
        self.audience_keywords = {
            'enterprise': ['enterprise', 'large business', 'corporation', 'fortune'],
            'sme': ['small business', 'sme', 'small and medium', 'startup'],
            'b2b': ['b2b', 'business to business', 'for businesses'],
            'b2c': ['b2c', 'business to consumer', 'for consumers', 'individual'],
            'non_profit': ['non-profit', 'nonprofit', 'ngo', 'charity'],
            'government': ['government', 'public sector', 'municipal', 'federal']
        }
    
    def extract_insights(self, content: WebsiteContent) -> Dict:
        """
        Extract comprehensive business insights from website content.
        
        Args:
            content: WebsiteContent object
        
        Returns:
            Dictionary with extracted business insights
        """
        if not content:
            return {}
        
        # Combine all text for analysis
        full_text = self._combine_text_content(content)
        text_lower = full_text.lower()
        
        insights = {
            'industry': self._extract_industry(text_lower, content),
            'product_type': self._extract_product_type(text_lower, content),
            'offerings': self._extract_offerings(text_lower, content),
            'value_proposition': self._extract_value_proposition(content),
            'pricing_model': self._extract_pricing_model(text_lower, content),
            'target_audience': self._extract_target_audience(text_lower, content),
            'tone': self._extract_tone(text_lower, content),
            'key_benefits': self._extract_benefits(content),
            'differentiators': self._extract_differentiators(content),
            'business_model': self._extract_business_model(text_lower, content),
            'geographic_focus': self._extract_geographic_focus(text_lower, content),
            'company_stage': self._extract_company_stage(text_lower, content)
        }
        
        return insights
    
    def _combine_text_content(self, content: WebsiteContent) -> str:
        """Combine all text content for analysis"""
        text_parts = [
            content.title,
            content.description,
            ' '.join(content.headings),
            ' '.join(content.paragraphs[:20])  # Limit paragraphs
        ]
        return ' '.join(text_parts)
    
    def _extract_industry(self, text: str, content: WebsiteContent) -> Dict:
        """Extract industry classification"""
        industry_scores = {}
        
        for industry, keywords in self.industry_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                industry_scores[industry] = score
        
        # Also check structured data
        for sd in content.structured_data:
            if sd.get('type') == 'json-ld':
                data = sd.get('data', {})
                if isinstance(data, dict):
                    # Check for industry in structured data
                    industry_field = data.get('industry') or data.get('@type')
                    if industry_field:
                        industry_scores[industry_field.lower()] = industry_scores.get(industry_field.lower(), 0) + 2
        
        if industry_scores:
            primary_industry = max(industry_scores.items(), key=lambda x: x[1])[0]
            return {
                'primary': primary_industry,
                'confidence': min(100, industry_scores[primary_industry] * 15),
                'alternatives': sorted(industry_scores.items(), key=lambda x: x[1], reverse=True)[:3]
            }
        
        return {'primary': 'general', 'confidence': 0}
    
    def _extract_product_type(self, text: str, content: WebsiteContent) -> List[str]:
        """Extract product/service types"""
        product_types = []
        
        # Check headings for product mentions
        for heading in content.headings[:10]:
            heading_lower = heading.lower()
            for indicator in self.product_indicators:
                if indicator in heading_lower:
                    # Extract product name
                    words = heading.split()
                    if len(words) > 1:
                        product_types.append(heading)
                    break
        
        # Check paragraphs for product descriptions
        for para in content.paragraphs[:10]:
            para_lower = para.lower()
            if any(indicator in para_lower for indicator in self.product_indicators):
                # Extract key phrases
                sentences = para.split('.')
                for sentence in sentences[:2]:
                    if any(indicator in sentence.lower() for indicator in self.product_indicators):
                        if len(sentence) > 20 and len(sentence) < 200:
                            product_types.append(sentence.strip())
        
        return list(set(product_types))[:5]  # Return top 5 unique
    
    def _extract_offerings(self, text: str, content: WebsiteContent) -> List[str]:
        """Extract specific offerings/services"""
        offerings = []
        
        # Look for service/product sections
        service_patterns = [
            r'we (?:offer|provide|deliver|supply) ([^.]{10,100})',
            r'our (?:services|products|solutions|offerings) (?:include|are) ([^.]{10,200})',
            r'(?:service|product|solution|offering):\s*([^.\n]{10,100})'
        ]
        
        for pattern in service_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            offerings.extend(matches)
        
        # Extract from headings
        for heading in content.headings:
            if any(keyword in heading.lower() for keyword in ['service', 'product', 'solution', 'feature']):
                offerings.append(heading)
        
        # Clean and deduplicate
        cleaned = []
        for offering in offerings:
            offering = offering.strip()
            if 10 < len(offering) < 200 and offering not in cleaned:
                cleaned.append(offering)
        
        return cleaned[:10]
    
    def _extract_value_proposition(self, content: WebsiteContent) -> str:
        """Extract value proposition"""
        # Check meta description first (often contains value prop)
        if content.description and len(content.description) > 30:
            return content.description
        
        # Check first h1 or h2
        for heading in content.headings[:3]:
            if len(heading) > 20 and len(heading) < 200:
                return heading
        
        # Check first substantial paragraph
        for para in content.paragraphs[:3]:
            if len(para) > 50 and len(para) < 300:
                return para
        
        return ""
    
    def _extract_pricing_model(self, text: str, content: WebsiteContent) -> Dict:
        """Extract pricing information"""
        pricing_info = {
            'has_pricing_page': False,
            'pricing_model': None,
            'price_indicators': [],
            'free_tier': False,
            'subscription': False
        }
        
        # Check for pricing keywords
        has_pricing = any(keyword in text for keyword in self.pricing_keywords)
        
        if has_pricing:
            # Check for pricing model
            if 'subscription' in text or 'monthly' in text or 'annual' in text:
                pricing_info['subscription'] = True
                pricing_info['pricing_model'] = 'subscription'
            
            if 'free' in text or 'trial' in text:
                pricing_info['free_tier'] = True
            
            # Extract price mentions
            price_pattern = r'\$[\d,]+|€[\d,]+|£[\d,]+|USD\s?[\d,]+|KES\s?[\d,]+'
            prices = re.findall(price_pattern, text)
            pricing_info['price_indicators'] = list(set(prices))[:5]
            
            # Check links for pricing page
            for link in content.links:
                if 'pricing' in link['url'].lower() or 'price' in link['url'].lower():
                    pricing_info['has_pricing_page'] = True
                    break
        
        return pricing_info
    
    def _extract_target_audience(self, text: str, content: WebsiteContent) -> Dict:
        """Extract target audience/ICP"""
        audience_matches = {}
        
        for audience_type, keywords in self.audience_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in text)
            if matches > 0:
                audience_matches[audience_type] = matches
        
        # Determine primary audience
        if audience_matches:
            primary = max(audience_matches.items(), key=lambda x: x[1])[0]
            return {
                'primary': primary,
                'all_matches': list(audience_matches.keys()),
                'confidence': min(100, audience_matches[primary] * 25)
            }
        
        return {'primary': 'general', 'all_matches': [], 'confidence': 0}
    
    def _extract_tone(self, text: str, content: WebsiteContent) -> str:
        """Extract business tone and positioning"""
        tone_indicators = {
            'professional': ['professional', 'enterprise', 'business', 'corporate', 'solution'],
            'casual': ['friendly', 'easy', 'simple', 'fun', 'relaxed'],
            'technical': ['technical', 'advanced', 'sophisticated', 'complex', 'engineered'],
            'innovative': ['innovative', 'cutting-edge', 'revolutionary', 'next-generation', 'breakthrough']
        }
        
        tone_scores = {}
        for tone, keywords in tone_indicators.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                tone_scores[tone] = score
        
        if tone_scores:
            return max(tone_scores.items(), key=lambda x: x[1])[0]
        
        return 'professional'  # Default
    
    def _extract_benefits(self, content: WebsiteContent) -> List[str]:
        """Extract key benefits"""
        benefits = []
        
        # Look for benefit sections
        benefit_keywords = ['benefit', 'advantage', 'why', 'advantage', 'gain', 'improve']
        
        for heading in content.headings:
            heading_lower = heading.lower()
            if any(keyword in heading_lower for keyword in benefit_keywords):
                # Get following content
                benefits.append(heading)
        
        # Extract from paragraphs with benefit language
        for para in content.paragraphs[:10]:
            para_lower = para.lower()
            if any(keyword in para_lower for keyword in ['benefit', 'advantage', 'help you', 'enable']):
                if 30 < len(para) < 200:
                    benefits.append(para)
        
        return benefits[:5]
    
    def _extract_differentiators(self, content: WebsiteContent) -> List[str]:
        """Extract unique selling points"""
        differentiators = []
        
        # Look for differentiator language
        diff_keywords = ['unique', 'only', 'first', 'exclusive', 'different', 'unlike', 'vs', 'versus']
        
        for para in content.paragraphs[:15]:
            para_lower = para.lower()
            if any(keyword in para_lower for keyword in diff_keywords):
                if 40 < len(para) < 250:
                    differentiators.append(para)
        
        return differentiators[:3]
    
    def _extract_business_model(self, text: str, content: WebsiteContent) -> str:
        """Extract business model"""
        if 'saas' in text or 'software as a service' in text:
            return 'SaaS'
        elif 'marketplace' in text or 'platform' in text:
            return 'Marketplace'
        elif 'ecommerce' in text or 'online store' in text:
            return 'E-commerce'
        elif 'consulting' in text or 'advisory' in text:
            return 'Consulting'
        elif 'subscription' in text:
            return 'Subscription'
        elif 'freemium' in text:
            return 'Freemium'
        else:
            return 'Service-based'
    
    def _extract_geographic_focus(self, text: str, content: WebsiteContent) -> List[str]:
        """Extract geographic focus"""
        countries = [
            'usa', 'united states', 'uk', 'united kingdom', 'canada', 'australia',
            'germany', 'france', 'spain', 'italy', 'netherlands', 'sweden',
            'kenya', 'nigeria', 'south africa', 'ghana', 'egypt', 'morocco',
            'india', 'china', 'japan', 'singapore', 'uae', 'saudi arabia'
        ]
        
        found_countries = []
        for country in countries:
            if country in text:
                found_countries.append(country.title())
        
        return list(set(found_countries))[:5]
    
    def _extract_company_stage(self, text: str, content: WebsiteContent) -> str:
        """Extract company stage (startup, growth, enterprise)"""
        if any(word in text for word in ['startup', 'founded', 'launched', 'new']):
            return 'Startup'
        elif any(word in text for word in ['enterprise', 'fortune', 'established', 'since']):
            return 'Enterprise'
        elif any(word in text for word in ['growing', 'expanding', 'scaling']):
            return 'Growth'
        else:
            return 'Established'


def extract_business_insights(content: WebsiteContent) -> Dict:
    """
    Convenience function to extract business insights.
    
    Args:
        content: WebsiteContent object
    
    Returns:
        Dictionary with business insights
    """
    extractor = BusinessInsightsExtractor()
    return extractor.extract_insights(content)

