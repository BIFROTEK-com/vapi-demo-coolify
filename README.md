# 🚀 VAPI Demo Builder

Ein vollständiger VAPI Demo Builder mit URL-Shortening, Session-Management und professionellem Branding.

## ✨ Features

- **VAPI Integration** - Vollständige VAPI-Assistant-Integration
- **URL Shortening** - Integrierte Shlink-Instanz
- **Session Management** - Redis-basierte Session-Verwaltung
- **Professional Branding** - Anpassbare Farben, Logo und Texte
- **Coolify Ready** - Ein-Klick-Deployment bei Coolify
- **Health Monitoring** - Vollständige Health Checks

## 🎯 Schnellstart

### 1. Repository klonen
```bash
git clone https://github.com/ihr-username/vapi-demo-coolify.git
cd vapi-demo-coolify
```

### 2. Environment konfigurieren
```bash
cp .env.example .env
# Bearbeiten Sie .env mit Ihren Werten
```

### 3. Bei Coolify deployen
1. Neues Projekt in Coolify erstellen
2. Repository verbinden
3. Docker Compose als Build-Methode wählen
4. `coolify.yml` als Konfigurationsdatei verwenden
5. Environment Variables aus `.env` eintragen
6. Deploy starten

## 📋 Voraussetzungen

- Coolify-Instanz
- VAPI-Account mit API-Keys
- Domain für Ihre Anwendung

## 🔧 Konfiguration

### VAPI-Konfiguration
1. Gehen Sie zu [VAPI Dashboard](https://dashboard.vapi.ai)
2. Erstellen Sie einen neuen Assistant
3. Kopieren Sie die Keys in Ihre `.env`-Datei

### Domain-Konfiguration
Setzen Sie in Ihrer `.env`-Datei:
- `WEBSITE_URL=https://ihre-domain.com`
- `SHLINK_DOMAIN=ihre-domain.com`
- `SHLINK_HTTPS=true`

## 📊 Services

Die Anwendung besteht aus 4 Services:

1. **vapi-demo** - Hauptanwendung (Port 8000)
2. **redis** - Session-Management
3. **shlink** - URL-Shortening (Port 8080)
4. **shlink-db** - PostgreSQL-Datenbank

## 🔍 Health Checks

- **App Health:** `https://ihre-domain.com/health`
- **Shlink Health:** `https://ihre-domain.com:8080/rest/v3/health`

## 📚 Dokumentation

- [Coolify Deployment Guide](COOLIFY_DEPLOYMENT.md)
- [Redis Integration](REDIS_INTEGRATION.md)
- [Shlink Setup](shlink/SHLINK_SETUP.md)

## 🛠️ Support

Bei Problemen:
1. Prüfen Sie die Logs in Coolify
2. Testen Sie die Health Checks
3. Kontaktieren Sie den Support

## 📄 Lizenz

MIT License - siehe [LICENSE](LICENSE) für Details.

## 🤝 Contributing

Contributions sind willkommen! Bitte erstellen Sie einen Pull Request.

---

**Ihre VAPI Demo ist bereit für den Einsatz!** 🚀