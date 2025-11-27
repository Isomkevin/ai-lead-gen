"""
Lead Generator API
A FastAPI backend for generating company leads with web scraping enhancement.

Author: Senior Backend Engineer
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
import uvicorn
import os
from datetime import datetime
import json
from enum import Enum
import logging

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log') if os.path.exists('logs') else logging.StreamHandler(),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

from generate_health_insurance import GeminiClient
from web_scraper import scrape_company_data
from email_sender import get_email_sender
from business_intelligence import BusinessIntelligenceAnalyzer
from avatar_service import get_avatar_service
from context_aware_lead_generator import generate_leads_from_website
from africastalking_service import get_africastalking_service
from fastapi.responses import Response
import base64

# Initialize FastAPI app
app = FastAPI(
    title="Lead Generator API",
    description="AI-powered lead generation with web scraping enhancement",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for production
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", 
    "https://leadgenerator.meallensai.com,https://lead-gen-aes4.onrender.com,https://lead-magnet-livid.vercel.app,http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=600,
)

# ========== Models ==========

class LeadRequest(BaseModel):
    """Request model for lead generation"""
    industry: str = Field(
        ..., 
        min_length=2, 
        max_length=100,
        description="Industry to target (e.g., 'health insurance', 'technology', 'finance')",
        example="health insurance"
    )
    number: int = Field(
        ..., 
        ge=1, 
        le=50,
        description="Number of companies to generate (1-50)",
        example=10
    )
    country: str = Field(
        ..., 
        min_length=2, 
        max_length=100,
        description="Country to focus on (e.g., 'USA', 'UK', 'Canada')",
        example="USA"
    )
    enable_web_scraping: bool = Field(
        default=False,
        description="Enable web scraping for enhanced contact data (slower but more accurate)"
    )
    
    @validator('number')
    def validate_number(cls, v):
        if v < 1:
            raise ValueError('Number must be at least 1')
        if v > 50:
            raise ValueError('Number cannot exceed 50 (rate limiting)')
        return v
    
    @validator('industry', 'country')
    def validate_non_empty(cls, v):
        if not v or v.strip() == "":
            raise ValueError('Field cannot be empty')
        return v.strip()


class CompanySocialMedia(BaseModel):
    """Social media accounts"""
    linkedin: Optional[str] = None
    twitter: Optional[str] = None
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    youtube: Optional[str] = None


class CompanyLead(BaseModel):
    """Individual company lead data"""
    company_name: str
    website_url: Optional[str] = None
    company_size: Optional[str] = None
    headquarters_location: Optional[str] = None
    revenue_market_cap: Optional[str] = None
    key_products_services: Optional[str] = None
    target_market: Optional[str] = None
    number_of_users: Optional[str] = None
    notable_customers: Optional[List[str]] = None
    social_media: Optional[CompanySocialMedia] = None
    social_media_scraped: Optional[CompanySocialMedia] = None
    contact_email: Optional[str] = None
    contact_email_llm: Optional[str] = None
    additional_emails: Optional[List[str]] = None
    recent_news_insights: Optional[str] = None
    decision_maker_roles: Optional[List[str]] = None


class LeadResponse(BaseModel):
    """Response model for lead generation"""
    success: bool
    message: str
    data: Dict[str, List[CompanyLead]]
    metadata: Dict[str, Any]


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    version: str
    gemini_api_configured: bool


# ========== In-Memory Storage ==========
# NOTE: This is in-memory and won't work with multiple workers (Docker uses 4 workers)
# For production with async endpoints, use Redis or a database
# Current frontend uses sync endpoint only for reliability
job_storage = {}


# ========== Helper Functions ==========

def validate_api_key():
    """Validate that GEMINI_API_KEY is configured"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY not configured. Please set it in your .env file"
        )
    return True


