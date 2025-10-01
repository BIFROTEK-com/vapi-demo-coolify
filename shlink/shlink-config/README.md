# Shlink URL Shortener - MySQL Produktionskonfiguration

## ✅ **Status: MySQL-basiert für Coolify Produktion!**

### **Docker Compose Dateien:**
- `coolify-mysql-docker-compose.yml` - **MySQL-basiert für Coolify** (Empfohlen)
- `docker-compose.yml` - **MySQL-basiert für lokale Entwicklung**
- `shlink-config/docker-compose.yml` - SQLite Version (nur für Tests)

### **Umgebungsvariablen:**
- `coolify-mysql-env.txt` - **MySQL-Umgebungsvariablen für Coolify** (Empfohlen)
- `coolify-ready-env.txt` - SQLite Version (nur für Tests)

## 🗄️ **MySQL Konfiguration (Produktionsbereit):**

### **Datenbank-Setup:**
```yaml
# MySQL 8.0 mit Health Checks
mysql:
  image: mysql:8.0
  environment:
    - MYSQL_ROOT_PASSWORD=shlink_root_password_2024
    - MYSQL_DATABASE=shlink
    - MYSQL_USER=shlink_user
    - MYSQL_PASSWORD=shlink_secure_password_2024
```

### **Shlink MySQL Integration:**
```bash
# Database Configuration (MySQL)
DB_DRIVER=mysql
DB_HOST=mysql
DB_USER=shlink_user
DB_PASSWORD=shlink_secure_password_2024
DB_NAME=shlink
DB_PORT=3306
DB_USE_ENCRYPTION=true
```

## 🚀 **Coolify Deployment:**

### **1. Docker Compose verwenden:**
- Kopieren Sie `coolify-mysql-docker-compose.yml` in Coolify
- Oder verwenden Sie die Datei direkt als Quelle

### **2. Umgebungsvariablen setzen:**
- Kopieren Sie alle Variablen aus `coolify-mysql-env.txt`
- **WICHTIG:** Passwörter für Produktion ändern!

### **3. Services:**
- **MySQL**: Datenbank mit Health Checks
- **Shlink**: URL Shortener mit MySQL
- **Redis**: Caching (Optional aber empfohlen)

## ⚡ **Performance Features:**

### **MySQL Vorteile:**
- ✅ **Produktionsbereit** - Offiziell unterstützt
- ✅ **Hohe Performance** - Optimiert für Last
- ✅ **ACID-Compliance** - Transaktionssicherheit
- ✅ **Replikation** - Backup/Recovery möglich
- ✅ **Skalierbar** - Concurrent Users unterstützt

### **Redis Caching:**
```bash
REDIS_SERVERS=redis://redis:6379
REDIS_PUBLIC_IP=redis
REDIS_SENTINEL_SERVICE=shlink
```

## 🔒 **Sicherheit:**

### **Datenbank-Verschlüsselung:**
```bash
DB_USE_ENCRYPTION=true
```

### **CORS Konfiguration:**
```bash
CORS_ALLOW_ORIGINS=*
CORS_ALLOW_HEADERS=*
CORS_ALLOW_METHODS=*
CORS_MAX_AGE=3600
```

## 📊 **Monitoring:**

### **Prometheus Metrics:**
```bash
ENABLE_METRICS=true
METRICS_DRIVER=prometheus
METRICS_ENDPOINT=/metrics
```

### **Strukturierte Logs:**
```bash
LOG_LEVEL=info
LOG_FORMAT=json
LOG_FILE=/var/log/shlink.log
```

## 🎯 **Features:**
- 🔗 **URL Shortening**: 5-stellige Codes
- 📊 **Analytics**: Erweiterte Statistiken
- 🌍 **Geolocation**: Nach License Key
- 🔒 **Sicherheit**: API Key + MySQL Verschlüsselung
- ⚡ **Performance**: MySQL + Redis Caching
- 🎯 **Auto-Title Resolution**: Automatische Titel-Erkennung
- 🔄 **Smart Redirects**: 302 Redirects mit Caching
- 📱 **QR Codes**: PNG-Format mit Fehlerkorrektur
- 🌍 **Timezone**: Europe/Berlin
- 📝 **JSON Logging**: Strukturierte Logs
- 🗄️ **MySQL**: Produktionsdatenbank
- ⚡ **Redis**: Caching für Performance

## 🔧 **Nächste Schritte:**

1. **In Coolify deployen:**
   - `coolify-mysql-docker-compose.yml` verwenden
   - Umgebungsvariablen aus `coolify-mysql-env.txt` kopieren

2. **Passwörter ändern:**
   - `MYSQL_ROOT_PASSWORD` ändern
   - `MYSQL_PASSWORD` ändern
   - `INITIAL_API_KEY` ändern

3. **GeoLite2 License Key:**
   - E-Mail für License Key abwarten
   - `GEOLITE_LICENSE_KEY` aktualisieren

4. **Container neu starten:**
   - Nach Passwort-Änderungen
   - Nach License Key Eingabe

## ⚠️ **Wichtige Hinweise:**

- **SQLite ist NICHT für Produktion empfohlen!**
- **MySQL ist die offizielle Empfehlung für Produktion**
- **Passwörter vor Deployment ändern!**
- **Backup-Strategien für MySQL implementieren**

**Shlink ist bereit für die MySQL-Produktion!** 🚀