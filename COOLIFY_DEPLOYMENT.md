# Coolify Deployment Guide

## 🚀 VAPI Demo Builder für Coolify

Diese Anleitung zeigt, wie du den VAPI Demo Builder auf Coolify deployst.

## 📋 Voraussetzungen

- Coolify installiert und konfiguriert
- Git Repository mit dem Code
- VAPI Credentials (Assistant ID, Public Key, Private Key)

## 🔧 Deployment-Optionen

### Option 1: Vollständig eigenständig (Empfohlen)

Verwende `coolify-docker-compose.yml` für ein vollständig eigenständiges Setup:

```bash
# In Coolify:
# 1. Neues Projekt erstellen
# 2. Git Repository verbinden
# 3. Docker Compose File: coolify-docker-compose.yml
# 4. Environment Variables setzen (siehe unten)
```

**Vorteile:**
- ✅ Vollständig eigenständig
- ✅ Keine externen Dependencies
- ✅ Redis und Shlink inklusive
- ✅ Perfekt für Production

### Option 2: Externe Services (Einfacher)

Verwende `coolify-simple.yml` mit externen Services:

```bash
# In Coolify:
# 1. Neues Projekt erstellen
# 2. Git Repository verbinden
# 3. Docker Compose File: coolify-simple.yml
# 4. Environment Variables setzen
```

**Vorteile:**
- ✅ Einfacher zu deployen
- ✅ Nutzt bestehende Redis/Shlink Services
- ✅ Weniger Ressourcenverbrauch

## 🔑 Environment Variables

### Erforderliche Variablen

```bash
# VAPI Configuration
ASSISTANT_ID=your_assistant_id_here
PUBLIC_KEY=your_public_key_here
VAPI_PRIVATE_KEY=your_private_key_here

# App Security
CONFIG_PASSWORD=your_secure_password_here
```

### Optionale Variablen

```bash
# Company Information
COMPANY_NAME=Your Company Name
SUPPORT_EMAIL=support@yourcompany.com

# Contact Options
FACEBOOK_BUSINESS_WHATSAPP=+1234567890
CALENDLY_LINK=https://calendly.com/your-link

# Redis (für Option 2)
REDIS_URL=redis://your-redis-host:6379

# Shlink (für Option 2)
SHLINK_API_KEY=your_shlink_api_key
SHLINK_BASE_URL=https://your-shlink-host/rest/v3

# Shlink Domain (für Option 1)
SHLINK_DOMAIN=your-domain.com
SHLINK_HTTPS=true
```

## 🚀 Deployment-Schritte

### Schritt 1: Repository vorbereiten

```bash
# Code committen
git add .
git commit -m "Add Coolify deployment configuration"
git push origin main
```

### Schritt 2: Coolify konfigurieren

1. **Neues Projekt erstellen**
   - Gehe zu Coolify Dashboard
   - Klicke "New Project"
   - Wähle "Git Repository"

2. **Repository verbinden**
   - Git URL eingeben
   - Branch: `main`
   - Build Pack: `Docker Compose`

3. **Docker Compose File auswählen**
   - Für vollständig eigenständig: `coolify-docker-compose.yml`
   - Für externe Services: `coolify-simple.yml`

4. **Environment Variables setzen**
   - Alle erforderlichen Variablen eintragen
   - Optionale Variablen nach Bedarf

### Schritt 3: Deploy starten

1. Klicke "Deploy"
2. Warte auf Build-Prozess
3. Überprüfe Logs auf Fehler
4. Teste die Anwendung

## 🔍 Health Checks

Die Anwendung bietet mehrere Health Check Endpoints:

- **Main Health**: `https://your-domain.com/health`
- **Redis Status**: Inklusive in `/health`
- **Shlink Status**: Automatisch überprüft

## 📊 Monitoring

### Logs überwachen

```bash
# In Coolify Dashboard
# 1. Gehe zu deinem Projekt
# 2. Klicke auf "Logs"
# 3. Überwache Startup und Runtime Logs
```

### Wichtige Log-Messages

```
✅ Connected to Upstash Redis at rediss://...
✅ Redis service initialized successfully
✅ Shlink service configured: True
INFO: Application startup complete.
```

## 🛠️ Troubleshooting

### Häufige Probleme

1. **Redis Connection Failed**
   ```
   ❌ Redis connection failed: Connection refused
   ```
   **Lösung**: Überprüfe REDIS_URL und Netzwerk-Konfiguration

2. **Shlink Service Not Configured**
   ```
   ⚠️ Shlink API Key not configured
   ```
   **Lösung**: Setze SHLINK_API_KEY in Environment Variables

3. **VAPI Credentials Missing**
   ```
   ❌ VAPI credentials not configured on server
   ```
   **Lösung**: Setze alle VAPI_* Environment Variables

### Debug-Modus aktivieren

```bash
# In Coolify Environment Variables
DEBUG=true
LOG_LEVEL=debug
```

## 🔒 Sicherheit

### Production-Empfehlungen

1. **Starke Passwörter verwenden**
   ```bash
   CONFIG_PASSWORD=your_very_secure_password_here
   REDIS_PASSWORD=your_redis_password_here
   ```

2. **HTTPS aktivieren**
   - Coolify SSL-Zertifikat konfigurieren
   - SHLINK_HTTPS=true setzen

3. **Environment Variables sichern**
   - Niemals Credentials in Git committen
   - Coolify Secrets verwenden

## 📈 Skalierung

### Horizontal Scaling

```yaml
# In coolify-docker-compose.yml
deploy:
  replicas: 3
  resources:
    limits:
      cpus: '0.5'
      memory: 512M
    reservations:
      cpus: '0.25'
      memory: 256M
```

### Load Balancing

Coolify bietet automatisches Load Balancing für mehrere Instanzen.

## 🔄 Updates

### Code Updates

```bash
# 1. Code ändern
git add .
git commit -m "Update application"
git push origin main

# 2. In Coolify
# - Automatisches Rebuild wird gestartet
# - Oder manuell "Redeploy" klicken
```

### Environment Variable Updates

1. Gehe zu Coolify Dashboard
2. Projekt → Settings → Environment Variables
3. Variablen ändern
4. "Redeploy" klicken

## 📞 Support

Bei Problemen:

1. Überprüfe die Logs in Coolify
2. Teste die Health Check Endpoints
3. Überprüfe Environment Variables
4. Kontaktiere den Support

## 🎉 Fertig!

Nach erfolgreichem Deployment ist deine VAPI Demo Builder Anwendung verfügbar unter:

- **Main App**: `https://your-domain.com`
- **Health Check**: `https://your-domain.com/health`
- **Config Page**: `https://your-domain.com/config`
- **API Docs**: `https://your-domain.com/docs`