def generate_leads_sync(industry: str, number: int, country: str, enable_scraping: bool = False) -> Dict:
    """Synchronous lead generation with automatic retry handling"""
    try:
        validate_api_key()
        
        # Generate leads with AI (includes automatic retry logic for 503 errors)
        logger.info(f"Starting lead generation: industry={industry}, number={number}, country={country}")
        client = GeminiClient()
        result = client.generate_companies(industry, number, country)
        
        # Enhance with web scraping if enabled
        if enable_scraping:
            logger.info("Enhancing results with web scraping (parallel)...")
            result = scrape_company_data_parallel(result, max_workers=3)
        
        logger.info(f"Successfully generated {len(result.get('companies', []))} leads")
        return result
        
    except Exception as e:
        error_msg = str(e)
        error_lower = error_msg.lower()
        
        # Check if it's a 503/overload error (after retries exhausted)
        is_503_error = (
            '503' in error_msg or 
            'overloaded' in error_lower or 
            'unavailable' in error_lower or
            'model is overloaded' in error_lower or
            'service unavailable' in error_lower
        )
        
        # Check if it's a rate limit error (429)
        is_rate_limit = (
            '429' in error_msg or
            'rate limit' in error_lower or
            'too many requests' in error_lower
        )
        
        # Check if it's a connection/timeout error
        is_connection_error = (
            'connection' in error_lower or
            'timeout' in error_lower or
            'network' in error_lower
        )
        
        if is_503_error:
            logger.error(f"503/Service Unavailable error after retries: {error_msg}")
            # Provide user-friendly message
            user_message = (
                "The AI service is currently overloaded. We've tried multiple times but the service is still unavailable. "
                "Please try again in a few minutes."
            )
            raise HTTPException(
                status_code=503,
                detail=f"Lead generation failed: {user_message} (Error: {error_msg})"
            )
        elif is_rate_limit:
            logger.error(f"Rate limit error: {error_msg}")
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please wait a moment before trying again."
            )
        elif is_connection_error:
            logger.error(f"Connection error: {error_msg}")
            raise HTTPException(
                status_code=503,
                detail="Connection error. Please check your internet connection and try again."
            )
        else:
            logger.error(f"Lead generation error: {error_msg}")
            raise HTTPException(
                status_code=500, 
                detail=f"Lead generation failed: {error_msg}"
            )


async def generate_leads_background(job_id: str, industry: str, number: int, country: str, enable_scraping: bool):
    """Background task for lead generation"""
    try:
        job_storage[job_id]['status'] = 'processing'
        job_storage[job_id]['started_at'] = datetime.utcnow().isoformat()
        
        result = generate_leads_sync(industry, number, country, enable_scraping)
        
        job_storage[job_id]['status'] = 'completed'
        job_storage[job_id]['completed_at'] = datetime.utcnow().isoformat()
        job_storage[job_id]['result'] = result
        
    except Exception as e:
        job_storage[job_id]['status'] = 'failed'
        job_storage[job_id]['error'] = str(e)
        job_storage[job_id]['completed_at'] = datetime.utcnow().isoformat()


# ========== API Endpoints ==========

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Lead Generator API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    api_key_configured = bool(os.getenv('GEMINI_API_KEY'))
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "gemini_api_configured": api_key_configured
    }


