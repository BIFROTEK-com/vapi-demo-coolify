# 🔧 Technische Dokumentation - VAPI Demo Builder

## 🏗️ System-Architektur

### **Backend (FastAPI)**
```
app/
├── main.py                 # FastAPI Application & Routes
├── config.py              # Settings & Environment Management
└── services/
    └── color_extractor.py # Brand Color Extraction Service
```

### **Frontend (Templates)**
```
app/templates/
├── public_webapp.html     # Main Customer Landing Page
├── admin_config.html      # Admin Configuration Interface
├── admin_dashboard.html   # Admin Management Dashboard
└── config.html           # Legacy Configuration Page
```

### **Static Assets**
```
app/static/
└── vapi-web-sdk.js       # Local VAPI SDK (fallback)
```

## 🔌 API Integration

### **VAPI Chat API Integration**

#### **Backend Endpoint:**
```python
@app.post("/api/chat")
async def chat_with_vapi(chat_request: ChatRequest) -> dict:
```

#### **Request Model:**
```python
class ChatRequest(BaseModel):
    message: str
    assistant_id: str
    session_id: str | None = None
    previous_chat_id: str | None = None
    # Assistant override variables
    customer_domain: str | None = None
    customer_name: str | None = None
    customer_email: str | None = None
    company_name: str | None = None
    whatsapp_phone: str | None = None
    calendly_link: str | None = None
```

#### **VAPI API Call:**
```python
async with httpx.AsyncClient() as client:
    response = await client.post(
        "https://api.vapi.ai/chat",
        headers={
            "Authorization": f"Bearer {private_api_key}",
            "Content-Type": "application/json"
        },
        json=request_body,
        timeout=30.0
    )
```

#### **Response Processing:**
```python
return {
    "success": True,
    "id": chat_response.get("id"),
    "message": chat_response.get("output", [{}])[0].get("content", ""),
    "session_id": chat_response.get("sessionId"),
    "raw_response": chat_response
}
```

## 🎨 Frontend-Architektur

### **JavaScript Structure**
```javascript
// VAPI Configuration
const VAPI_CONFIG = {
    publicKey: "{{ public_key }}",
    assistantId: "{{ assistant_id }}",
    assistantOverrides: {
        variableValues: {
            customer_domain: "{{ customer_domain }}",
            customer_name: "{{ customer_name }}",
            // ... weitere Variablen
        }
    }
};

// Chat Message Handling
async function sendChatMessage(message) {
    // Backend API Call
    const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            message: message,
            assistant_id: VAPI_CONFIG.assistantId,
            // ... weitere Parameter
        })
    });
    
    // Response Processing
    if (response.ok) {
        const data = await response.json();
        addChatMessage(data.message, 'assistant');
    }
}
```

### **UI Components**

#### **Chat Interface:**
```html
<div id="chatMessages" class="space-y-4 max-h-96 overflow-y-auto">
    <!-- Chat Messages -->
</div>

<div class="flex space-x-2">
    <input id="chatInput" type="text" placeholder="Schreiben Sie Ihre Nachricht...">
    <button id="sendButton">Send</button>
</div>
```

#### **Voice Button:**
```html
<button id="voiceButton" class="voice-button">
    <div class="pulse-ring"></div>
    <img src="data:image/svg+xml;base64,..." alt="Voice">
</button>
```

## 🔧 Configuration Management

### **Environment Variables**
```env
# VAPI Credentials
ASSISTANT_ID=uuid-format-assistant-id
PUBLIC_KEY=uuid-format-public-key
VAPI_PRIVATE_KEY=uuid-format-private-key

# Optional Settings
DEBUG=false
LOG_LEVEL=info
```

### **Settings Class**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    assistant_id: str = ""
    public_key: str = ""
    vapi_private_key: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = False
```

### **Dynamic Configuration**
```python
@app.get("/webapp")
def public_webapp(
    customer_domain: str = Query(default="beispiel.de"),
    customer_name: str = Query(default="Kunde"),
    # ... weitere Parameter
):
    # Template-Variablen generieren
    config = {
        "customer_name": customer_name,
        "customer_domain": clean_domain,
        "company_name": company_name,
        # ... weitere Konfiguration
    }
    
    return templates.TemplateResponse("public_webapp.html", {
        "request": request,
        "assistant_id": assistant_id,
        "public_key": public_key,
        **config
    })
```

## 🎯 Brand Integration System

### **Domain Analysis**
```python
def analyze_brand(domain: str):
    # Domain bereinigen
    clean_domain = domain.replace('https://', '').replace('http://', '')
    clean_domain = clean_domain.replace('www.', '').split('/')[0]
    
    # Company Name extrahieren
    company_name = clean_domain.replace('.com', '').replace('.de', '')
    company_name = company_name.replace('-', ' ').title()
    
    # Logo URLs generieren
    logo_urls = [
        f"https://t1.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&url=http://{clean_domain}&size=128",
        f"https://www.google.com/s2/favicons?domain={clean_domain}&sz=128",
        f"https://icons.duckduckgo.com/ip3/{clean_domain}.ico",
        f"https://{clean_domain}/favicon.ico"
    ]
    
    return {
        "company_name": company_name,
        "logo_urls": logo_urls,
        "colors": get_brand_colors()
    }
