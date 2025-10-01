# Redis Integration für VAPI Demo Builder

Diese Dokumentation beschreibt die Redis-Integration für Session-Management und Cross-Worker-Kommunikation im VAPI Demo Builder.

## Übersicht

Die Redis-Integration ermöglicht:
- **Session-Management**: Persistente Speicherung von Browser-Sessions
- **Message Broadcasting**: Cross-Worker-Kommunikation für Webhook-Messages
- **SSE (Server-Sent Events)**: Echtzeit-Message-Streaming an Frontend-Clients
- **Fallback-Mechanismus**: Automatischer Fallback auf In-Memory-Storage wenn Redis nicht verfügbar

## Konfiguration

### Environment Variables

Fügen Sie folgende Variablen zu Ihrer `.env` Datei hinzu:

```bash
# Redis Configuration
REDIS_URL=redis://redis:6379
REDIS_PASSWORD=your-redis-password-here

# Für externe Redis-Instanzen (z.B. Upstash)
# REDIS_URL=redis://default:your-redis-password@redis-12345.upstash.io:6379
```

### Deployment-Optionen

#### 1. Lokale Entwicklung (Docker Compose)

Redis wird automatisch als Container bereitgestellt:

```yaml
# docker-compose.yml
redis:
  image: redis:7-alpine
  container_name: vapi-redis
  ports:
    - "6379:6379"
  command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
```

**Setup:**
1. Kopieren Sie `env.example` zu `.env`
2. Setzen Sie `REDIS_PASSWORD` in der `.env`
3. Starten Sie mit `docker-compose up`

#### 2. Coolify Docker Deployment

Redis wird intern von Coolify bereitgestellt:

```yaml
# coolify.yml
redis:
  image: redis:7-alpine
  container_name: vapi-redis
  command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
```

**Setup:**
1. Setzen Sie `REDIS_PASSWORD` in Coolify Environment Variables
2. Deployen Sie die Anwendung

#### 3. Externe Redis-Instanz (Produktion)

Für Produktionsumgebungen können externe Redis-Instanzen verwendet werden:

- **Upstash Redis**: Cloud-basierte Redis-Instanz
- **AWS ElastiCache**: Managed Redis-Service
- **Eigene Redis-Instanz**: Self-hosted Redis-Server

**Konfiguration testen:**
```bash
# Health Check mit Redis-Status
curl http://localhost:8000/health
```

## Architektur

### Redis Service (`app/services/redis_service.py`)

Der `RedisService` bietet folgende Funktionen:

```python
# Session Management
await redis_service.store_session(session_id, session_data, ttl=3600)
session_data = await redis_service.get_session(session_id)
await redis_service.delete_session(session_id)

# Message Broadcasting
await redis_service.store_webhook_message(session_id, message_data, ttl=3600)
messages = await redis_service.get_webhook_messages(session_id)

# Cross-Worker Communication
await redis_service.publish_message(channel, message_data)
await redis_service.subscribe_to_channel(channel, callback)

# Redis Info
redis_info = await redis_service.get_redis_info()
```

### Integration in FastAPI (`app/main.py`)

Die Integration erfolgt über:

1. **Startup Event**: Automatische Redis-Verbindung beim App-Start
2. **Session Registration**: Speicherung in Redis mit Fallback
3. **Message Streaming**: Redis-basierte Message-Übertragung
4. **Webhook Handling**: Redis für Message-Broadcasting

## Verwendung

### Session Management

```python
# Session registrieren
POST /api/register-browser-session
{
    "browser_session_id": "unique-session-id",
    "customer_domain": "example.com",
    "customer_name": "John Doe",
    "customer_email": "john@example.com",
    "company_name": "Example Corp"
}
```

### Message Streaming

```python
# SSE Stream für Messages
GET /api/message-stream/{browser_session_id}
# Response: text/event-stream

# Webhook Message senden
POST /webhook/vapi/send-message
{
    "message": {
        "role": "assistant",
        "content": "Hello from VAPI!"
    },
    "sessionId": "unique-session-id"  # Optional für Broadcast
}
```

### Health Check

```python
# Redis-Status überprüfen
GET /health
# Response:
{
    "status": "healthy",
    "timestamp": "2025-01-27T10:30:00Z",
    "redis": {
        "connected": true,
        "redis_version": "7.0.0",
        "used_memory_human": "1.2M",
        "connected_clients": "5"
    }
}
```

## Datenstruktur

### Session Storage

```json
{
    "customer_domain": "example.com",
    "customer_name": "John Doe",
    "customer_email": "john@example.com",
    "company_name": "Example Corp",
    "created_at": "2025-01-27T10:30:00Z",
    "updated_at": "2025-01-27T10:30:00Z"
}
```