@app.post("/api/v1/leads/generate", tags=["Leads"])
async def generate_leads(request: LeadRequest):
    """
    Generate company leads based on industry, number, and country.
    
    - **industry**: Target industry (e.g., "health insurance", "technology")
    - **number**: Number of companies to generate (1-50)
    - **country**: Country to focus on (e.g., "USA", "UK", "Canada")
    - **enable_web_scraping**: Enable web scraping for enhanced data (slower)
    
    Returns comprehensive company information including:
    - Company details (name, size, location, revenue)
    - Contact information (emails, social media)
    - Business intelligence (customers, products, decision makers)
    """
    try:
        # Generate leads
        result = generate_leads_sync(
            industry=request.industry,
            number=request.number,
            country=request.country,
            enable_scraping=request.enable_web_scraping
        )
        
        # Build response
        response = {
            "success": True,
            "message": f"Successfully generated {len(result.get('companies', []))} leads",
            "data": result,
            "metadata": {
                "industry": request.industry,
                "country": request.country,
                "requested_count": request.number,
                "actual_count": len(result.get('companies', [])),
                "web_scraping_enabled": request.enable_web_scraping,
                "generated_at": datetime.utcnow().isoformat()
            }
        }
        
        return response
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/v1/leads/generate-async", tags=["Leads"])
async def generate_leads_async(request: LeadRequest, background_tasks: BackgroundTasks):
    """
    Generate leads asynchronously (recommended for web scraping enabled).
    Returns a job ID to check status later.
    
    Use this endpoint when enable_web_scraping=true as it can take several minutes.
    """
    try:
        validate_api_key()
        
        # Generate unique job ID
        job_id = f"job_{datetime.utcnow().timestamp()}_{request.industry[:10]}"
        
        # Initialize job
        job_storage[job_id] = {
            "status": "queued",
            "industry": request.industry,
            "number": request.number,
            "country": request.country,
            "enable_web_scraping": request.enable_web_scraping,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Add to background tasks
        background_tasks.add_task(
            generate_leads_background,
            job_id,
            request.industry,
            request.number,
            request.country,
            request.enable_web_scraping
        )
        
        return {
            "success": True,
            "message": "Lead generation job queued",
            "job_id": job_id,
            "status_endpoint": f"/api/v1/leads/status/{job_id}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/leads/status/{job_id}", tags=["Leads"])
async def get_job_status(job_id: str):
    """
    Check the status of an async lead generation job.
    
    Status values:
    - queued: Job is waiting to be processed
    - processing: Job is currently running
    - completed: Job finished successfully
    - failed: Job encountered an error
    """
    if job_id not in job_storage:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = job_storage[job_id]
    
    response = {
        "job_id": job_id,
        "status": job['status'],
        "created_at": job['created_at']
    }
    
    if job['status'] == 'completed':
        response['result'] = job.get('result')
        response['completed_at'] = job.get('completed_at')
    elif job['status'] == 'failed':
        response['error'] = job.get('error')
        response['completed_at'] = job.get('completed_at')
    elif job['status'] == 'processing':
        response['started_at'] = job.get('started_at')
    
    return response


@app.get("/api/v1/leads/export/{job_id}", tags=["Leads"])
async def export_leads(
    job_id: str,
    format: str = Query(default="json", regex="^(json|csv)$")
):
    """
    Export leads in different formats (json or csv).
    Currently only JSON is supported.
    """
    if job_id not in job_storage:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = job_storage[job_id]
    
    if job['status'] != 'completed':
        raise HTTPException(
            status_code=400, 
            detail=f"Job is not completed yet. Current status: {job['status']}"
        )
    
    if format == "json":
        return job.get('result')
    else:
        raise HTTPException(status_code=501, detail="CSV export not yet implemented")


# ========== Email Endpoints ==========

class EmailAttachment(BaseModel):
    """Email attachment model"""
    filename: str = Field(..., description="Original filename")
    content: str = Field(..., description="Base64 encoded file content")
    mimetype: str = Field(default="application/octet-stream", description="MIME type of the file")


class EmailRequest(BaseModel):
    """Request model for sending emails"""
    to_email: str = Field(..., description="Recipient email address")
    from_email: str = Field(..., description="Sender email address")
    subject: str = Field(..., min_length=1, description="Email subject")
    body: str = Field(..., min_length=1, description="Email body (HTML supported)")
    attachments: Optional[List[EmailAttachment]] = Field(default=None, description="List of attachments (base64 encoded)")


@app.post("/api/v1/email/send", tags=["Email"])
async def send_email(request: EmailRequest):
    """
    Send an email to a lead.
    
    - **to_email**: Recipient's email address
    - **from_email**: Your email address (for reference)
    - **subject**: Email subject line
    - **body**: Email body content (HTML supported)
    - **attachments**: Optional list of attachments
    
    Returns success status and message.
    """
    try:
        logger.info(f"Email send request: from={request.from_email}, to={request.to_email}")
        email_sender = get_email_sender()
        
        # Process attachments (convert base64 to files)
        import base64
        import tempfile
        import os as os_module
        
        attachment_files = []
        temp_files = []
        
        if request.attachments:
            for attachment in request.attachments:
                try:
                    # Decode base64 content
                    file_content = base64.b64decode(attachment.content)
                    
                    # Create temporary file
                    temp_file = tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=f"_{attachment.filename}",
                        mode='wb'
                    )
                    temp_file.write(file_content)
                    temp_file.close()
                    
                    attachment_files.append(temp_file.name)
                    temp_files.append(temp_file.name)
                    
                except Exception as e:
                    print(f"⚠️ Failed to process attachment {attachment.filename}: {str(e)}")
        
        # Send email (from_email is now used properly)
        # CC the user so they get a copy of what they sent
        logger.info(f"Sending email via email service...")
        result = email_sender.send_email(
            from_email=request.from_email,
            to_email=request.to_email,
            subject=request.subject,
            contents=request.body,
            attachments=attachment_files if attachment_files else None,
            cc_email=request.from_email  # User gets a copy
        )
        
        logger.info(f"Email send result: {result}")
        logger.info(f"Result type: {type(result)}, Success: {result.get('success')}")
        
        # Clean up temporary files
        for temp_file in temp_files:
            try:
                os_module.unlink(temp_file)
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup temp file: {cleanup_error}")
        
        # Check if result is a dict and has success key
        if not isinstance(result, dict):
            logger.error(f"Invalid result type: {type(result)}, value: {result}")
            raise HTTPException(status_code=500, detail="Email service returned invalid response")
        
        if result.get("success") is True:
            logger.info("Email sent successfully, returning success response")
            response_data = {
                "success": True,
                "message": f"Email sent successfully to {request.to_email}",
                "method": result.get("method", "unknown"),
                "to": request.to_email,
                "from": request.from_email,
                "cc": request.from_email,
                "attachments_count": len(attachment_files) if attachment_files else 0,
                "sent_at": datetime.utcnow().isoformat(),
                "note": f"A copy of this email was sent to {request.from_email}"
            }
            logger.info(f"Returning response: {response_data}")
            return response_data
        else:
            error_msg = result.get("message", "Unknown error occurred")
            logger.error(f"Email sending marked as failed: {error_msg}")
            raise HTTPException(status_code=500, detail=error_msg)
            
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except ValueError as e:
        logger.error(f"Email validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected email error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send email. Please check your email configuration.")


