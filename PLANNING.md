## Project Planning

### Goal
Set up a minimal, reliable FastAPI server that serves a static page embedding the VAPI widget provided by the user, with environment-driven configuration and tests.

### Architecture
- **Framework**: FastAPI
- **Templating**: Jinja2 for rendering the HTML page
- **Config/Validation**: `pydantic` BaseSettings for `assistant_id` and `public_key`
- **Server**: Uvicorn (ASGI)
- **Tests**: `pytest` with FastAPI TestClient

### Modules
- `app/config.py`: Pydantic settings for `assistant_id` and `public_key`, with defaults matching the provided widget. Includes a cache reset helper for tests.
- `app/main.py`: FastAPI app, routes `/` (serves widget page) and `/health` (simple healthcheck).
- `app/templates/index.html`: Jinja2 template embedding the widget and script include, rendering configured IDs.

### Conventions
- Python, PEP8, type hints, Black-compatible formatting.
- Short, well-named functions and clear responsibilities per file (keep files < 500 LOC).
- Tests in `tests/` mirroring app structure.

### Configuration
Environment variables (optional, with safe defaults):
- `ASSISTANT_ID`: UUID for the VAPI assistant ID.
- `PUBLIC_KEY`: UUID for the VAPI public key.

### Testing Strategy
- Happy path: `/` returns 200 and contains the widget tag with configured IDs.
- Edge case: override IDs via env and verify rendered output.
- Failure case: invalid UUIDs should cause settings validation error.

## Vapi Assistant Overrides - Technische Dokumentation

### Problem (Stand: Sept 2025)
Die Vapi Assistant Overrides wurden nicht korrekt an Vapi übertragen. Insbesondere `conversation_context` fehlte in den Vapi Call Logs, obwohl andere Variablen (`customer_domain`, `customer_name`, etc.) funktionierten.

### Ursache
Das Vapi Web SDK Widget cachte die `assistantOverrides` bei der Initialisierung (in `vapi-credentials.js`):

```javascript
vapiInstance = window.vapiSDK.run({
    apiKey: apiKey,
    assistant: assistant,
    config: buttonConfig,
    assistantOverrides: window.VAPI_CONFIG.assistantOverrides // Gecacht beim Start!
});
```

Wenn später `conversation_context` dynamisch aktualisiert wurde (z.B. mit Chat-Historie), wurden diese Änderungen vom Widget ignoriert.

### Lösung
Die Vapi SDK `start()` Methode akzeptiert `assistantOverrides` als zweiten Parameter. Dies überschreibt die gecachten Werte:

```javascript
// In voice-functions.js - startVoiceCall()
const assistantOverrides = {
    variableValues: {
        ...window.VAPI_CONFIG.assistantOverrides.variableValues,
        conversation_context: conversationContext || 'Keine vorherigen Nachrichten'
    }
};

// Übergibt frische Overrides direkt an start()
window.vapi.start(window.VAPI_CONFIG.assistantId, assistantOverrides);
```

### Wichtige Erkenntnisse

1. **Vapi überträgt keine leeren Strings**: Wenn `conversation_context` ein leerer String ist, wird es nicht in `variableValues` übertragen. Lösung: Default-Wert verwenden.

2. **Extra Variablen von Vapi**: Die Call Logs zeigen zusätzliche Variablen, die Vapi selbst hinzufügt:
   - `now`: Aktueller Zeitstempel
   - `chat_history`: "[]" (von Vapi)
   - `current_browser_session`: "no_session"
   - `vapi_session_id`: "no_session"

3. **Script-Reihenfolge kritisch**: `VAPI_CONFIG` muss vor allen anderen Scripts definiert werden (in `public_webapp.html`).

### Architektur-Entscheidungen

1. **Zentrale Konfiguration**: `window.VAPI_CONFIG` als Single Source of Truth in `public_webapp.html`
2. **Dynamische Updates**: Assistant Overrides werden bei jedem Voice Call neu erstellt
3. **Konsistente Variablen**: Alle URL-Parameter werden sowohl für Session-Erstellung als auch Voice Calls verwendet

### Debugging-Tipps

1. **Vapi CLI für Call Logs**:
   ```bash
   vapi call list | head -10
   vapi call get <call-id> | grep -A50 "assistantOverrides"
   ```

2. **Browser Console**: Prüfen ob `window.VAPI_CONFIG` korrekt geladen ist
3. **Server Logs**: FastAPI logs zeigen, welche Variablen bei Session-Erstellung ankommen

### Offene Punkte
- Session-basierte Variablen (`vapi_session_id`) könnten für Multi-Channel-Support genutzt werden
- Die `/api/create-session` Route wird aktuell nicht für Voice Calls verwendet (nur für zukünftige Features)



