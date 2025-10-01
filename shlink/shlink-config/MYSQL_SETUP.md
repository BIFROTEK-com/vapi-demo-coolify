# 🗄️ Shlink MySQL Setup für Coolify

## ✅ **MySQL-basierte Produktionskonfiguration erstellt!**

### **📁 Neue Dateien:**

1. **`coolify-mysql-docker-compose.yml`** - MySQL Docker Compose für Coolify
2. **`coolify-mysql-env.txt`** - MySQL Umgebungsvariablen für Coolify
3. **`docker-compose.yml`** - MySQL Docker Compose für lokale Entwicklung

### **🔧 Services in der Konfiguration:**

#### **1. MySQL 8.0 Database:**
- **Container:** `shlink_mysql`
- **Port:** `3306`
- **Datenbank:** `shlink`
- **User:** `shlink_user`
- **Health Check:** ✅ Aktiv

#### **2. Shlink URL Shortener:**
- **Container:** `shlink`
- **Port:** `8081` (extern) → `8080` (intern)
- **Datenbank:** MySQL (nicht SQLite!)
- **Health Check:** ✅ Aktiv
- **Dependencies:** Wartet auf MySQL

#### **3. Redis Cache (Optional):**
- **Container:** `shlink_redis`
- **Port:** `6379`
- **Memory:** 256MB mit LRU Policy
- **Health Check:** ✅ Aktiv

### **🚀 Coolify Deployment:**

#### **Schritt 1: Docker Compose**
```bash
# In Coolify verwenden:
coolify-mysql-docker-compose.yml
```

#### **Schritt 2: Umgebungsvariablen**
```bash
# Alle Variablen aus:
coolify-mysql-env.txt
```

#### **Schritt 3: Passwörter ändern**
```bash
# WICHTIG: Vor Produktion ändern!
MYSQL_ROOT_PASSWORD=shlink_root_password_2024
MYSQL_PASSWORD=shlink_secure_password_2024
INITIAL_API_KEY=0f44e6fa0477e39539b988adf1c36510234606718cda43f8a037c6fc0dc451c3
```

### **⚡ MySQL Vorteile:**

#### **✅ Produktionsbereit:**
- Offiziell von Shlink unterstützt
- Keine Datenverlust-Risiken
- ACID-Compliance
- Transaktionssicherheit

#### **✅ Performance:**
- Hohe Concurrent Users
- Optimierte Abfragen
- Replikation möglich
- Backup/Recovery

#### **✅ Skalierbar:**
- Horizontale Skalierung
- Load Balancing
- Clustering möglich

### **🔒 Sicherheit:**

#### **Datenbank-Verschlüsselung:**
```bash
DB_USE_ENCRYPTION=true
```

#### **CORS Konfiguration:**
```bash
CORS_ALLOW_ORIGINS=*
CORS_ALLOW_HEADERS=*
CORS_ALLOW_METHODS=*
CORS_MAX_AGE=3600
```

### **📊 Monitoring:**

#### **Prometheus Metrics:**
```bash
ENABLE_METRICS=true
METRICS_DRIVER=prometheus
METRICS_ENDPOINT=/metrics
```

#### **Strukturierte Logs:**
```bash
LOG_LEVEL=info
LOG_FORMAT=json
LOG_FILE=/var/log/shlink.log
```

### **🎯 Features:**

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

### **⚠️ Wichtige Hinweise:**

1. **SQLite ist NICHT für Produktion empfohlen!**
2. **MySQL ist die offizielle Empfehlung für Produktion**
3. **Passwörter vor Deployment ändern!**
4. **Backup-Strategien für MySQL implementieren**
5. **GeoLite2 License Key nach E-Mail-Eingang aktualisieren**

### **🔧 Nächste Schritte:**

1. **In Coolify deployen:**
   - `coolify-mysql-docker-compose.yml` verwenden
   - Umgebungsvariablen aus `coolify-mysql-env.txt` kopieren

2. **Passwörter ändern:**
   - Alle Passwörter vor Produktion ändern
   - Sichere Passwörter verwenden

3. **GeoLite2 License Key:**
   - E-Mail für License Key abwarten
   - `GEOLITE_LICENSE_KEY` aktualisieren

4. **Container neu starten:**
   - Nach Passwort-Änderungen
   - Nach License Key Eingabe

**Shlink ist bereit für die MySQL-Produktion!** 🚀
