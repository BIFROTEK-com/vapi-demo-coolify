# 🎯 VAPI Demo Builder

Eine professionelle FastAPI-Anwendung für personalisierte VAPI Voice & Chat Assistenten mit automatischer Brand-Integration.

## 🚀 Features

### ✅ **Aktuell implementiert:**
- **🎤 VAPI Chat Integration** - Funktioniert mit echter VAPI API
- **🎨 Automatische Brand-Extraktion** - Logo, Farben, Domain-Analyse
- **📱 Responsive Design** - Modern mit Tailwind CSS
- **⚙️ Admin Dashboard** - Konfiguration und Management
- **🔧 Session Management** - Persistente Chat-Sessions
- **🛡️ Error Handling** - Robuste Fehlerbehandlung

### 🚧 **In Entwicklung:**
- **🎙️ VAPI Voice SDK** - Voice-Chat Funktionalität (temporär deaktiviert)
- **📊 Analytics Dashboard** - Gesprächsstatistiken
- **🔗 Webhook Integration** - Real-time Events

## 🏗️ Architektur

```
vapi-demo-builder/
├── app/
│   ├── main.py              # FastAPI Hauptanwendung
│   ├── config.py            # Konfiguration & Settings
│   ├── services/
│   │   └── color_extractor.py  # Brand-Farb-Extraktion
│   ├── static/
│   │   └── vapi-web-sdk.js     # VAPI SDK (lokal)
│   └── templates/
│       ├── public_webapp.html   # Haupt-Landing-Page
│       ├── admin_config.html    # Admin-Konfiguration
│       ├── admin_dashboard.html # Admin-Dashboard
│       └── config.html          # Legacy-Konfiguration
├── archive/                 # Archivierte Templates
├── backup/                  # Backup-Dateien
├── tests/                   # Unit Tests
├── requirements.txt         # Python Dependencies
├── package.json            # Node.js Dependencies
└── .env                    # Umgebungsvariablen
```

## 🛠️ Installation

### 1. Repository klonen
```bash
git clone https://github.com/BIFROTEK-com/vapi-demo-builder.git
cd vapi-demo-builder
```

### 2. Python Environment
```bash
# Virtual Environment erstellen
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# oder
.venv\Scripts\activate     # Windows

# Dependencies installieren
pip install -r requirements.txt
```

### 3. Node.js Dependencies (optional)
```bash
npm install
```

### 4. Umgebungsvariablen
```bash
cp env.example .env
# .env Datei bearbeiten:
```

```env
# VAPI Configuration
ASSISTANT_ID=your-vapi-assistant-id
PUBLIC_KEY=your-vapi-public-key
VAPI_PRIVATE_KEY=your-vapi-private-key
```

### 5. Anwendung starten
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🎯 Verwendung

### **Für End-Kunden:**
- **Landing Page:** `http://localhost:8000/webapp`
- **Personalisiert:** `http://localhost:8000/webapp?customer_domain=example.com&customer_name=Max`

### **Für Administratoren:**
- **Admin Dashboard:** `http://localhost:8000/admin`
- **Konfiguration:** `http://localhost:8000/admin/config`

### **API Endpoints:**
- **Chat API:** `POST /api/chat` - VAPI Chat Integration
- **Brand Analyse:** `GET /analyze-brand?domain=example.com`
- **Health Check:** `GET /health`

## 🔧 Konfiguration

### **VAPI Setup:**
1. **VAPI Dashboard:** https://dashboard.vapi.ai
2. **Assistant erstellen** und ID kopieren
3. **API Keys** generieren (Public + Private)
4. **Credentials** in Admin-Panel oder `.env` eintragen

### **Personalisierung:**
```python
# URL Parameter für Personalisierung
?customer_domain=example.com
&customer_name=Max Mustermann
&customer_email=max@example.com
&company_name=Example GmbH
&whatsapp_phone=+49 151 12345678
&calendly_link=https://calendly.com/example
```

## 🎨 Design System

### **Farben:**
- **Primary:** `#4361ee` (Blau)
- **Secondary:** `#3a0ca3` (Dunkelblau)
- **Accent:** `#4cc9f0` (Hellblau)
- **Success:** `#2ecc71` (Grün)
- **Warning:** `#f39c12` (Orange)
- **Error:** `#e74c3c` (Rot)

### **Components:**
- **Voice Button** - Animierter Sprach-Button
- **Chat Interface** - Modern mit Typing-Indicator
- **Toast Notifications** - Feedback-System
- **Dark Mode** - Automatische Theme-Erkennung

## 🧪 Testing

