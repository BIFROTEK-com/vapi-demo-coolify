# Shlink Link Shortener API - Anleitung

## Übersicht
Die Shlink API wird verwendet, um lange Landing Page URLs zu kurzen, benutzerfreundlichen Links zu verkürzen.

## Credentials
- **API Key**: `0f44e6fa0477e39539b988adf1c36510234606718cda43f8a037c6fc0dc451c3`
- **Domain**: `demo.bifrotek.com`
- **Base URL**: `https://demo.bifrotek.com/rest/v3`

## Installation
```bash
python -m pip install requests
```

## API Verwendung

### Python Code
```python
import requests

url = "https://demo.bifrotek.com/rest/v3/short-urls"

payload = {
    "longUrl": "https://custom-demo.bifrotek.com/webapp?customer_domain=planity.de&customer_name=Kevin%20Wolter&customer_email=kevin@planity.de&company_name=Planity",
    "title": "Planity Demo",
    "tags": ["campaign", "demo", "planity"]
}

headers = {
    "X-Api-Key": "0f44e6fa0477e39539b988adf1c36510234606718cda43f8a037c6fc0dc451c3",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

print(response.text)
```

### Parameter Erklärung
- **longUrl**: Die vollständige URL der Landing Page
- **title**: Titel für den Link (optional)
- **tags**: Tags für bessere Organisation (optional)
- **customSlug**: Gewünschter Kurzcode (optional, z.B. "planity" → demo.bifrotek.com/planity)

### Beispiel URLs
- **Original**: `https://custom-demo.bifrotek.com/webapp?customer_domain=planity.de&customer_name=Kevin%20Wolter&customer_email=kevin@planity.de&company_name=Planity`
- **Short**: `https://demo.bifrotek.com/planity`

## Verwendung für Autocampaign
1. Erstelle Landing Page URL mit allen Parametern
2. URL-encode die Parameter
3. Rufe Shlink API auf
4. Verwende den generierten Short Link in E-Mails/SMS

## Response Format
```json
{
  "shortUrl": "https://demo.bifrotek.com/planity",
  "shortCode": "planity",
  "longUrl": "https://custom-demo.bifrotek.com/webapp?...",
  "dateCreated": "2025-09-16T13:51:55+02:00",
  "title": "Planity Demo",
  "tags": ["campaign", "demo", "planity"],
  "visitsSummary": {
    "total": 0,
    "nonBots": 0,
    "bots": 0
  }
}
```

## Vorteile gegenüber Rebrandly
- ✅ **Self-hosted**: Vollständige Kontrolle über die Daten
- ✅ **Keine Kosten**: Open Source, keine monatlichen Gebühren
- ✅ **Bessere Performance**: Lokale Infrastruktur
- ✅ **Detaillierte Analytics**: Umfassende Besucher-Statistiken
- ✅ **Custom Domain**: Eigene Domain ohne Zusatzkosten
- ✅ **API Limits**: Keine Beschränkungen auf API-Aufrufe
