"""
Context-Aware Lead Generator
Generates tailored leads based on business insights extracted from user's website.
"""

import os
import json
import logging
from typing import Dict, List, Optional
from generate_health_insurance import GeminiClient
from website_content_analyzer import analyze_website_content
from business_insights_extractor import extract_business_insights

logger = logging.getLogger(__name__)


class ContextAwareLeadGenerator:
    """
    Generates contextually relevant leads based on business insights.
    Uses extracted insights to tailor lead generation prompts and criteria.
    """
    
    def __init__(self):
        self.gemini_client = GeminiClient()
    
    def generate_contextual_leads(
        self,
        user_website_url: str,
        number_of_leads: int = 10,
        target_country: Optional[str] = None
    ) -> Dict:
        """
        Generate leads based on user's website analysis.
        
        Args:
            user_website_url: URL of user's business/product website
            number_of_leads: Number of leads to generate
            target_country: Optional country filter
        
        Returns:
            Dictionary with generated leads and insights
        """
        try:
            logger.info(f"Analyzing user website: {user_website_url}")
            
            # Step 1: Analyze website content
            website_content = analyze_website_content(user_website_url)
            
            if not website_content:
                raise Exception("Failed to analyze website content")
            
            # Step 2: Extract business insights
            insights = extract_business_insights(website_content)
            
            logger.info(f"Extracted insights: {insights.get('industry', {}).get('primary', 'unknown')}")
            
            # Step 3: Generate tailored leads
            leads = self._generate_tailored_leads(insights, website_content, number_of_leads, target_country)
            
            return {
                'success': True,
                'user_website': user_website_url,
                'insights': insights,
                'website_analysis': {
                    'title': website_content.title,
                    'description': website_content.description,
                    'industry': insights.get('industry', {}).get('primary', 'unknown'),
                    'value_proposition': insights.get('value_proposition', ''),
                    'target_audience': insights.get('target_audience', {}).get('primary', 'general')
                },
                'leads': leads,
                'generation_context': {
                    'based_on_industry': insights.get('industry', {}).get('primary'),
                    'target_audience': insights.get('target_audience', {}).get('primary'),
                    'business_model': insights.get('business_model', ''),
                    'geographic_focus': insights.get('geographic_focus', [])
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating contextual leads: {str(e)}")
            raise Exception(f"Failed to generate contextual leads: {str(e)}")
    
    def _generate_tailored_leads(
        self,
        insights: Dict,
        website_content,
        number: int,
        country: Optional[str]
    ) -> List[Dict]:
        """Generate leads tailored to business insights"""
        
        # Build context-aware prompt
        industry = insights.get('industry', {}).get('primary', 'general')
        target_audience = insights.get('target_audience', {}).get('primary', 'general')
        business_model = insights.get('business_model', '')
        offerings = insights.get('offerings', [])
        value_prop = insights.get('value_proposition', '')
        
        # Determine target country
        geo_focus = insights.get('geographic_focus', [])
        if not country and geo_focus:
            country = geo_focus[0]  # Use first geographic focus
        if not country:
            country = "USA"  # Default
        
        # Build tailored prompt
        prompt = self._build_tailored_prompt(
            industry=industry,
            target_audience=target_audience,
            business_model=business_model,
            offerings=offerings,
            value_proposition=value_prop,
            number=number,
            country=country,
            website_title=website_content.title
        )
        
        # Generate leads using Gemini
        result = self.gemini_client.generate_companies(
            industry=self._map_industry_for_generation(industry, insights),
            number=number,
            country=country
        )
        
        # Enhance leads with context
        enhanced_leads = self._enhance_leads_with_context(
            result.get('companies', []),
            insights,
            website_content
        )
        
        return enhanced_leads
    
    def _build_tailored_prompt(
        self,
        industry: str,
        target_audience: str,
        business_model: str,
        offerings: List[str],
        value_proposition: str,
        number: int,
        country: str,
        website_title: str
    ) -> str:
        """Build a tailored prompt for lead generation"""
        
        prompt = f"""
        Generate {number} highly relevant leads for a business that:
        
        Industry: {industry}
        Target Audience: {target_audience}
        Business Model: {business_model}
        Key Offerings: {', '.join(offerings[:3]) if offerings else 'Various services'}
        Value Proposition: {value_proposition[:200] if value_proposition else 'Not specified'}
        
        Focus on companies in {country} that would be ideal customers, partners, or prospects
        for this business. Prioritize companies that:
        1. Operate in complementary or related industries
        2. Serve similar target audiences ({target_audience})
        3. Could benefit from the offerings mentioned
        4. Are in a position to engage (growth stage, expanding, etc.)
        
        Return comprehensive company information including contact details.
        """
        
        return prompt
    
    def _map_industry_for_generation(self, industry: str, insights: Dict) -> str:
        """Map extracted industry to generation-friendly format"""
        industry_mapping = {
            'technology': 'technology',
            'healthcare': 'healthcare',
            'finance': 'financial services',
            'education': 'education',
            'ecommerce': 'e-commerce',
            'consulting': 'business consulting',
            'real_estate': 'real estate',
            'marketing': 'marketing and advertising',
            'manufacturing': 'manufacturing',
            'logistics': 'logistics and supply chain'
        }
        
        mapped = industry_mapping.get(industry, industry)
        
        # Add context from offerings if available
        offerings = insights.get('offerings', [])
        if offerings and len(offerings) > 0:
            # Try to extract more specific industry from first offering
            first_offering = offerings[0].lower()
            if 'saas' in first_offering or 'software' in first_offering:
                mapped = 'SaaS companies'
            elif 'fintech' in first_offering or 'payment' in first_offering:
                mapped = 'fintech'
        
        return mapped
    
    def _enhance_leads_with_context(
        self,
        leads: List[Dict],
        insights: Dict,
        website_content
    ) -> List[Dict]:
        """Enhance generated leads with context and relevance scoring"""
        
        industry = insights.get('industry', {}).get('primary', '')
        target_audience = insights.get('target_audience', {}).get('primary', '')
        business_model = insights.get('business_model', '')
        
        enhanced = []
        for lead in leads:
            # Add context relevance score
            relevance_score = self._calculate_relevance_score(lead, insights)
            
            # Add context tags
            context_tags = self._generate_context_tags(lead, insights)
            
            # Add match reasoning
            match_reasoning = self._generate_match_reasoning(lead, insights, website_content)
            
            enhanced_lead = {
                **lead,
                'context_relevance_score': relevance_score,
                'context_tags': context_tags,
                'match_reasoning': match_reasoning,
                'generated_for_industry': industry,
                'target_audience_match': self._check_audience_match(lead, target_audience)
            }
            
            enhanced.append(enhanced_lead)
        
        # Sort by relevance score
        enhanced.sort(key=lambda x: x.get('context_relevance_score', 0), reverse=True)
        
        return enhanced
    
    def _calculate_relevance_score(self, lead: Dict, insights: Dict) -> int:
        """Calculate how relevant a lead is to the user's business"""
        score = 50  # Base score
        
        # Industry match
        user_industry = insights.get('industry', {}).get('primary', '').lower()
        lead_industry = lead.get('key_products_services', '').lower()
        if user_industry in lead_industry or lead_industry in user_industry:
            score += 20
        
        # Target audience match
        user_audience = insights.get('target_audience', {}).get('primary', '').lower()
        if user_audience in ['b2b', 'enterprise']:
            # Prefer larger companies
            company_size = lead.get('company_size', '').lower()
            if '100+' in company_size or '1000+' in company_size:
                score += 15
        elif user_audience in ['b2c', 'individual']:
            # Prefer consumer-facing companies
            target_market = lead.get('target_market', '').lower()
            if 'consumer' in target_market or 'individual' in target_market:
                score += 15
        
        # Geographic match
        user_geo = insights.get('geographic_focus', [])
        if user_geo:
            lead_location = lead.get('headquarters_location', '').lower()
            if any(country.lower() in lead_location for country in user_geo):
                score += 10
        
        # Company size relevance
        company_size = lead.get('company_size', '')
        if company_size:
            if '100+' in company_size or '500+' in company_size:
                score += 5
        
        return min(100, score)
    
    def _generate_context_tags(self, lead: Dict, insights: Dict) -> List[str]:
        """Generate tags indicating why this lead is relevant"""
        tags = []
        
        industry = insights.get('industry', {}).get('primary', '')
        if industry:
            tags.append(f"Industry: {industry}")
        
        audience = insights.get('target_audience', {}).get('primary', '')
        if audience:
            tags.append(f"Audience: {audience}")
        
        business_model = insights.get('business_model', '')
        if business_model:
            tags.append(f"Model: {business_model}")
        
        return tags
    
    def _generate_match_reasoning(
        self,
        lead: Dict,
        insights: Dict,
        website_content
    ) -> str:
        """Generate explanation of why this lead is a good match"""
        reasons = []
        
        industry = insights.get('industry', {}).get('primary', '')
        if industry:
            reasons.append(f"Operates in {industry} sector")
        
        audience = insights.get('target_audience', {}).get('primary', '')
        if audience:
            reasons.append(f"Serves {audience} market")
        
        company_size = lead.get('company_size', '')
        if company_size:
            reasons.append(f"Company size: {company_size}")
        
        if lead.get('revenue_market_cap'):
            reasons.append(f"Revenue: {lead.get('revenue_market_cap')}")
        
        return "; ".join(reasons) if reasons else "Potential match based on business profile"
    
    def _check_audience_match(self, lead: Dict, target_audience: str) -> bool:
        """Check if lead matches target audience"""
        if not target_audience or target_audience == 'general':
            return True
        
        target_market = lead.get('target_market', '').lower()
        company_size = lead.get('company_size', '').lower()
        
        if target_audience == 'enterprise':
            return '1000+' in company_size or 'enterprise' in target_market
        elif target_audience == 'sme':
            return 'small' in target_market or '50+' in company_size
        elif target_audience == 'b2b':
            return 'b2b' in target_market or 'business' in target_market
        elif target_audience == 'b2c':
            return 'consumer' in target_market or 'individual' in target_market
        
        return True


def generate_leads_from_website(
    website_url: str,
    number: int = 10,
    country: Optional[str] = None
) -> Dict:
    """
    Convenience function to generate leads from website.
    
    Args:
        website_url: User's business website URL
        number: Number of leads to generate
        country: Optional country filter
    
    Returns:
        Dictionary with leads and insights
    """
    generator = ContextAwareLeadGenerator()
    return generator.generate_contextual_leads(website_url, number, country)