### Webhook Messages

```json
{
    "content": "Hello from VAPI!",
    "role": "assistant",
    "timestamp": "2025-01-27T10:30:00Z",
    "source": "voice-function"
}
```

## Redis Keys

- `session:{session_id}`: Session-Daten (TTL: 1 Stunde)
- `webhook_messages:{session_id}`: Message-Queue (TTL: 1 Stunde)

## Fallback-Mechanismus

Wenn Redis nicht verfügbar ist:

1. **Automatischer Fallback** auf In-Memory-Storage
2. **Keine Funktionalitätsverluste** - alle Features funktionieren weiter
3. **Single-Worker-Modus** - Cross-Worker-Kommunikation nicht verfügbar
4. **Logging** - Warnung wird in den Logs ausgegeben

## Testing

### Unit Tests

```bash
# Redis Service Tests
pytest tests/test_redis_service.py -v

# Integration Tests
pytest tests/test_redis_integration.py -v

# Alle Tests
pytest tests/ -v
```

### Test Coverage

- ✅ Redis-Verbindung (erfolgreich/fehlgeschlagen)
- ✅ Session-Management (speichern/abrufen/löschen)
- ✅ Message-Broadcasting
- ✅ SSE-Streaming
- ✅ Fallback-Mechanismus
- ✅ Error-Handling

## Monitoring

### Redis-Status überwachen

```bash
# Health Check
curl http://localhost:8000/health | jq '.redis'

# Docker Container Status
docker ps | grep redis

# Redis Container Logs
docker logs vapi-redis
```

### Logs überwachen

```bash
# Redis-Verbindungsstatus
grep "Redis" logs/app.log

# Session-Aktivität
grep "session" logs/app.log

# Message-Broadcasting
grep "webhook" logs/app.log

# Docker Redis Logs
docker logs vapi-redis --follow
```

## Troubleshooting

### Häufige Probleme

1. **Redis-Verbindung fehlgeschlagen**:
   - Überprüfen Sie die `REDIS_URL` und `REDIS_PASSWORD` in der `.env`
   - Stellen Sie sicher, dass Redis-Container läuft: `docker ps | grep redis`
   - Prüfen Sie Container-Logs: `docker logs vapi-redis`

2. **Sessions werden nicht gespeichert**:
   - Überprüfen Sie Redis-Container-Status
   - Testen Sie mit `/health` Endpoint
   - Prüfen Sie Redis-Logs: `docker logs vapi-redis`

3. **Messages kommen nicht an**:
   - Überprüfen Sie Session-Registration
   - Testen Sie Webhook-Endpoints
   - Prüfen Sie Redis-Verbindung

### Debug-Modus

```bash
# Debug-Logging aktivieren
DEBUG=true python -m uvicorn app.main:app --reload

# Redis-Verbindung testen
python -c "
from app.services.redis_service import redis_service
import asyncio
print(asyncio.run(redis_service.connect()))
"
```

## Performance

### Optimierungen

- **Connection Pooling**: Automatisch durch `redis.asyncio`
- **TTL-Management**: Automatische Bereinigung alter Sessions
- **Batch-Operations**: Effiziente Message-Broadcasting
- **Fallback-Caching**: In-Memory-Cache als Backup

### Skalierung

- **Multi-Worker**: Redis ermöglicht Cross-Worker-Kommunikation
- **Horizontal Scaling**: Mehrere App-Instanzen können dieselbe Redis-Instanz nutzen
- **Load Balancing**: Sessions sind worker-übergreifend verfügbar

## Sicherheit

### Best Practices

- **Credentials**: Verwenden Sie starke Passwörter
- **TLS**: Upstash Redis verwendet standardmäßig TLS
- **TTL**: Sessions haben automatische Ablaufzeit
- **Validation**: Alle Daten werden validiert vor Speicherung

### Docker Security

- **Container Isolation**: Redis läuft in isoliertem Container
- **Password Protection**: Redis ist mit Passwort geschützt
- **Network Security**: Container-zu-Container Kommunikation
- **Volume Persistence**: Daten werden in Docker-Volumes gespeichert

### Externe Redis-Instanzen (Produktion)

Für Produktionsumgebungen mit externen Redis-Instanzen:

- **Upstash Redis**: Cloud-basierte Redis-Instanz mit VPC-Isolation
- **AWS ElastiCache**: Managed Redis-Service mit Security Groups
- **Eigene Redis-Instanz**: Self-hosted mit Firewall-Konfiguration
