# 🚀 VAPI Demo Builder - Coolify Deployment Guide

## Übersicht

Diese Anleitung zeigt Ihnen, wie Sie den VAPI Demo Builder einfach und schnell bei Coolify deployen können.

## 📋 Voraussetzungen

- Coolify-Instanz (selbst gehostet oder Cloud)
- VAPI-Account mit API-Keys
- Domain für Ihre Anwendung

## 🎯 Schnellstart (5 Minuten)

### Schritt 1: Repository klonen
```bash
git clone https://github.com/ihr-username/vapi-demo-coolify.git
cd vapi-demo-coolify
```

### Schritt 2: Environment-Variablen konfigurieren
Kopieren Sie `.env.example` zu `.env` und füllen Sie Ihre Werte ein:

```bash
cp .env.example .env
```

**Wichtige Variablen:**
- `ASSISTANT_ID` - Ihr VAPI Assistant ID
- `PUBLIC_KEY` - Ihr VAPI Public Key  
- `VAPI_PRIVATE_KEY` - Ihr VAPI Private Key
- `COMPANY_NAME` - Ihr Firmenname
- `WEBSITE_URL` - Ihre Domain
- `REDIS_PASSWORD` - Starkes Passwort für Redis

### Schritt 3: Bei Coolify deployen

1. **Neues Projekt erstellen** in Coolify
2. **Repository verbinden** (GitHub/GitLab)
3. **Docker Compose** als Build-Methode wählen
4. **docker-compose.yaml** als Konfigurationsdatei verwenden
5. **Environment Variables** aus `.env` in Coolify eintragen
6. **Deploy** starten

## 🔧 Detaillierte Konfiguration

### VAPI-Konfiguration

1. Gehen Sie zu [VAPI Dashboard](https://dashboard.vapi.ai)
2. Erstellen Sie einen neuen Assistant
3. Kopieren Sie die Keys:
   - Assistant ID
   - Public Key
   - Private Key

### Domain-Konfiguration

Setzen Sie in Coolify:
- `WEBSITE_URL=https://ihre-domain.com`
- `SHLINK_DOMAIN=ihre-domain.com`
- `SHLINK_HTTPS=true`

### Branding anpassen

Passen Sie die Farben und das Logo an:
- `PRIMARY_COLOR=#ihre-farbe`
- `SECONDARY_COLOR=#ihre-farbe`
- `ACCENT_COLOR=#ihre-farbe`
- `LOGO_URL=https://ihre-domain.com/logo.png`

## 📊 Services

Die Anwendung besteht aus 4 Services:

1. **vapi-demo** - Hauptanwendung (Port 8000)
2. **redis** - Session-Management
3. **shlink** - URL-Shortening (Port 8080)
4. **shlink-db** - PostgreSQL-Datenbank

## 🔍 Health Checks

Nach dem Deployment prüfen Sie:
- Hauptanwendung: `https://ihre-domain.com/health`
- Shlink API: `https://ihre-domain.com:8080/rest/v3/health`

## 🛠️ Troubleshooting

### Häufige Probleme

1. **Container startet nicht:**
   - Prüfen Sie alle Environment Variables
   - Prüfen Sie die Logs in Coolify

2. **Shlink funktioniert nicht:**
   - Warten Sie 2-3 Minuten nach dem Start
   - Prüfen Sie die Datenbank-Verbindung

3. **VAPI-Verbindung fehlt:**
   - Prüfen Sie die VAPI-Keys
   - Testen Sie mit `/health` Endpoint

### Logs anzeigen

In Coolify:
1. Gehen Sie zu Ihrem Projekt
2. Klicken Sie auf "Logs"
3. Wählen Sie den entsprechenden Service

## 📈 Monitoring

### Health Check URLs
- **App Health:** `https://ihre-domain.com/health`
- **Shlink Health:** `https://ihre-domain.com:8080/rest/v3/health`

### Wichtige Metriken
- Redis-Verbindung
- Shlink-Datenbank
- VAPI-API-Verbindung

## 🔒 Sicherheit

### Empfohlene Einstellungen
- Starke Passwörter für Redis
- HTTPS für alle externen URLs
- Regelmäßige Updates

### Environment Variables
- Niemals echte Keys in Git committen
- Verwenden Sie Coolify Secrets für sensible Daten

## 📞 Support

Bei Problemen:
1. Prüfen Sie die Logs
2. Testen Sie die Health Checks
3. Kontaktieren Sie den Support

## 🎉 Fertig!

Nach erfolgreichem Deployment haben Sie:
- ✅ Vollständige VAPI Demo-Anwendung
- ✅ URL-Shortening mit Shlink
- ✅ Session-Management mit Redis
- ✅ Professionelle Branding-Optionen

**Ihre VAPI Demo ist bereit für den Einsatz!** 🚀