```

### **Color System**
```python
# Standard Brand Colors
BRAND_COLORS = {
    "primary": "#4361ee",      # Blau
    "secondary": "#3a0ca3",    # Dunkelblau
    "accent": "#4cc9f0",       # Hellblau
    "success": "#2ecc71",      # Grün
    "warning": "#f39c12",      # Orange
    "error": "#e74c3c"         # Rot
}
```

## 🔒 Security Implementation

### **API Key Management**
```python
# Private Key nur im Backend
private_api_key = settings.vapi_private_key
if not private_api_key:
    raise HTTPException(
        status_code=500, 
        detail="VAPI_PRIVATE_KEY not configured"
    )

# Public Key im Frontend (sicher)
public_key = settings.public_key  # Kann im Frontend verwendet werden
```

### **Input Validation**
```python
# Pydantic Validation
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    assistant_id: str = Field(..., regex=r'^[0-9a-f-]{36}$')
    session_id: str | None = Field(None, regex=r'^[0-9a-f-]{36}$')
```

### **Error Handling**
```python
try:
    # VAPI API Call
    response = await client.post("https://api.vapi.ai/chat", ...)
    
    if response.status_code not in [200, 201]:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"VAPI API error: {response.text}"
        )
        
except httpx.TimeoutException:
    raise HTTPException(status_code=408, detail="Request timeout")
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")
```

## 📊 Database Schema (Future)

### **Planned Tables**
```sql
-- Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Chat Sessions
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    vapi_session_id VARCHAR(255),
    customer_domain VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Chat Messages
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES chat_sessions(id),
    role VARCHAR(20) NOT NULL, -- 'user' or 'assistant'
    content TEXT NOT NULL,
    vapi_message_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🧪 Testing Strategy

### **Unit Tests**
```python
# tests/test_app.py
def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_chat_endpoint():
    response = client.post("/api/chat", json={
        "message": "test",
        "assistant_id": "test-uuid"
    })
    assert response.status_code == 200
```

### **Integration Tests**
```python
# tests/test_vapi_integration.py
@pytest.mark.asyncio
async def test_vapi_chat_integration():
    # Mock VAPI API Response
    with httpx_mock.HTTPXMock() as mock:
        mock.add_response(
            method="POST",
            url="https://api.vapi.ai/chat",
            json={"id": "test", "output": [{"content": "response"}]}
        )
        
        # Test Chat Request
        response = await chat_with_vapi(ChatRequest(
            message="test",
            assistant_id="test-uuid"
        ))
        
        assert response["success"] is True
```

## 🚀 Performance Optimizations

### **Async Operations**
```python
# Async HTTP Calls
async with httpx.AsyncClient() as client:
    response = await client.post(...)

# Async Template Rendering
@app.get("/webapp")
async def public_webapp(...):
    return templates.TemplateResponse(...)
```

### **Caching Strategy**
```python
# Template Caching
templates = Jinja2Templates(
    directory="app/templates",
    auto_reload=False  # Production: False
)

# Settings Caching
@lru_cache()
def get_settings():
    return Settings()
```

### **Static File Optimization**
```python
# Static Files mit Caching
app.mount("/static", StaticFiles(
    directory="app/static",
    html=True
), name="static")
```

## 🔄 Deployment Pipeline

### **Docker Configuration**
```dockerfile
FROM python:3.11-slim

# System Dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python Dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application Code
COPY . .

# Health Check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run Application
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **Environment-specific Configs**
```python
# config.py
class Settings(BaseSettings):
    environment: str = "development"
    debug: bool = False
    log_level: str = "info"
    
    # Production Overrides
    @validator('debug')
    def set_debug(cls, v, values):
        if values.get('environment') == 'production':
            return False
        return v
```

## 📈 Monitoring & Logging

### **Structured Logging**
```python
import structlog

logger = structlog.get_logger()

@app.post("/api/chat")
async def chat_with_vapi(chat_request: ChatRequest):
    logger.info("chat_request_received", 
                message_length=len(chat_request.message),
                assistant_id=chat_request.assistant_id)
    
    try:
        # ... API Call
        logger.info("vapi_response_received", 
                    response_id=response_id,
                    response_length=len(response_text))
    except Exception as e:
        logger.error("vapi_request_failed", 
                     error=str(e),
                     assistant_id=chat_request.assistant_id)
```

### **Health Checks**
```python
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.2.0"
    }

@app.get("/health/detailed")
async def detailed_health():
    # Check VAPI API Connectivity
    vapi_status = await check_vapi_connection()
    
    return {
        "status": "ok",
        "services": {
            "vapi": vapi_status,
            "database": "ok",  # Future
            "cache": "ok"      # Future
        }
    }
```

## 🔧 Development Tools

### **Pre-commit Hooks**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

### **Development Scripts**
```bash
#!/bin/bash
# scripts/dev.sh

# Start Development Server
echo "Starting VAPI Demo Builder..."
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# scripts/test.sh
#!/bin/bash
echo "Running Tests..."
pytest tests/ --cov=app --cov-report=html

# scripts/lint.sh
#!/bin/bash
echo "Linting Code..."
black app/ tests/
isort app/ tests/
flake8 app/ tests/
mypy app/
```

---

**Letzte Aktualisierung:** 2024-09-02  
**Version:** 1.2.0  
**Autor:** BIFROTEK Development Team