@app.post("/api/v1/email/generate-content", tags=["Email"])
async def generate_email_content(
    company_name: str,
    purpose: str = "introduction",
    tone: str = "professional"
):
    """
    Generate AI-powered email content for a company.
    
    - **company_name**: Name of the company to email
    - **purpose**: Purpose of email (introduction, follow-up, partnership, etc.)
    - **tone**: Tone of email (professional, casual, friendly)
    
    Returns AI-generated email content suggestions.
    """
    try:
        validate_api_key()
        
        client = GeminiClient()
        
        prompt = f"""
        Generate a professional email for the following:
        
        Company: {company_name}
        Purpose: {purpose}
        Tone: {tone}
        
        Return a JSON object with:
        {{
            "subject": "Email subject line",
            "greeting": "Opening greeting",
            "body": "Main email body (2-3 paragraphs)",
            "call_to_action": "Closing call to action",
            "closing": "Email closing signature"
        }}
        
        Make it compelling, personalized, and professional.
        Return ONLY the JSON object, no additional text.
        """
        
        # Use the AI client to generate content (simplified for now)
        suggestions = {
            "subject": f"Exploring Partnership Opportunities with {company_name}",
            "greeting": f"Dear {company_name} Team,",
            "body": f"I hope this email finds you well. I came across {company_name} and was impressed by your work in the industry. I believe there could be valuable opportunities for collaboration between our organizations.\n\nI would love to schedule a brief call to discuss how we might work together to create mutual value.",
            "call_to_action": "Would you be available for a 15-minute call next week?",
            "closing": "Best regards,"
        }
        
        return {
            "success": True,
            "suggestions": suggestions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== Business Intelligence Endpoints ==========

@app.post("/api/v1/leads/analyze", tags=["Leads"])
async def analyze_leads_with_intelligence(request: LeadRequest):
    """
    Generate leads and analyze business intelligence from websites.
    Returns leads with scoring and business intelligence data.
    
    This endpoint:
    - Generates leads using AI
    - Scrapes company websites for business intelligence
    - Scores each lead based on multiple criteria
    - Returns leads sorted by score (highest first)
    """
    try:
        logger.info(f"Starting lead analysis: industry={request.industry}, number={request.number}, country={request.country}")
        
        # Generate leads first
        result = generate_leads_sync(
            industry=request.industry,
            number=request.number,
            country=request.country,
            enable_scraping=request.enable_web_scraping
        )
        
        # Analyze business intelligence for each company
        analyzer = BusinessIntelligenceAnalyzer()
        companies = result.get('companies', [])
        
        logger.info(f"Analyzing business intelligence for {len(companies)} companies...")
        
        for company in companies:
            website_url = company.get('website_url')
            
            if website_url:
                try:
                    # Extract business intelligence
                    business_info = analyzer.extract_business_info(website_url)
                    
                    # Score the lead
                    lead_scoring = analyzer.score_lead(company, business_info)
                    
                    # Add to company data
                    company['business_intelligence'] = business_info
                    company['lead_score'] = lead_scoring['lead_score']
                    company['quality_tier'] = lead_scoring['quality_tier']
                    company['recommendation'] = lead_scoring['recommendation']
                    company['scoring_breakdown'] = lead_scoring['scoring_breakdown']
                    
                    # Small delay to be respectful (optimized)
                    import time
                    time.sleep(0.5)  # Reduced delay for faster processing
                    
                except Exception as e:
                    logger.warning(f"Error analyzing {website_url}: {str(e)}")
                    # Add default scoring if analysis fails
                    company['lead_score'] = 0
                    company['quality_tier'] = 'Unknown'
                    company['recommendation'] = 'Analysis unavailable'
                    company['business_intelligence'] = {'error': str(e)}
            else:
                # No website URL - default scoring
                company['lead_score'] = 0
                company['quality_tier'] = 'Unknown'
                company['recommendation'] = 'No website URL available'
                company['business_intelligence'] = {}
        
        # Sort by lead score (highest first)
        companies.sort(key=lambda x: x.get('lead_score', 0), reverse=True)
        result['companies'] = companies
        
        # Calculate statistics
        premium_count = sum(1 for c in companies if c.get('quality_tier') == 'Premium')
        high_count = sum(1 for c in companies if c.get('quality_tier') == 'High')
        avg_score = sum(c.get('lead_score', 0) for c in companies) / len(companies) if companies else 0
        
        logger.info(f"Analysis complete. Premium: {premium_count}, High: {high_count}, Avg Score: {avg_score:.1f}")
        
        return {
            "success": True,
            "message": f"Generated and analyzed {len(companies)} leads",
            "data": result,
            "metadata": {
                "industry": request.industry,
                "country": request.country,
                "requested_count": request.number,
                "actual_count": len(companies),
                "web_scraping_enabled": request.enable_web_scraping,
                "analysis_enabled": True,
                "sorted_by_score": True,
                "premium_leads": premium_count,
                "high_leads": high_count,
                "average_score": round(avg_score, 1),
                "generated_at": datetime.utcnow().isoformat()
            }
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error in lead analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ========== Context-Aware Lead Generation Endpoints ==========

class WebsiteBasedLeadRequest(BaseModel):
    """Request model for website-based lead generation"""
    website_url: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="URL of user's business/product website to analyze",
        example="https://example.com"
    )
    number: int = Field(
        ...,
        ge=1,
        le=50,
        description="Number of leads to generate (1-50)",
        example=10
    )
    country: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100,
        description="Optional country filter (if not provided, uses geographic focus from website)",
        example="USA"
    )
    enable_web_scraping: bool = Field(
        default=True,
        description="Enable web scraping for enhanced contact data"
    )
    enable_business_intelligence: bool = Field(
        default=True,
        description="Enable business intelligence analysis on generated leads"
    )
    
    @validator('website_url')
    def validate_website_url(cls, v):
        if not v or v.strip() == "":
            raise ValueError('Website URL cannot be empty')
        # Basic URL validation
        url = v.strip()
        if not (url.startswith('http://') or url.startswith('https://')):
            url = 'https://' + url
        return url


