from fastapi import FastAPI, Request, Form, Query, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import json
from datetime import datetime
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()

from .config import get_settings
from .config_manager import config_manager
from .config_functions import (
    get_vapi_credentials, get_company_config, get_brand_colors, get_contact_config,
    save_vapi_credentials, save_manual_inputs, save_domain_analysis
)
from .services.color_extractor import extract_brand_colors
from .services.redis_service import redis_service
from .services.shlink_service import shlink_service, ShortUrlRequest, ShortUrlResponse


app = FastAPI(title="VAPI Web SDK Integration")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add caching headers for static files
@app.middleware("http")
async def add_cache_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Add cache headers for static files
    if request.url.path.startswith("/static/"):
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        response.headers["ETag"] = f'"{hash(request.url.path)}"'
    elif request.url.path.endswith((".js", ".css")):
        response.headers["Cache-Control"] = "public, max-age=86400"
    
    return response

# Optimize template rendering for production
templates = Jinja2Templates(
    directory="app/templates",
    autoescape=False,  # Disable autoescaping for React components
    auto_reload=False  # Disable auto-reload in production
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Pydantic models
class WebhookData(BaseModel):
    message: dict
    sessionId: str

class ShortUrlRequest(BaseModel):
    url: str
    title: Optional[str] = None

class ShortUrlResponse(BaseModel):
    shortUrl: str
    longUrl: str
    title: Optional[str] = None

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# Main routes
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Main page with VAPI integration."""
    # Load VAPI credentials and config using new config manager
    vapi_creds = get_vapi_credentials()
    company_config = get_company_config()
    brand_colors = get_brand_colors()
    contact_config = get_contact_config()
    
    # Check if configuration is complete
    config_complete = bool(vapi_creds["assistant_id"] and vapi_creds["public_key"])
    
    return templates.TemplateResponse("public_webapp.html", {
        "request": request,
        "assistant_id": vapi_creds["assistant_id"],
        "public_key": vapi_creds["public_key"],
        "company_name": company_config["company_name"],
        "website_url": company_config["website_url"],
        "support_email": company_config["support_email"],
        "impressum_url": company_config["impressum_url"],
        "privacy_policy_url": company_config["privacy_policy_url"],
        "terms_url": company_config["terms_url"],
        "logo_url": company_config["logo_url"],
        "facebook_business_whatsapp": contact_config["facebook_business_whatsapp"],
        "calendly_link": contact_config["calendly_link"],
        "primary_color": brand_colors["primary_color"],
        "secondary_color": brand_colors["secondary_color"],
        "accent_color": brand_colors["accent_color"],
        "config_complete": config_complete,
        "current_url": str(request.url)
    })

@app.get("/config", response_class=HTMLResponse)
async def config_page(request: Request):
    """Configuration page."""
    return templates.TemplateResponse("config.html", {
        "request": request,
        "current_url": str(request.url)
    })

# Configuration API endpoints
@app.get("/api/secure-config")
def get_secure_config(password: str = Query(...)) -> dict:
    """Get configuration with password protection."""
    config_password = config_manager.get_config_value("CONFIG_PASSWORD", "")
    
    # Check password
    if password != config_password:
        raise HTTPException(status_code=401, detail="Invalid password")
    
    # Return config using new config manager
    vapi_creds = get_vapi_credentials()
    company_config = get_company_config()
    brand_colors = get_brand_colors()
    contact_config = get_contact_config()
    
    return {
        "assistantId": vapi_creds["assistant_id"],
        "publicKey": vapi_creds["public_key"],
        "facebookBusinessWhatsApp": contact_config["facebook_business_whatsapp"],
        "calendlyLink": contact_config["calendly_link"],
        "analyzedDomain": config_manager.get_config_value("ANALYZED_DOMAIN"),
        "companyName": company_config["company_name"],
        "websiteUrl": company_config["website_url"],
        "supportEmail": company_config["support_email"],
        "impressumUrl": company_config["impressum_url"],
        "privacyPolicyUrl": company_config["privacy_policy_url"],
        "termsUrl": company_config["terms_url"],
        "heroTitle": "",  # Not stored in config
        "heroText": "",   # Not stored in config
        "primaryColor": brand_colors["primary_color"],
        "secondaryColor": brand_colors["secondary_color"],
        "accentColor": brand_colors["accent_color"],
        "logoUrl": company_config["logo_url"]
    }

@app.get("/api/env-config")
def get_env_config() -> dict:
    """Public API for configuration values (deprecated - use /api/secure-config)."""
    return get_secure_config("")  # No password for backward compatibility

@app.get("/api/config-status")
def get_config_status() -> dict:
    """Check if configuration is complete and valid."""
    vapi_creds = get_vapi_credentials()
    
    return {
        "assistant_id_configured": bool(vapi_creds["assistant_id"]),
        "public_key_configured": bool(vapi_creds["public_key"]),
        "config_complete": bool(vapi_creds["assistant_id"] and vapi_creds["public_key"]),
        "environment": "coolify" if config_manager.is_coolify else "local"
    }

# Save endpoints using new config functions
@app.post("/save-vapi-credentials")
async def save_vapi_credentials_endpoint(
    assistant_id: str = Form(...),
    public_key: str = Form(...),
    private_key: str = Form(default=""),
) -> dict[str, str]:
    """Save VAPI credentials with intelligent fallback."""
    return save_vapi_credentials(assistant_id, public_key, private_key)

@app.post("/save-manual-inputs")
async def save_manual_inputs_endpoint(
    facebook_business_whatsapp: str = Form(default=""),
    calendly_link: str = Form(default=""),
) -> dict[str, str]:
    """Save manual inputs with intelligent fallback."""
    return save_manual_inputs(facebook_business_whatsapp, calendly_link)

@app.post("/save-domain-analysis")
async def save_domain_analysis_endpoint(
    analyzed_domain: str = Form(default=""),
    company_name: str = Form(default=""),
    website_url: str = Form(default=""),
    support_email: str = Form(default=""),
    impressum_url: str = Form(default=""),
    privacy_policy_url: str = Form(default=""),
    terms_url: str = Form(default=""),
    hero_title: str = Form(default=""),
    hero_text: str = Form(default=""),
    primary_color: str = Form(default=""),
    secondary_color: str = Form(default=""),
    accent_color: str = Form(default=""),
    logo_url: str = Form(default=""),
) -> dict[str, str]:
    """Save domain analysis results with intelligent fallback."""
    return save_domain_analysis(
        analyzed_domain, company_name, website_url, support_email,
        impressum_url, privacy_policy_url, terms_url, hero_title, hero_text,
        primary_color, secondary_color, accent_color, logo_url
    )

# Domain analysis endpoint
@app.post("/api/analyze-domain")
async def analyze_domain(domain: str = Form(...)) -> dict:
    """Analyze domain and extract brand information."""
    try:
        # Clean domain
        clean_domain = domain.strip().lower()
        if not clean_domain.startswith(('http://', 'https://')):
            clean_domain = f"https://{clean_domain}"
        
        # Extract brand colors
        try:
            primary_color, secondary_color, accent_color = await extract_brand_colors(clean_domain)
        except Exception as e:
            print(f"⚠️ Color extraction failed: {e}, using defaults")
            primary_color = "#4361ee"    # Standard blue
            secondary_color = "#3a0ca3"  # Standard dark blue  
            accent_color = "#4cc9f0"     # Standard light blue
        
        # Automatically save to config (local development only)
        if not config_manager.is_coolify:
            try:
                await save_domain_analysis(
                    analyzed_domain=clean_domain,
                    company_name="",  # Will be filled by user
                    website_url=clean_domain,
                    support_email="",  # Will be filled by user
                    impressum_url="",  # Will be filled by user
                    privacy_policy_url="",  # Will be filled by user
                    terms_url="",  # Will be filled by user
                    hero_title="",  # Empty, user can fill manually
                    hero_text="",   # Empty, user can fill manually
                    primary_color=primary_color,
                    secondary_color=secondary_color,
                    accent_color=accent_color,
                    logo_url=""  # Will be filled by user
                )
                print(f"✅ Domain analysis results automatically saved")
            except Exception as e:
                print(f"⚠️ Failed to save domain analysis: {e}")
        else:
            print(f"ℹ️ Running in Coolify - domain analysis results not saved (managed by Coolify)")

        return {
            "success": True,
            "domain": clean_domain,
            "company_name": "",  # Will be filled by user
            "website_url": clean_domain,
            "support_email": "",  # Will be filled by user
            "impressum_url": "",  # Will be filled by user
            "privacy_policy_url": "",  # Will be filled by user
            "terms_url": "",  # Will be filled by user
            "hero_title": "",  # Empty, user can fill manually
            "hero_text": "",   # Empty, user can fill manually
            "primary_color": primary_color,
            "secondary_color": secondary_color,
            "accent_color": accent_color,
            "logo_url": ""  # Will be filled by user
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# Webhook endpoint
@app.post("/webhook")
async def webhook(data: WebhookData):
    """Handle VAPI webhook events."""
    try:
        # Store webhook message in Redis
        await redis_service.store_webhook_message(
            data.sessionId, 
            data.message.dict()
        )
        
        return {"status": "success"}
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return {"status": "error", "message": str(e)}

# URL shortening endpoint
@app.post("/api/shorten-url", response_model=ShortUrlResponse)
async def shorten_url(request: ShortUrlRequest):
    """Shorten a URL using Shlink service."""
    try:
        result = await shlink_service.create_short_url(request.url, request.title)
        return ShortUrlResponse(
            shortUrl=result.shortUrl,
            longUrl=result.longUrl,
            title=result.title
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Test endpoint
@app.get("/test", response_class=HTMLResponse)
async def test_page(request: Request):
    """Test page for VAPI Web SDK."""
    return templates.TemplateResponse("test_web_sdk.html", {
        "request": request,
        "current_url": str(request.url)
    })

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    print("🚀 Starting VAPI Demo Application...")
    
    # Connect to Redis
    await redis_service.connect()
    
    print("✅ VAPI Demo Application started successfully!")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("🛑 Shutting down VAPI Demo Application...")
    
    # Disconnect from Redis
    await redis_service.disconnect()
    
    print("✅ VAPI Demo Application shutdown complete!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