```bash
# Unit Tests ausführen
pytest tests/

# Spezifische Tests
pytest tests/test_app.py
pytest tests/test_color_extractor.py

# Coverage Report
pytest --cov=app tests/
```

## 📊 API Dokumentation

### **Chat API**
```http
POST /api/chat
Content-Type: application/json

{
  "message": "Hallo, wie geht es dir?",
  "assistant_id": "uuid-here",
  "session_id": null,
  "customer_domain": "example.com",
  "customer_name": "Max",
  "customer_email": "max@example.com",
  "company_name": "Example GmbH",
  "whatsapp_phone": "+49 151 12345678",
  "calendly_link": "https://calendly.com/example"
}
```

**Response:**
```json
{
  "success": true,
  "id": "chat-uuid",
  "message": "Hallo Max! Wie kann ich dir helfen?",
  "session_id": "session-uuid",
  "raw_response": { ... }
}
```

### **Brand Analyse API**
```http
GET /analyze-brand?domain=example.com
```

**Response:**
```json
{
  "success": true,
  "domain": "example.com",
  "company_name": "Example",
  "logo_url": "https://...",
  "colors": {
    "primary": "#4361ee",
    "secondary": "#3a0ca3",
    "accent": "#4cc9f0"
  },
  "extracted_info": { ... }
}
```

## 🚀 Deployment

### **Docker (empfohlen):**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **Heroku:**
```bash
# Procfile erstellen
echo "web: uvicorn app.main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Deploy
git push heroku master
```

### **Railway/Render:**
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## 🔒 Sicherheit

### **Environment Variables:**
- ✅ Alle API-Keys in `.env`
- ✅ Keine Secrets im Code
- ✅ Private Keys nur im Backend

### **CORS & Headers:**
- ✅ CORS konfiguriert
- ✅ Security Headers
- ✅ Input Validation (Pydantic)

## 🐛 Troubleshooting

### **Häufige Probleme:**

#### **1. VAPI Chat funktioniert nicht**
```bash
# Prüfe VAPI Credentials
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "assistant_id": "your-id"}'
```

#### **2. Templates nicht gefunden**
```bash
# Prüfe Template-Pfad
ls app/templates/
```

#### **3. Static Files laden nicht**
```bash
# Prüfe Static-Pfad
ls app/static/
```

### **Debug Mode:**
```bash
# Detaillierte Logs
uvicorn app.main:app --reload --log-level debug
```

## 📈 Performance

### **Optimierungen:**
- ✅ **Async/Await** - Non-blocking I/O
- ✅ **HTTP Client Pooling** - Wiederverwendbare Connections
- ✅ **Template Caching** - Jinja2 Cache
- ✅ **Static File Serving** - FastAPI StaticFiles

### **Monitoring:**
```python
# Health Check Endpoint
GET /health
# Response: {"status": "ok"}
```

## 🤝 Contributing

### **Development Setup:**
```bash
# Pre-commit Hooks
pip install pre-commit
pre-commit install

# Code Formatting
black app/ tests/
isort app/ tests/

# Linting
flake8 app/ tests/
mypy app/
```

### **Pull Request Process:**
1. **Fork** das Repository
2. **Feature Branch** erstellen
3. **Tests** schreiben und ausführen
4. **Code** formatieren und linten
5. **Pull Request** erstellen

## 📝 Changelog

### **v1.2.0** (Aktuell)
- ✅ **VAPI Chat Integration** - Echte API-Verbindung
- ✅ **Pydantic Validation** - HTTP 422 Fehler behoben
- ✅ **Template Cleanup** - Archive/Backup-Struktur
- ✅ **Error Handling** - Robuste Fehlerbehandlung

### **v1.1.0**
- ✅ **Admin Dashboard** - Konfiguration und Management
- ✅ **Brand Extraktion** - Automatische Logo/Farb-Erkennung
- ✅ **Responsive Design** - Mobile-optimiert

### **v1.0.0**
- ✅ **Initial Release** - Basis-Funktionalität
- ✅ **FastAPI Setup** - REST API
- ✅ **Template System** - Jinja2 Templates

## 📞 Support

### **Kontakt:**
- **GitHub Issues:** https://github.com/BIFROTEK-com/vapi-demo-builder/issues
- **Email:** support@bifrotek.com
- **Discord:** BIFROTEK Community

### **Dokumentation:**
- **VAPI Docs:** https://docs.vapi.ai
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **Tailwind CSS:** https://tailwindcss.com

## 📄 Lizenz

MIT License - siehe [LICENSE](LICENSE) für Details.

---

**Made with ❤️ by BIFROTEK**