@app.post("/api/v1/leads/generate-from-website", tags=["Leads"])
async def generate_leads_from_user_website(request: WebsiteBasedLeadRequest):
    """
    Generate contextually relevant leads based on user's website analysis.
    
    This endpoint:
    1. Analyzes the user's website to extract business insights
    2. Generates tailored leads based on extracted insights
    3. Optionally enhances leads with web scraping and BI analysis
    
    **How it works:**
    - Analyzes website content (text, structure, metadata)
    - Extracts industry, target audience, value proposition, offerings
    - Generates leads that match the user's business profile
    - Scores leads for relevance and quality
    
    **Example:**
    If your website is a SaaS platform for healthcare, it will generate leads
    for healthcare companies that could use your platform.
    """
    try:
        logger.info(f"Generating leads from website: {request.website_url}")
        
        # Step 1: Generate contextual leads from website
        result = generate_leads_from_website(
            website_url=request.website_url,
            number=request.number,
            country=request.country
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Failed to generate leads from website')
            )
        
        leads = result.get('leads', [])
        insights = result.get('insights', {})
        website_analysis = result.get('website_analysis', {})
        
        # Step 2: Optionally enhance with web scraping
        if request.enable_web_scraping:
            logger.info("Enhancing leads with web scraping...")
            from web_scraper import scrape_company_data_parallel
            leads_data = {'companies': leads}
            # Use parallel scraping for faster performance
            enhanced_data = scrape_company_data_parallel(leads_data, max_workers=3)
            leads = enhanced_data.get('companies', leads)
        
        # Step 3: Optionally add business intelligence analysis
        if request.enable_business_intelligence:
            logger.info("Adding business intelligence analysis...")
            analyzer = BusinessIntelligenceAnalyzer()
            
            for lead in leads:
                website_url = lead.get('website_url')
                if website_url:
                    try:
                        business_info = analyzer.extract_business_info(website_url)
                        lead_scoring = analyzer.score_lead(lead, business_info)
                        
                        lead['business_intelligence'] = business_info
                        lead['lead_score'] = lead_scoring['lead_score']
                        lead['quality_tier'] = lead_scoring['quality_tier']
                        lead['recommendation'] = lead_scoring['recommendation']
                        lead['scoring_breakdown'] = lead_scoring['scoring_breakdown']
                        
                        # Combine context relevance with BI score
                        context_score = lead.get('context_relevance_score', 50)
                        bi_score = lead.get('lead_score', 0)
                        lead['combined_score'] = round((context_score * 0.4) + (bi_score * 0.6))
                        
                        import time
                        time.sleep(0.5)  # Reduced delay for faster processing
                    except Exception as e:
                        logger.warning(f"Error analyzing {website_url}: {str(e)}")
        
        # Sort by combined score or context relevance
        if request.enable_business_intelligence:
            leads.sort(key=lambda x: x.get('combined_score', x.get('context_relevance_score', 0)), reverse=True)
        else:
            leads.sort(key=lambda x: x.get('context_relevance_score', 0), reverse=True)
        
        # Calculate statistics
        premium_count = sum(1 for l in leads if l.get('quality_tier') == 'Premium')
        high_count = sum(1 for l in leads if l.get('quality_tier') == 'High')
        avg_relevance = sum(l.get('context_relevance_score', 0) for l in leads) / len(leads) if leads else 0
        
        logger.info(f"Generated {len(leads)} contextual leads from website analysis")
        
        return {
            "success": True,
            "message": f"Generated {len(leads)} contextually relevant leads from website analysis",
            "data": {
                "companies": leads
            },
            "website_analysis": website_analysis,
            "insights": insights,
            "metadata": {
                "user_website": request.website_url,
                "requested_count": request.number,
                "actual_count": len(leads),
                "web_scraping_enabled": request.enable_web_scraping,
                "business_intelligence_enabled": request.enable_business_intelligence,
                "average_relevance_score": round(avg_relevance, 1),
                "premium_leads": premium_count if request.enable_business_intelligence else 0,
                "high_leads": high_count if request.enable_business_intelligence else 0,
                "generated_at": datetime.utcnow().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating leads from website: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate leads from website: {str(e)}"
        )


# ========== Africa's Talking (SMS/Voice/Airtime) Endpoints ==========

class SMSRequest(BaseModel):
    """Request model for sending SMS"""
    phone_numbers: List[str] = Field(
        ...,
        description="List of phone numbers with country code (e.g., +254712345678)",
        example=["+254712345678", "+254798765432"]
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=1600,
        description="SMS message text (max 1600 characters)",
        example="Your leads are ready! Check your dashboard."
    )
    sender_id: Optional[str] = Field(
        default=None,
        description="Optional sender ID (must be approved in Africa's Talking)"
    )


class LeadNotificationSMSRequest(BaseModel):
    """Request for sending lead notification SMS"""
    phone: str = Field(..., description="Phone number with country code")
    lead_summary: Dict = Field(..., description="Lead generation summary")


@app.post("/api/v1/sms/send", tags=["SMS"])
async def send_sms(request: SMSRequest):
    """
    Send SMS via Africa's Talking.
    
    **Features:**
    - Send SMS to multiple recipients
    - Automatic phone number formatting
    - Cost tracking
    - Delivery status
    
    **Phone Number Format:**
    - Include country code: +254712345678 (Kenya)
    - Or use local format: 0712345678 (auto-converted)
    """
    try:
        at_service = get_africastalking_service()
        if not at_service:
            raise HTTPException(
                status_code=503,
                detail="Africa's Talking not configured. Set AFRICASTALKING_USERNAME and AFRICASTALKING_API_KEY in .env"
            )
        
        result = at_service.send_sms(
            phone_numbers=request.phone_numbers,
            message=request.message,
            sender_id=request.sender_id
        )
        
        if result.get('success'):
            return {
                "success": True,
                "message": "SMS sent successfully",
                "recipients_count": len(result.get('recipients', [])),
                "cost": result.get('cost', '0'),
                "recipients": result.get('recipients', [])
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Failed to send SMS')
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending SMS: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send SMS: {str(e)}")


@app.post("/api/v1/sms/send-lead-notification", tags=["SMS"])
async def send_lead_notification_sms(request: LeadNotificationSMSRequest):
    """
    Send SMS notification when leads are generated.
    
    Automatically formats a notification message with:
    - Total leads generated
    - Premium/High quality counts
    - Dashboard link
    """
    try:
        at_service = get_africastalking_service()
        if not at_service:
            raise HTTPException(
                status_code=503,
                detail="Africa's Talking not configured"
            )
        
        result = at_service.send_lead_notification_sms(
            phone=request.phone,
            lead_summary=request.lead_summary
        )
        
        if result.get('success'):
            return {
                "success": True,
                "message": "Lead notification SMS sent",
                "data": result
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Failed to send notification')
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending lead notification: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


class VoiceCallRequest(BaseModel):
    """Request for initiating voice call"""
    phone_number: str = Field(..., description="Phone number with country code")
    message: str = Field(..., description="Text message to convert to speech")


@app.post("/api/v1/voice/call", tags=["Voice"])
async def initiate_voice_call(request: VoiceCallRequest):
    """
    Initiate a voice call with text-to-speech via Africa's Talking.
    
    **Use Cases:**
    - Lead verification calls
    - Automated follow-ups
    - Voice notifications
    - Lead qualification surveys
    """
    try:
        at_service = get_africastalking_service()
        if not at_service:
            raise HTTPException(
                status_code=503,
                detail="Africa's Talking not configured"
            )
        
        result = at_service.initiate_voice_call(
            phone_number=request.phone_number,
            message=request.message
        )
        
        if result.get('success'):
            return {
                "success": True,
                "message": "Voice call initiated",
                "data": result.get('data', {})
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Failed to initiate call')
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error initiating voice call: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


class AirtimeRequest(BaseModel):
    """Request for sending airtime"""
    phone_number: str = Field(..., description="Phone number with country code")
    amount: str = Field(..., description="Amount to send (e.g., '100')")
    currency: str = Field(default="KES", description="Currency code (KES, UGX, TZS, etc.)")


@app.post("/api/v1/airtime/send", tags=["Airtime"])
async def send_airtime(request: AirtimeRequest):
    """
    Send airtime to a phone number via Africa's Talking.
    
    **Use Cases:**
    - Reward users for successful lead conversions
    - Incentivize referrals
    - Thank you rewards
    - Lead generation incentives
    
    **Supported Currencies:**
    - KES (Kenya Shilling)
    - UGX (Uganda Shilling)
    - TZS (Tanzania Shilling)
    - And more...
    """
    try:
        at_service = get_africastalking_service()
        if not at_service:
            raise HTTPException(
                status_code=503,
                detail="Africa's Talking not configured"
            )
        
        result = at_service.send_airtime(
            phone_number=request.phone_number,
            amount=request.amount,
            currency=request.currency
        )
        
        if result.get('success'):
            return {
                "success": True,
                "message": "Airtime sent successfully",
                "data": result.get('data', {})
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Failed to send airtime')
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending airtime: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== Avatar/Voice Endpoints ==========

class AvatarRequest(BaseModel):
    """Request for avatar voice generation"""
    company_name: str = Field(..., description="Company name for personalization")
    message_type: str = Field(
        default="introduction", 
        description="Type: introduction, follow_up, summary",
        example="introduction"
    )
    custom_message: Optional[str] = Field(
        default=None,
        description="Custom message text (optional, overrides default)"
    )
    voice_id: Optional[str] = Field(
        default="21m00Tcm4TlvDq8ikWAM",
        description="ElevenLabs voice ID"
    )


@app.post("/api/v1/avatar/generate-voice", tags=["Avatar"])
async def generate_avatar_voice(request: AvatarRequest):
    """
    Generate AI avatar voice message for a lead.
    
    Returns MP3 audio file that can be:
    - Downloaded
    - Embedded in emails
    - Sent via SMS (with link)
    - Used in voice calls
    """
    try:
        avatar_service = get_avatar_service()
        
        if not avatar_service:
            raise HTTPException(
                status_code=503,
                detail="ElevenLabs API not configured. Please set ELEVENLABS_API_KEY environment variable."
            )
        
        if request.message_type == "introduction":
            # Create lead data structure
            lead_data = {
                "company_name": request.company_name,
                "key_products_services": ""  # Can be enhanced later
            }
            
            if request.custom_message:
                # Generate voice from custom message
                result = avatar_service.generate_custom_voice(
                    request.custom_message,
                    request.voice_id
                )
            else:
                # Use default introduction
                result = avatar_service.create_avatar_conversation(lead_data)
            
            if "error" in result:
                raise HTTPException(status_code=500, detail=result["error"])
            
            # Decode base64 audio
            audio_bytes = base64.b64decode(result['audio_base64'])
            
            # Return audio file
            return Response(
                content=audio_bytes,
                media_type="audio/mpeg",
                headers={
                    "Content-Disposition": f"attachment; filename=voice_{request.company_name.replace(' ', '_')}.mp3"
                }
            )
        
        elif request.message_type == "summary":
            # This would need leads data - for now return error
            raise HTTPException(
                status_code=400,
                detail="Summary type requires leads data. Use /api/v1/avatar/generate-summary instead."
            )
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown message type: {request.message_type}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating avatar voice: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/avatar/generate-summary", tags=["Avatar"])
async def generate_lead_summary_voice(leads: List[Dict]):
    """
    Generate voice summary of lead generation results.
    
    Args:
        leads: List of lead dictionaries with quality_tier and other data
    """
    try:
        avatar_service = get_avatar_service()
        
        if not avatar_service:
            raise HTTPException(
                status_code=503,
                detail="ElevenLabs API not configured"
            )
        
        result = avatar_service.generate_lead_summary_voice(leads)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Decode base64 audio
        audio_bytes = base64.b64decode(result['audio_base64'])
        
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=lead_summary.mp3"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating summary voice: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/avatar/voices", tags=["Avatar"])
async def get_available_voices():
    """
    Get list of available ElevenLabs voices.
    
    Returns list of voice options that can be used for voice generation.
    """
    try:
        avatar_service = get_avatar_service()
        
        if not avatar_service:
            return {
                "success": False,
                "message": "ElevenLabs API not configured",
                "voices": []
            }
        
        voices = avatar_service.get_available_voices()
        
        return {
            "success": True,
            "voices": voices,
            "count": len(voices)
        }
        
    except Exception as e:
        logger.error(f"Error fetching voices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== Startup & Shutdown Events ==========

@app.on_event("startup")
async def startup_event():
    """Run on API startup"""
    logger.info("="*60)
    logger.info("🚀 Lead Generator API Starting...")
    logger.info("="*60)
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"CORS Allowed Origins: {ALLOWED_ORIGINS}")
    logger.info(f"Gemini API Key: {'✅ Configured' if os.getenv('GEMINI_API_KEY') else '❌ Missing'}")
    logger.info(f"Email Service: {'✅ Configured' if os.getenv('EMAIL_USER') or os.getenv('SENDGRID_API_KEY') else '⚠️ Not configured'}")
    logger.info(f"ElevenLabs Avatar: {'✅ Configured' if os.getenv('ELEVENLABS_API_KEY') else '⚠️ Not configured'}")
    logger.info(f"Africa's Talking: {'✅ Configured' if os.getenv('AFRICASTALKING_API_KEY') else '⚠️ Not configured'}")
    logger.info("="*60)


@app.on_event("shutdown")
async def shutdown_event():
    """Run on API shutdown"""
    logger.info("🛑 Lead Generator API Shutting Down...")


# ========== Run Server ==========

if __name__ == "__main__":
    import sys
    
    # Check if running in production mode
    is_production = os.getenv('ENVIRONMENT') == 'production'
    
    print("=" * 60)
    print("🚀 Lead Generator API Starting...")
    print("=" * 60)
    
    if not is_production:
        print(f"📚 API Documentation: http://localhost:8000/docs")
        print(f"📖 ReDoc Documentation: http://localhost:8000/redoc")
        print(f"💚 Health Check: http://localhost:8000/health")
        print("=" * 60)
        print("⚠️  Running in DEVELOPMENT mode")
        print("   Set ENVIRONMENT=production for production")
        print("=" * 60)
    
    # Check required environment variables
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ CRITICAL: GEMINI_API_KEY not set!")
        print("   Add to .env file or environment variables")
        sys.exit(1)
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=int(os.getenv('PORT', 8000)),
        reload=True,  # Auto-reload in development (change to False for production)
        log_level="info" if is_production else "debug",
        access_log=is_production,
        workers=1  # For development; use multiple workers in Docker
    )

