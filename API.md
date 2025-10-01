# 📡 API Dokumentation - VAPI Demo Builder

## 🎯 Übersicht

Die VAPI Demo Builder API bietet Endpoints für Chat-Integration, Brand-Analyse und Konfiguration. Alle Endpoints sind RESTful und verwenden JSON für Request/Response.

**Base URL:** `http://localhost:8000`  
**Content-Type:** `application/json`

## 🔐 Authentifizierung

Derzeit keine Authentifizierung erforderlich. In zukünftigen Versionen wird API-Key-Authentifizierung implementiert.

## 📋 Endpoints

### 🗣️ Chat API

#### **POST /api/chat**
Sendet eine Nachricht an den VAPI Assistant und erhält eine Antwort.

**Request Body:**
```json
{
  "message": "Hallo, wie geht es dir?",
  "assistant_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "session_id": null,
  "customer_domain": "example.com",
  "customer_name": "Max Mustermann",
  "customer_email": "max@example.com",
  "company_name": "Example GmbH",
  "whatsapp_phone": "+49 151 12345678",
  "calendly_link": "https://calendly.com/example"
}
```

**Request Parameters:**
| Parameter | Typ | Erforderlich | Beschreibung |
|-----------|-----|--------------|--------------|
| `message` | string | ✅ | Die Nachricht des Benutzers |
| `assistant_id` | string | ✅ | VAPI Assistant UUID |
| `session_id` | string\|null | ❌ | Session ID für Kontext |
| `customer_domain` | string\|null | ❌ | Kunden-Domain |
| `customer_name` | string\|null | ❌ | Kunden-Name |
| `customer_email` | string\|null | ❌ | Kunden-E-Mail |
| `company_name` | string\|null | ❌ | Firmen-Name |
| `whatsapp_phone` | string\|null | ❌ | WhatsApp-Nummer |
| `calendly_link` | string\|null | ❌ | Calendly-Link |

**Response (200 OK):**
```json
{
  "success": true,
  "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "message": "Hallo Max! Wie kann ich dir helfen?",
  "session_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "raw_response": {
    "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "orgId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "input": [
      {
        "role": "user",
        "content": "Hallo, wie geht es dir?"
      }
    ],
    "output": [
      {
        "role": "assistant",
        "content": "Hallo Max! Wie kann ich dir helfen?"
      }
    ],
    "assistantId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "assistantOverrides": {
      "variableValues": {
        "customer_name": "Max Mustermann",
        "company_name": "Example GmbH",
        "customer_domain": "example.com"
      }
    },
    "cost": 0.0056,
    "createdAt": "2025-09-02T02:52:20.113Z"
  }
}
```

**Error Responses:**

**422 Unprocessable Entity:**
```json
{
  "detail": [
    {
      "type": "string_type",
      "loc": ["body", "message"],
      "msg": "Input should be a valid string",
      "input": null
    }
  ]
}
```

**500 Internal Server Error:**
```json
{
  "detail": "VAPI_PRIVATE_KEY not configured on server"
}
```

**408 Request Timeout:**
```json
{
  "detail": "Request timeout"
}
```

**cURL Beispiel:**
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hallo, wie geht es dir?",
    "assistant_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "customer_name": "Max Mustermann",
    "customer_domain": "example.com"
  }'
```

---

### 🎨 Brand Analyse API

#### **GET /analyze-brand**
Analysiert eine Domain und extrahiert Brand-Informationen wie Logo, Farben und Metadaten.

**Query Parameters:**
| Parameter | Typ | Erforderlich | Beschreibung |
|-----------|-----|--------------|--------------|
| `domain` | string | ✅ | Domain zu analysieren (z.B. "example.com") |

**Request:**
```http
GET /analyze-brand?domain=example.com
```

**Response (200 OK):**
```json
{
  "success": true,
  "domain": "example.com",
  "company_name": "Example",
  "logo_url": "https://t1.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=http://example.com&size=128",
  "logo_url_fallback": "https://www.google.com/s2/favicons?domain=example.com&sz=128",
  "website_url": "https://example.com",
  "support_email": "info@example.com",
  "impressum_url": "https://example.com/impressum",
  "privacy_url": "https://example.com/datenschutz",
  "terms_url": "https://example.com/agb",
  "colors": {
    "primary": "#4361ee",
    "secondary": "#3a0ca3",
    "accent": "#4cc9f0"
  },
  "extracted_info": {
    "companyName": "Example",
    "logoUrl": "https://t1.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=http://example.com&size=128",
    "websiteUrl": "https://example.com",
    "primaryColor": "#4361ee",
    "secondaryColor": "#3a0ca3",
    "accentColor": "#4cc9f0"
  }
}
```

**Error Response (400 Bad Request):**
```json
{
  "success": false,
  "error": "Invalid domain format",
  "domain": "invalid-domain"
}
```

**cURL Beispiel:**
```bash
curl "http://localhost:8000/analyze-brand?domain=example.com"
```

---

### ⚙️ Konfiguration API

#### **POST /save-vapi-credentials**
Speichert VAPI-Credentials in der .env-Datei.

**Request Body (Form Data):**
```
assistant_id=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
public_key=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "VAPI credentials saved successfully to .env file"
}
```

**Error Response:**
```json
{
  "status": "error",
  "message": "Failed to save credentials: Permission denied"
}
```

#### **POST /update-bot-config**
Aktualisiert Bot-Konfiguration dynamisch.

**Request Body (Form Data):**
```
customer_domain=example.com
customer_whatsapp=+49 151 12345678
facebook_business_whatsapp=+49 151 87654321
assistant_id=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
public_key=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Bot configuration updated",
  "customer_domain": "example.com",
  "customer_whatsapp": "+49 151 12345678",
  "facebook_business_whatsapp": "+49 151 87654321",
  "assistant_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "public_key": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

