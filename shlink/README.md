# Shlink Integration

## 🔗 Übersicht
Integration mit Shlink URL-Shortener für Link-Management im Lead-Prozess.

## 📁 Dateien

### Dokumentation
- **`SHLINK_API_ANLEITUNG.md`** - Vollständige Anleitung für Shlink API

### Skripte
- **`shlink_helper.py`** - Helper-Funktionen für Shlink-Operationen
- **`test_shlink.py`** - Test-Skripte für Shlink-Integration

## 🚀 Verwendung

### Link-Generierung
```python
from shlink_helper import ShlinkHelper

shlink = ShlinkHelper(
    api_url="https://demo.bifrotek.com/rest/v3",
    api_key="your_api_key",
    default_domain="demo.bifrotek.com"
)

# Short Link erstellen
short_link = shlink.create_short_link(
    long_url="https://example.com",
    title="Lead Tracking Link"
)
```

### Wasserfall-Integration
- **Long Link** - Personalisierte URLs mit Lead-Parametern
- **Short Link** - Kurze, trackbare URLs
- **Link-Validierung** - Erreichbarkeit testen
- **Analytics** - Klick-Tracking und Statistiken

## 🔧 Setup

### Umgebungsvariablen
```bash
SHLINK_API_URL=https://demo.bifrotek.com/rest/v3
SHLINK_API_KEY=your_api_key
SHLINK_DEFAULT_DOMAIN=demo.bifrotek.com
```

### Docker-Setup
```bash
# Shlink mit MySQL
docker-compose -f shlink-config/coolify-mysql-docker-compose.yml up -d
```

## 📊 Features

### Link-Management
- Automatische Short-Link-Generierung
- Custom Domain Support
- Link-Validierung
- Analytics und Tracking

### Lead-Integration
- Personalisierte Parameter
- UTM-Tracking
- Conversion-Tracking
- A/B-Testing Support

## 🔗 API-Endpoints

- **POST** `/rest/v3/short-urls` - Short Link erstellen
- **GET** `/rest/v3/short-urls` - Links auflisten
- **GET** `/rest/v3/short-urls/{shortCode}` - Link-Details
- **GET** `/rest/v3/short-urls/{shortCode}/visits` - Analytics

## 🎯 Nächste Schritte

1. Shlink-Service stabilisieren
2. Analytics-Dashboard erstellen
3. A/B-Testing für Links implementieren
4. Automatische Link-Rotation
