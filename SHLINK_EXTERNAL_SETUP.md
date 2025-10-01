# Externer Shlink-Service Setup

## Übersicht

Diese Anleitung zeigt, wie Sie einen externen Shlink-Service für die VAPI Demo App konfigurieren.

## Option 1: Coolify Shlink-Service (Empfohlen)

### 1. Shlink bei Coolify deployen

1. **Neues Projekt in Coolify erstellen**
2. **Docker Compose Repository hinzufügen:**
   ```yaml
   # docker-compose.yaml für Shlink
   version: '3.8'
   
   services:
     mysql:
       image: mysql:8.0
       container_name: shlink_mysql
       restart: unless-stopped
       environment:
         - MYSQL_ROOT_PASSWORD=shlink_root_password_2024
         - MYSQL_DATABASE=shlink
         - MYSQL_USER=shlink_user
         - MYSQL_PASSWORD=shlink_secure_password_2024
       volumes:
         - mysql_data:/var/lib/mysql
       healthcheck:
         test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-p$$MYSQL_ROOT_PASSWORD"]
         interval: "30s"
         timeout: "10s"
         retries: 5
         start_period: "30s"
   
     shlink:
       image: shlinkio/shlink:stable
       container_name: shlink
       restart: unless-stopped
       depends_on:
         mysql:
           condition: service_healthy
       environment:
         - DEFAULT_DOMAIN=your-domain.com
         - IS_HTTPS_ENABLED=true
         - GEOLITE_LICENSE_KEY=your_geolite_license_key_here
         - INITIAL_API_KEY=your_initial_api_key_here
         - DB_DRIVER=mysql
         - DB_HOST=mysql
         - DB_USER=shlink_user
         - DB_PASSWORD=shlink_secure_password_2024
         - DB_NAME=shlink
         - DB_PORT=3306
         - DB_USE_ENCRYPTION=true
         - TIMEZONE=Europe/Berlin
         - LOGS_FORMAT=json
         - MEMORY_LIMIT=512M
         - DEFAULT_SHORT_CODES_LENGTH=5
         - AUTO_RESOLVE_TITLES=true
         - DELETE_SHORT_URL_THRESHOLD=0
         - REDIRECT_STATUS_CODE=302
         - REDIRECT_CACHE_LIFETIME=30
         - REDIRECT_EXTRA_PATH_MODE=append
         - DEFAULT_QR_CODE_SIZE=300
         - DEFAULT_QR_CODE_MARGIN=1
         - DEFAULT_QR_CODE_FORMAT=png
         - DEFAULT_QR_CODE_ERROR_CORRECTION=L
         - DEFAULT_QR_CODE_ROUND_BLOCK_SIZE=true
         - QR_CODE_FOR_DISABLED_SHORT_URLS=true
         - REDIS_SERVERS=redis://redis:6379
         - REDIS_PUBLIC_IP=redis
         - REDIS_SENTINEL_SERVICE=shlink
         - CORS_ALLOW_ORIGINS=*
         - CORS_ALLOW_HEADERS=*
         - CORS_ALLOW_METHODS=*
         - CORS_MAX_AGE=3600
         - ENABLE_METRICS=true
         - METRICS_DRIVER=prometheus
         - METRICS_ENDPOINT=/metrics
         - LOG_LEVEL=info
         - LOG_FORMAT=json
         - LOG_FILE=/var/log/shlink.log
       volumes:
         - shlink_data:/var/www/html/data
         - shlink_logs:/var/log
       healthcheck:
         test: ["CMD", "wget", "--spider", "http://localhost:8080/rest/v3/health"]
         interval: "30s"
         timeout: "10s"
         retries: 3
         start_period: "60s"
   
     redis:
       image: redis:7-alpine
       container_name: shlink_redis
       restart: unless-stopped
       command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
       volumes:
         - redis_data:/data
       healthcheck:
         test: ["CMD", "redis-cli", "ping"]
         interval: "30s"
         timeout: "10s"
         retries: 3
         start_period: "30s"
   
   volumes:
     mysql_data:
       driver: local
     shlink_data:
       driver: local
     shlink_logs:
       driver: local
     redis_data:
       driver: local
   ```

3. **Deployen und warten, bis alle Services healthy sind**

### 2. VAPI Demo App konfigurieren

1. **In Ihrer .env Datei:**
   ```bash
   # Shlink Configuration (External Service)
   SHLINK_BASE_URL=https://your-shlink-domain.com/rest/v3
   SHLINK_API_KEY=your_initial_api_key_here
   SHLINK_DOMAIN=your-shlink-domain.com
   SHLINK_HTTPS=true
   ```

2. **VAPI Demo App deployen:**
   ```bash
   git clone https://github.com/BIFROTEK-com/vapi-demo-coolify.git
   cd vapi-demo-coolify
   cp .env.example .env
   # .env mit Ihren Werten füllen
   docker-compose up -d
   ```

## Option 2: Externe Shlink-Instanz

### 1. Shlink-Instanz einrichten

- **Shlink.io Cloud** (https://shlink.io)
- **Eigene VPS-Instanz** mit Shlink
- **Bestehende Shlink-Instanz**

### 2. API-Key generieren

1. **Shlink-Webinterface öffnen**
2. **API-Keys → New API Key**
3. **Berechtigungen:** Alle Rechte
4. **API-Key kopieren**

### 3. VAPI Demo App konfigurieren

```bash
# In .env
SHLINK_BASE_URL=https://your-shlink-instance.com/rest/v3
SHLINK_API_KEY=your_generated_api_key
SHLINK_DOMAIN=your-shlink-instance.com
SHLINK_HTTPS=true
```

## Testen

### 1. Shlink-Health-Check

```bash
curl https://your-shlink-domain.com/rest/v3/health
```

### 2. Short Link erstellen

```bash
curl -X POST "https://your-shlink-domain.com/rest/v3/short-urls" \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: your_api_key" \
  -d '{
    "longUrl": "https://example.com",
    "title": "Test Link"
  }'
```

### 3. VAPI Demo App testen

```bash
curl http://localhost:8000/webapp?customer_domain=test.com&customer_name=Test&customer_email=test@test.com&company_name=Test%20Company
```

## Troubleshooting

### Shlink nicht erreichbar

1. **Domain/DNS prüfen**
2. **Firewall/Ports prüfen**
3. **SSL-Zertifikat prüfen**

### API-Key-Fehler

1. **API-Key korrekt kopiert?**
2. **Berechtigungen ausreichend?**
3. **Shlink-Instanz läuft?**

### CORS-Fehler

1. **CORS_ALLOW_ORIGINS=* in Shlink-Konfiguration**
2. **Domain in CORS-Whitelist**

## Support

Bei Problemen:
- **GitHub Issues:** https://github.com/BIFROTEK-com/vapi-demo-coolify/issues
- **Dokumentation:** https://shlink.io/documentation/