---

### 🏥 Health Check API

#### **GET /health**
Einfacher Health Check für Monitoring.

**Response (200 OK):**
```json
{
  "status": "ok"
}
```

**cURL Beispiel:**
```bash
curl "http://localhost:8000/health"
```

---

## 🌐 Web Routes

### **GET /**
Redirect zur Haupt-WebApp.

**Response:** `302 Redirect` → `/webapp`

### **GET /webapp**
Personalisierte Landing Page für End-Kunden.

**Query Parameters:**
| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `customer_domain` | string | "beispiel.de" | Kunden-Domain |
| `customer_name` | string | "Kunde" | Kunden-Name |
| `customer_email` | string | "" | Kunden-E-Mail |
| `company_name` | string | "Beispiel" | Firmen-Name |
| `whatsapp_phone` | string | "+49 151 12345678" | WhatsApp-Nummer |
| `calendly_link` | string | "https://calendly.com/beispiel" | Calendly-Link |

**Beispiel:**
```
http://localhost:8000/webapp?customer_domain=example.com&customer_name=Max%20Mustermann&company_name=Example%20GmbH
```

### **GET /admin**
Admin Dashboard für Verwaltung.

### **GET /admin/config**
Admin-Konfigurationsseite für VAPI-Einstellungen.

---

## 🔧 Error Handling

### **Standard Error Format:**
```json
{
  "detail": "Error message here"
}
```

### **Validation Error Format:**
```json
{
  "detail": [
    {
      "type": "string_type",
      "loc": ["body", "field_name"],
      "msg": "Input should be a valid string",
      "input": null
    }
  ]
}
```

### **HTTP Status Codes:**
| Code | Bedeutung | Beschreibung |
|------|-----------|--------------|
| 200 | OK | Erfolgreiche Anfrage |
| 302 | Found | Redirect |
| 400 | Bad Request | Ungültige Anfrage |
| 404 | Not Found | Ressource nicht gefunden |
| 408 | Request Timeout | Anfrage-Timeout |
| 422 | Unprocessable Entity | Validierungsfehler |
| 500 | Internal Server Error | Server-Fehler |

---

## 📊 Rate Limiting

Derzeit kein Rate Limiting implementiert. Geplant für zukünftige Versionen:

- **Chat API:** 60 Requests/Minute pro IP
- **Brand Analyse:** 10 Requests/Minute pro IP
- **Admin APIs:** 100 Requests/Minute pro IP

---

## 🔒 Security Headers

### **CORS Configuration:**
```python
# Erlaubte Origins (Development)
origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "https://yourdomain.com"
]
```

### **Security Headers:**
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`

---

## 📈 Performance

### **Response Times (Durchschnitt):**
- **Chat API:** ~800ms (abhängig von VAPI)
- **Brand Analyse:** ~200ms
- **Health Check:** ~5ms
- **Static Files:** ~10ms

### **Timeouts:**
- **VAPI API Calls:** 30 Sekunden
- **HTTP Client:** 30 Sekunden
- **Request Timeout:** 60 Sekunden

---

## 🧪 Testing

### **API Testing mit curl:**

```bash
# Health Check
curl "http://localhost:8000/health"

# Chat Test
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "assistant_id": "your-uuid"}'

# Brand Analyse
curl "http://localhost:8000/analyze-brand?domain=google.com"
```

### **API Testing mit Python:**

```python
import requests

# Chat API Test
response = requests.post("http://localhost:8000/api/chat", json={
    "message": "Hallo!",
    "assistant_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "customer_name": "Test User"
})

print(response.json())
```

### **API Testing mit JavaScript:**

```javascript
// Chat API Test
const response = await fetch('http://localhost:8000/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        message: 'Hallo!',
        assistant_id: 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
        customer_name: 'Test User'
    })
});

const data = await response.json();
console.log(data);
```

---

## 📝 Changelog

### **v1.2.0** (Aktuell)
- ✅ **Chat API:** Vollständige VAPI-Integration
- ✅ **Error Handling:** Verbesserte Fehlerbehandlung
- ✅ **Validation:** Pydantic-Modelle korrigiert

### **v1.1.0**
- ✅ **Brand Analyse API:** Domain-Analyse implementiert
- ✅ **Admin APIs:** Konfiguration und Management

### **v1.0.0**
- ✅ **Initial Release:** Basis-API-Funktionalität

---

**Letzte Aktualisierung:** 2024-09-02  
**API Version:** 1.2.0  
**Dokumentation Version:** 1.0

