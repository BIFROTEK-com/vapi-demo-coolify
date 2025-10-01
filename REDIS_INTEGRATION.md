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
# Upstash Redis URL (empfohlen für Production)
REDIS_URL=redis://default:your-redis-password@redis-12345.upstash.io:6379

# Alternative: Redis Credentials (falls URL nicht verwendet wird)
REDIS_USERNAME=default
REDIS_PASSWORD=your-redis-password
```

### Upstash Redis Setup

1. **Datenbank erstellen**:
   - Gehen Sie zu [Upstash Console](https://console.upstash.com)
   - Erstellen Sie eine neue Redis-Datenbank
   - Wählen Sie die nächstgelegene Region (z.B. Frankfurt, Germany)

2. **Credentials abrufen**:
   - Kopieren Sie die Redis URL aus der Upstash Console
   - Oder notieren Sie sich Username und Password separat

3. **Konfiguration testen**:
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

# Upstash Console
# Gehen Sie zu https://console.upstash.com für detaillierte Metriken
```

### Logs überwachen

```bash
# Redis-Verbindungsstatus
grep "Redis" logs/app.log

# Session-Aktivität
grep "session" logs/app.log

# Message-Broadcasting
grep "webhook" logs/app.log
```

## Troubleshooting

### Häufige Probleme

1. **Redis-Verbindung fehlgeschlagen**:
   - Überprüfen Sie die `REDIS_URL` in der `.env`
   - Stellen Sie sicher, dass Upstash Redis läuft
   - Prüfen Sie Firewall-Einstellungen

2. **Sessions werden nicht gespeichert**:
   - Überprüfen Sie Redis-Logs in der Upstash Console
   - Testen Sie mit `/health` Endpoint

3. **Messages kommen nicht an**:
   - Überprüfen Sie Session-Registration
   - Testen Sie Webhook-Endpoints

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

### Upstash Security

- **VPC**: Private Netzwerk-Isolation möglich
- **Encryption**: Daten werden verschlüsselt übertragen und gespeichert
- **Access Control**: IP-Whitelisting verfügbar
