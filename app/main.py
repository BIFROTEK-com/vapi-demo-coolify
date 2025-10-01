from fastapi import FastAPI, Request, Form, Query, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import json
from datetime import datetime
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()

from .config import get_settings
from .services.color_extractor import extract_brand_colors
from .services.redis_service import redis_service
from .services.shlink_service import shlink_service, ShortUrlRequest, ShortUrlResponse


app = FastAPI(title="VAPI Web SDK Integration")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add caching headers for static files
@app.middleware("http")
async def add_cache_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Add cache headers for static files
    if request.url.path.startswith("/static/"):
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        response.headers["ETag"] = f'"{hash(request.url.path)}"'
    elif request.url.path.endswith((".js", ".css")):
        response.headers["Cache-Control"] = "public, max-age=86400"
    
    return response

# Optimize template rendering for production
templates = Jinja2Templates(
    directory="app/templates",
    auto_reload=False,  # Disable auto-reload in production
    autoescape=True,
    trim_blocks=True,
    lstrip_blocks=True
)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
# Mount React assets at /assets for the config page
app.mount("/assets", StaticFiles(directory="app/static/react-config/assets"), name="react-assets")

# Session mapping for Voice Call to Browser Session routing
browser_session_mapping = {}  # Maps browser_session_id to customer info
webhook_messages = {}  # Maps browser_session_id to list of webhook messages
active_connections = {}  # Maps browser_session_id to SSE connections

# Redis service for session management and cross-worker communication
# Will be initialized on startup

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize Redis connection on startup."""
    await redis_service.connect()
    if redis_service.is_connected():
        print("✅ Redis service initialized successfully")
    else:
        print("ℹ️ Redis service not available - using in-memory storage (single-worker only)")

@app.on_event("shutdown")
async def shutdown_event():
    """Close Redis connection on shutdown."""
    await redis_service.disconnect()
    print("✅ Redis service disconnected")

# Pydantic models for VAPI Chat API
class BrowserSessionRequest(BaseModel):
    browser_session_id: str
    customer_domain: str = None
    customer_name: str = None
    customer_email: str = None
    company_name: str = None

class ChatRequest(BaseModel):
    message: str
    assistant_id: str
    browser_session_id: str  # WICHTIG: Browser Session ID für Session-Routing!
    session_id: str | None = None
    previous_chat_id: str | None = None
    # Assistant override variables
    customer_domain: str | None = None
    customer_name: str | None = None
    customer_email: str | None = None
    company_name: str | None = None
    calendly_link: str | None = None
    # Voice transcript for context sync
    voice_transcript: str | None = None
    # Chat history for context sync
    chat_history: str | None = None
    # Conversation context from frontend
    conversation_context: str | None = None
    # Source for message type
    source: str | None = None


class ChatResponse(BaseModel):
    id: str
    output: list[dict]
    session_id: str | None = None


# VAPI Webhook Models
class VAPIWebhookEvent(BaseModel):
    """VAPI Webhook Event Model"""
    type: str
    call: dict | None = None
    message: dict | None = None
    functionCall: dict | None = None
    endOfCallReport: dict | None = None
    transcript: dict | None = None
    status: str | None = None
    timestamp: str | None = None


class WebhookResponse(BaseModel):
    """Webhook Response Model"""
    success: bool
    message: str
    data: dict | None = None



@app.post("/api/create-session")
async def create_vapi_session(
    customer_domain: str = None,
    customer_name: str = None,
    customer_email: str = None,
    company_name: str = None,
    calendly_link: str = None,
    chat_history: str = None,
    conversation_context: str = None
) -> dict:
    """Create a new VAPI session for voice/chat integration with assistant overrides."""
    try:
        # Get private API key from settings
        try:
            settings = get_settings()
            private_api_key = settings.vapi_private_key
            assistant_id = settings.assistant_id
        except Exception:
            private_api_key = os.getenv("VAPI_PRIVATE_KEY", "")
            assistant_id = os.getenv("ASSISTANT_ID", "")
        
        if not private_api_key or not assistant_id:
            raise HTTPException(
                status_code=500, 
                detail="VAPI credentials not configured on server"
            )
        
        # Prepare session creation with assistant overrides
        session_data = {"assistantId": assistant_id}
        
        # Add assistant overrides if provided
        if any([customer_domain, customer_name, customer_email, company_name, calendly_link, chat_history, conversation_context]):
            assistant_overrides = {}
            variable_values = {}
            
            if customer_domain:
                variable_values["customer_domain"] = customer_domain
            if customer_name:
                variable_values["customer_name"] = customer_name
            if customer_email:
                variable_values["customer_email"] = customer_email
            if company_name:
                variable_values["company_name"] = company_name
            if calendly_link:
                variable_values["calendly_link"] = calendly_link
            if chat_history:
                variable_values["chat_history"] = chat_history
            if conversation_context:
                variable_values["conversation_context"] = conversation_context
            
            if variable_values:
                assistant_overrides["variableValues"] = variable_values
                session_data["assistantOverrides"] = assistant_overrides
        
        # Create VAPI session
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.vapi.ai/session",
                headers={
                    "Authorization": f"Bearer {private_api_key}",
                    "Content-Type": "application/json"
                },
                json=session_data,
                timeout=30.0
            )
            
            if response.status_code not in [200, 201]:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"VAPI session creation failed: {response.text}"
                )
            
            session_response = response.json()
            
            # Log session creation details
            print(f"✅ VAPI session created: {session_response.get('id')}")
            print(f"📋 Session variables: {variable_values if 'variable_values' in locals() else 'None'}")
            
            return {
                "success": True,
                "sessionId": session_response.get("id"),
                "assistantId": session_response.get("assistantId"),
                "message": "VAPI session created successfully with assistant overrides",
                "variableValues": variable_values if 'variable_values' in locals() else {}
            }
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=408, detail="Session creation timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Session creation error: {str(e)}")


@app.post("/api/chat")
async def chat_with_vapi(chat_request: ChatRequest) -> dict:
    """
    Backend endpoint for VAPI Chat API.
    
    This endpoint uses the private VAPI API key to send chat messages
    and returns the assistant's response. This is required because
    the Chat API needs a private key which cannot be exposed in frontend code.
    """
    try:
        # Get private API key from settings
        try:
            settings = get_settings()
            private_api_key = settings.vapi_private_key
        except Exception:
            private_api_key = os.getenv("VAPI_PRIVATE_KEY", "")
        
        if not private_api_key:
            raise HTTPException(
                status_code=500, 
                detail="VAPI_PRIVATE_KEY not configured on server"
            )
        
        # Prepare request body for VAPI Chat API
        request_body = {
            "assistantId": chat_request.assistant_id,
            "input": chat_request.message
        }
        
        # Add session management - prioritize sessionId over previousChatId
        # WICHTIG: VAPI unterstützt assistantOverrides nicht bei Session-basierten Anfragen
        # Daher verwenden wir keine Sessions für Chat-Nachrichten mit assistantOverrides
        if chat_request.session_id:
            # Bei Session-basierten Anfragen können wir keine assistantOverrides verwenden
            # Daher ignorieren wir die Session-ID und verwenden assistantId + assistantOverrides
            print(f"⚠️ Session ID {chat_request.session_id} wird ignoriert, da assistantOverrides verwendet werden")
            # request_body["sessionId"] = chat_request.session_id
            # if "assistantId" in request_body:
            #     del request_body["assistantId"]
        elif chat_request.previous_chat_id:
            request_body["previousChatId"] = chat_request.previous_chat_id
        
        # Add assistant overrides with variable values and chat history
        assistant_overrides = {}
        variable_values = {}
        
        # Always add core customer data
        if chat_request.customer_domain:
            variable_values["customer_domain"] = chat_request.customer_domain
        if chat_request.customer_name:
            variable_values["customer_name"] = chat_request.customer_name
        if chat_request.customer_email:
            variable_values["customer_email"] = chat_request.customer_email
        if chat_request.company_name:
            variable_values["company_name"] = chat_request.company_name
        if chat_request.calendly_link:
            variable_values["calendly_link"] = chat_request.calendly_link
        if chat_request.voice_transcript:
            variable_values["voice_transcript"] = chat_request.voice_transcript
        
        # Add session context for voice/chat sync
        if chat_request.session_id:
            variable_values["vapi_session_id"] = chat_request.session_id
            # WICHTIG: current_browser_session muss die BROWSER Session ID sein, nicht die VAPI Session ID!
            variable_values["current_browser_session"] = chat_request.browser_session_id or "unknown"
        else:
            # Auch ohne session_id müssen wir current_browser_session setzen
            # VAPI braucht es für {{current_browser_session}} Ersetzung
            variable_values["current_browser_session"] = chat_request.browser_session_id or "unknown"
        
        # Add chat history if provided
        if hasattr(chat_request, 'chat_history') and chat_request.chat_history:
            variable_values["chat_history"] = chat_request.chat_history
        
        # Add conversation context if provided
        if chat_request.conversation_context:
            variable_values["conversation_context"] = chat_request.conversation_context
            print(f"📋 Chat API - conversation_context: {chat_request.conversation_context[:100]}...")
        
        # Always include assistant overrides if we have any variables
        if variable_values:
            assistant_overrides["variableValues"] = variable_values
            request_body["assistantOverrides"] = assistant_overrides
            print(f"✅ Chat API sending variableValues: {list(variable_values.keys())}")
        
        # Make request to VAPI Chat API
        print(f"🚀 Sending request to VAPI Chat API with timeout 300s...")
        print(f"📤 Request body: {request_body}")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.vapi.ai/chat",
                headers={
                    "Authorization": f"Bearer {private_api_key}",
                    "Content-Type": "application/json"
                },
                json=request_body,
                timeout=300.0  # 5 Minuten für Tool-Calls
            )
            
            if response.status_code not in [200, 201]:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"VAPI API error: {response.text}"
                )
            
            chat_response = response.json()
            
            # Extract message from VAPI response - handle different response structures
            message_content = ""
            if "output" in chat_response and chat_response["output"]:
                # New VAPI Chat API structure - find the last assistant message
                if isinstance(chat_response["output"], list) and len(chat_response["output"]) > 0:
                    # Look for the last assistant message in the output array
                    for output_item in reversed(chat_response["output"]):
                        if output_item.get("role") == "assistant" and output_item.get("content"):
                            message_content = output_item["content"]
                            break
                    # Fallback to first item if no assistant message found
                    if not message_content and len(chat_response["output"]) > 0:
                        message_content = chat_response["output"][0].get("content", "")
                elif isinstance(chat_response["output"], str):
                    message_content = chat_response["output"]
            elif "message" in chat_response:
                # Alternative structure
                message_content = chat_response["message"]
            elif "content" in chat_response:
                # Direct content
                message_content = chat_response["content"]
            
            print(f"📝 Extracted message content: '{message_content}'")
            
            return {
                "success": True,
                "id": chat_response.get("id"),
                "message": message_content,
                "session_id": chat_response.get("sessionId"),
                "raw_response": chat_response
            }
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=408, detail="Request timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@app.post("/api/register-browser-session")
async def register_browser_session(request: BrowserSessionRequest) -> dict:
    """Register a browser session for webhook routing."""
    try:
        session_data = {
            "customer_domain": request.customer_domain,
            "customer_name": request.customer_name,
            "customer_email": request.customer_email,
            "company_name": request.company_name,
            "created_at": datetime.now().isoformat()
        }
        
        # Store in both Redis AND in-memory for debug visibility
        browser_session_mapping[request.browser_session_id] = session_data
        
        if redis_service.is_connected():
            await redis_service.store_session(request.browser_session_id, session_data)
        
        return {
            "success": True,
            "message": "Browser session registered successfully",
            "browser_session_id": request.browser_session_id
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to register browser session: {str(e)}"
        }

@app.get("/api/message-stream/{browser_session_id}")
async def message_stream(browser_session_id: str):
    """Server-Sent Events stream for webhook messages."""
    from fastapi.responses import StreamingResponse
    import asyncio
    import json
    
    async def event_generator():
        # Store connection for this session
        active_connections[browser_session_id] = True
        
        heartbeat_counter = 0
        try:
            while True:
                # Send queued messages for this session
                messages = []
                if redis_service.is_connected():
                    # Get messages from Redis (using session_messages instead of webhook_messages)
                    messages = await redis_service.get_session_messages(browser_session_id)
                # Messages will be cleared after successful SSE send (see below)
                else:
                    # Fallback to in-memory storage
                    if browser_session_id in webhook_messages and webhook_messages[browser_session_id]:
                        messages = webhook_messages[browser_session_id].copy()
                        webhook_messages[browser_session_id] = []
                
                for message in messages:
                    yield f"data: {json.dumps(message)}\n\n"
                    print(f"📧 SSE: Sent message to {browser_session_id}: {message.get('content', 'N/A')}")
                    
                # Only delete messages if they were actually sent via SSE
                if messages and redis_service.is_connected():
                    await redis_service.redis_client.delete(f"session_messages:{browser_session_id}")
                    print(f"🗑️ SSE: Cleared {len(messages)} messages after successful send")

                # Heartbeat every 15 seconds to keep proxies from buffering/closing
                heartbeat_counter += 1
                if heartbeat_counter >= 15:
                    # Comment line per SSE spec (ignored by clients), helps flush buffers
                    yield ": keep-alive\n\n"
                    heartbeat_counter = 0

                await asyncio.sleep(1)
        except asyncio.CancelledError:
            if browser_session_id in active_connections:
                del active_connections[browser_session_id]
            raise
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
            # Disable proxy buffering on Nginx-like proxies to allow streaming
            "X-Accel-Buffering": "no"
        }
    )


@app.post("/webhook/vapi/send-message")
async def vapi_send_message_webhook(request: Request):
    """
    ⭐ EINZIGER WEG: VAPI Tool-Call → Redis → Frontend
    
    Versteht VAPI-Tool-Call-Format und antwortet korrekt
    """
    try:
        # Raw request body lesen (VAPI-Tool-Call-Format)
        body = await request.body()
        webhook_data = json.loads(body)
        
        print(f"\n{'='*60}")
        print(f"📨 VAPI TOOL-CALL: {webhook_data}")
        print(f"{'='*60}")
        
        # Parse Tool-Call aus VAPI-Format
        message_obj = webhook_data.get("message") if isinstance(webhook_data.get("message"), dict) else None
        tool_calls_list = message_obj.get("toolCalls") if message_obj else []
        
        if not tool_calls_list:
            return {"error": "No tool calls found"}
        
        # Ersten Tool-Call nehmen
        tool_call = tool_calls_list[0]
        tool_call_id = tool_call.get("id", "unknown")
        function_data = tool_call.get("function", {})
        function_name = function_data.get("name", "")
        parameters = function_data.get("arguments", {})
        
        # Arguments als JSON-String → parsen
        if isinstance(parameters, str):
            try:
                parameters = json.loads(parameters)
            except Exception:
                pass
        
        print(f"🔧 Function: {function_name}")
        print(f"🆔 Tool Call ID: {tool_call_id}")
        print(f"📋 Parameters: {parameters}")
        
        # Nur send_chat_message Tool verarbeiten
        if function_name != "send_chat_message":
            return {"error": f"Unknown function: {function_name}"}
        
        # Parameter extrahieren
        message_content = parameters.get("message", "")
        session_id = parameters.get("session_id", "")
        
        if not session_id or not message_content:
            return {"error": "Missing session_id or message"}
        
        # Message-Data für Redis
        message_data = {
            "content": message_content,
            "role": "assistant", 
            "timestamp": datetime.now().isoformat(),
            "source": "vapi-tool",
            "icon": "📧"
        }
        
        # NUR Redis - kein In-Memory Fallback
        if not redis_service.is_connected():
            return {"error": "Redis not connected"}
        
        await redis_service.add_message_to_session(session_id, message_data)
        print(f"📧 VAPI → Redis → Session: {session_id}")
        
        # VAPI-Tool-Call-Response (WICHTIG!)
        from fastapi.responses import JSONResponse
        response_data = {
            "results": [
                {
                    "toolCallId": tool_call_id,
                    "result": f"Message '{message_content}' sent to session {session_id}"
                }
            ]
        }
        
        print(f"📤 VAPI RESPONSE: {response_data}")
        print(f"{'='*60}\n")
        
        return JSONResponse(content=response_data)
    
    except Exception as e:
        print(f"❌ VAPI Tool-Call Error: {e}")
        return {"error": str(e)}

@app.post("/webhook/vapi/send-message", response_model=WebhookResponse)
async def vapi_send_message_webhook(request: Request) -> WebhookResponse:
    """
    Spezieller Webhook für VAPI Tool-Calls und send() Nachrichten.
    
    Empfängt Tool-Calls vom VAPI Assistant und verarbeitet sie,
    umgeht den Transcriber für saubere Links und Formatierung.
    
    WICHTIG: Unterstützt Session-Identifikation für Multi-User-Szenarien.
    """
    try:
        # Raw request body lesen
        body = await request.body()
        webhook_data = json.loads(body)
        
        print(f"\n{'='*80}")
        print(f"📨 VAPI WEBHOOK RECEIVED: {webhook_data}")
        print(f"{'='*80}")
        
        # Event-Type identifizieren
        event_type = webhook_data.get("type", "unknown")
        print(f"🎯 Event type: {event_type}")
        
        # Session-ID aus verschiedenen Quellen extrahieren
        session_id = None
        if "sessionId" in webhook_data:
            session_id = webhook_data["sessionId"]
        elif "call" in webhook_data and "sessionId" in webhook_data["call"]:
            session_id = webhook_data["call"]["sessionId"]
        
        print(f"🔍 Session ID detected: {session_id}")
        
        # Parse message object once
        message_obj = webhook_data.get("message") if isinstance(webhook_data.get("message"), dict) else None
        
        # Tool-Call Details extrahieren
        function_call = None
        if "functionCall" in webhook_data:
            function_call = webhook_data["functionCall"]
        elif message_obj and "functionCall" in message_obj:
            function_call = message_obj["functionCall"]
            
        # Prüfe ob es ein Tool-Call ist (VAPI sendet message.toolCalls[])
        is_tool_call = False
        tool_calls_list = message_obj.get("toolCalls") if message_obj else None
        
        if function_call:
            is_tool_call = True
            print("🔧 TOOL CALL DETECTED (old format)!")
        elif isinstance(tool_calls_list, list) and len(tool_calls_list) > 0:
            is_tool_call = True
            print("🔧 TOOL CALL DETECTED (message.toolCalls present)!")
        elif message_obj and message_obj.get("type") == "tool-calls":
            # Some events include type but empty toolCalls; still treat as tool-call wrapper
            is_tool_call = True
            print("🔧 TOOL CALL DETECTED (type == 'tool-calls')!")
        else:
            print("❌ NO TOOL CALL DETECTED")
            print(f"   Message type: {message_obj.get('type', 'N/A') if message_obj else 'N/A'}")
            print(f"   Has toolCalls key: {('toolCalls' in message_obj) if message_obj else False}")
        
        if is_tool_call:
            # Handle both formats: functionCall (old) and message.toolCalls[] (new VAPI format)
            if "functionCall" in webhook_data:
                function_call = webhook_data["functionCall"]
                function_name = function_call.get("name", "")
                parameters = function_call.get("parameters", {})
                tool_call_id = function_call.get("id", "unknown")
            else:
                # VAPI new format: message.toolCalls[]
                tool_calls = message_obj.get("toolCalls", []) if message_obj else []
                if tool_calls:
                    function_call = tool_calls[0]  # Take first tool call
                    function_name = function_call.get("function", {}).get("name", "")
                    parameters = function_call.get("function", {}).get("arguments", {})
                    # arguments may be a JSON string → parse if needed
                    if isinstance(parameters, str):
                        try:
                            parameters = json.loads(parameters)
                        except Exception:
                            pass
                    tool_call_id = function_call.get("id", "unknown")
                else:
                    print("❌ No tool calls found in message.toolCalls")
                    return WebhookResponse(success=False, message="No tool calls found")
            
            print(f"🔧 Tool-Call: {function_name} with params: {parameters}")
            print(f"🆔 Tool Call ID: {tool_call_id}")
            
            # Verarbeite send_chat_message Tool-Call
            if function_name == "send_chat_message":
                message_content = parameters.get("message", "")
                message_role = parameters.get("role", "assistant")
                tool_session_id = parameters.get("session_id", "")
                
                # VAPI ersetzt {{current_browser_session}} automatisch
                # Wir müssen nur die echte Session-ID übergeben
                
                print(f"💬 Tool-Call message: {message_content}")
                print(f"👤 Role: {message_role}")
                print(f"🆔 Tool Session ID: {tool_session_id}")
                print(f"🆔 Webhook Session ID: {session_id}")
                
                # Verwende die Session-ID aus dem Tool-Call (prioritär) oder aus dem Webhook
                final_session_id = tool_session_id or session_id
                
                if not final_session_id:
                    print("⚠️ WARNING: No session ID found - message cannot be routed to specific chat!")
                    return WebhookResponse(
                        success=False,
                        message="No session ID provided - cannot route message to specific chat",
                        data={"error": "missing_session_id"}
                    )
                
                # Session-basierte Nachrichten-Routing implementieren
                print(f"🔄 Routing message to session: {final_session_id}")
                
                # Look up session info - check both in-memory and Redis
                session_info = browser_session_mapping.get(final_session_id)
                if session_info:
                    print(f"✅ Session found in memory: {session_info}")
                elif redis_service.is_connected():
                    # Fallback: Look in Redis for cross-worker compatibility
                    session_info = await redis_service.get_session(final_session_id)
                    if session_info:
                        print(f"✅ Session found in Redis: {session_info}")
                        # Cache in memory for future requests in this worker
                        browser_session_mapping[final_session_id] = session_info
                    else:
                        print(f"⚠️ Session not found in Redis either: {final_session_id}")
                else:
                    print(f"⚠️ Session not found in memory and Redis not available: {final_session_id}")
                
                # Store webhook message for frontend streaming
                message_data = {
                    "content": message_content,
                    "role": message_role,
                    "timestamp": datetime.now().isoformat(),
                    "source": "voice-function"
                }
                
                # Store message in Redis if available, fallback to in-memory
                try:
                    if redis_service.is_connected():
                        await redis_service.add_message_to_session(final_session_id, message_data)
                        print(f"📧 Message stored in Redis for session: {final_session_id}")
                    else:
                        if final_session_id not in webhook_messages:
                            webhook_messages[final_session_id] = []
                        webhook_messages[final_session_id].append(message_data)
                        print(f"📧 Message stored in memory for session: {final_session_id}")
                except Exception as e:
                    print(f"❌ Storage error: {e}")
                    # Fallback to in-memory
                    if final_session_id not in webhook_messages:
                        webhook_messages[final_session_id] = []
                    webhook_messages[final_session_id].append(message_data)
                
                print(f"📧 Webhook message stored for frontend streaming")
                
                # VAPI erwartet spezifisches Response-Format für Tool-Calls
                # tool_call_id ist bereits oben extrahiert
                response_data = {
                    "results": [
                        {
                            "toolCallId": tool_call_id,
                            "result": f"Message '{message_content}' successfully routed to session {final_session_id}"
                        }
                    ]
                }
                
                print(f"📤 WEBHOOK RESPONSE:")
                print(f"   🆔 Tool Call ID: {tool_call_id}")
                print(f"   📝 Result: Message successfully routed to session {final_session_id}")
                print(f"   📋 Full Response: {response_data}")
                print(f"{'='*80}\n")
                
                from fastapi.responses import JSONResponse
                return JSONResponse(response_data)
            else:
                print(f"❓ Unknown tool call: {function_name}")
                # tool_call_id ist bereits oben extrahiert
                from fastapi.responses import JSONResponse
                return JSONResponse({
                    "results": [
                        {
                            "toolCallId": tool_call_id,
                            "result": f"Unknown tool call '{function_name}' received"
                        }
                    ]
                })
        
        # Fallback für normale send() Nachrichten
        elif "message" in webhook_data:
            if isinstance(webhook_data["message"], dict):
                message_content = webhook_data["message"].get("content", "")
                message_role = webhook_data["message"].get("role", "assistant")
            else:
                message_content = str(webhook_data["message"])
                message_role = "assistant"
            
            print(f"💬 Direct message: {message_content}")
            print(f"👤 Role: {message_role}")
            
            # Broadcast to all active sessions if no specific session ID
            if message_content:  # Only send if message is not empty
                print(f"📡 Broadcasting message to all active sessions")
                message_data = {
                    "content": message_content,
                    "role": message_role,
                    "timestamp": datetime.now().isoformat(),
                    "source": "voice-function"
                }
                
                # Store in Redis for each active session
                try:
                    for session_id in browser_session_mapping.keys():
                        # Store message in Redis array for this session
                        await redis_service.add_message_to_session(session_id, message_data)
                        print(f"📧 Message stored in Redis for session: {session_id}")
                except Exception as e:
                    print(f"❌ Redis storage error: {e}")
                    # Fallback to in-memory storage
                    for session_id in browser_session_mapping.keys():
                        if session_id not in webhook_messages:
                            webhook_messages[session_id] = []
                        webhook_messages[session_id].append(message_data)
                        print(f"📧 Message stored in memory for session: {session_id}")
            
            # Für normale Nachrichten (nicht Tool-Calls) verwenden wir das Standard-Format
            return WebhookResponse(
                success=True,
                message="Direct message processed and broadcasted to all sessions",
                data={
                    "message_content": message_content,
                    "message_role": message_role,
                    "broadcasted_to": len(browser_session_mapping),
                    "raw_data": webhook_data
                }
            )
        
        else:
            print(f"❓ Unknown webhook data format: {webhook_data}")
            return WebhookResponse(
                success=True,
                message="Unknown webhook format received",
                data={"raw_data": webhook_data}
            )
        
    except Exception as e:
        print(f"❌ Webhook processing error: {str(e)}")
        return WebhookResponse(
            success=False,
            message=f"Webhook processing failed: {str(e)}",
            data={"error": str(e)}
        )


@app.post("/webhook/vapi-OLD-DISABLED")
async def vapi_webhook_OLD_DISABLED(request: Request):
    """
    VAPI Webhook Endpoint für Echtzeit-Events.
    
    Empfängt Events von VAPI wie:
    - call-start: Call gestartet
    - call-end: Call beendet
    - message: Neue Nachricht
    - function-call: Function Call ausgeführt
    - end-of-call-report: Call Report
    - transcript: Transcript Update
    """
    try:
        # Parse the request body manually
        webhook_data = await request.json()
        webhook_event_type = webhook_data.get("type", "unknown")
        
        print(f"🔔 VAPI WEBHOOK INCOMING: {webhook_event_type}")
        
        # Handle different event types
        if webhook_event_type == "call-start":
            print("📞 Call started")
            # Hier können Sie Call-Start-Logik implementieren
            # z.B. Datenbank-Eintrag, Analytics, etc.
            
        elif webhook_event_type == "call-end":
            print("📞 Call ended")
            # Hier können Sie Call-End-Logik implementieren
            # z.B. Call-Report speichern, Analytics, etc.
            
        elif webhook_event_type == "message":
            print(f"💬 Message received: {webhook_data.get('message')}")
            # Hier können Sie Message-Logik implementieren
            # z.B. Nachricht in Datenbank speichern, etc.
            
        elif webhook_event_type == "function-call":
            function_call_data = webhook_data.get("functionCall", {})
            print(f"🔧 Function call: {function_call_data}")
            
            # Handle send_chat_message function calls
            if function_call_data and function_call_data.get("name") == "send_chat_message":
                parameters = function_call_data.get("parameters", {})
                message_content = parameters.get("message", "")
                message_role = parameters.get("role", "assistant")
                tool_session_id = parameters.get("session_id", "")
                tool_call_id = function_call_data.get("id", "NO_ID_PROVIDED")
                
                print(f"💬 Tool-Call message: {message_content}")
                print(f"👤 Role: {message_role}")
                print(f"🆔 Tool Session ID: {tool_session_id}")
                print(f"🆔 Tool Call ID: {tool_call_id}")
                
                if tool_session_id and message_content:
                    # Store webhook message for frontend streaming
                    message_data = {
                        "content": message_content,
                        "role": message_role,
                        "timestamp": datetime.now().isoformat(),
                        "source": "voice-function"
                    }
                    
                    # Store message in BOTH Redis AND in-memory for debug visibility
                    if tool_session_id not in webhook_messages:
                        webhook_messages[tool_session_id] = []
                    webhook_messages[tool_session_id].append(message_data)
                    print(f"📧 Webhook message stored in memory for session: {tool_session_id}")
                    
                    if redis_service.is_connected():
                        await redis_service.store_webhook_message(tool_session_id, message_data)
                        print(f"📧 Webhook message stored in Redis for session: {tool_session_id}")
                    
                    # VAPI erwartet direkt das results Array, nicht in WebhookResponse verpackt
                    from fastapi.responses import JSONResponse
                    response_data = {
                        "results": [
                            {
                                "toolCallId": tool_call_id,
                                "result": f"Message '{message_content}' successfully routed to session {tool_session_id}"
                            }
                        ]
                    }
                    print(f"📤 VAPI WEBHOOK OUTGOING: Function call success")
                    return JSONResponse(content=response_data)
                else:
                    print("⚠️ WARNING: Missing session_id or message content in send_chat_message call")
                    return WebhookResponse(
                        success=False,
                        message="Missing session_id or message content",
                        data={"error": "missing_parameters"}
                    )
            
            # Hier können Sie weitere Function-Call-Logik implementieren
            # z.B. Custom Functions ausführen, etc.
            
        elif webhook_event_type == "end-of-call-report":
            print(f"📊 End of call report: {webhook_data.get('endOfCallReport')}")
            # Hier können Sie Call-Report-Logik implementieren
            # z.B. Report in Datenbank speichern, Analytics, etc.
            
        elif webhook_event_type == "transcript":
            print(f"📝 Transcript update: {webhook_data.get('transcript')}")
            # Hier können Sie Transcript-Logik implementieren
            # z.B. Transcript in Datenbank speichern, etc.
            
        else:
            print(f"❓ Unknown event type: {webhook_event_type}")
        
        response_data = WebhookResponse(
            success=True,
            message=f"Webhook event '{webhook_event_type}' processed successfully",
            data={"event_type": webhook_event_type, "timestamp": webhook_data.get("timestamp")}
        )
        print(f"📤 VAPI WEBHOOK OUTGOING: Default response")
        return response_data
        
    except Exception as e:
        print(f"❌ Webhook processing error: {str(e)}")
        return WebhookResponse(
            success=False,
            message=f"Webhook processing failed: {str(e)}",
            data={"error": str(e)}
        )


# Old redirect route removed - now using React Landing Page as main route


@app.get("/webapp", response_class=HTMLResponse)
def public_webapp(
    request: Request,
    customer_domain: str = Query(default="", description="Customer domain"),
    customer_name: str = Query(default="", description="Customer name"),
    customer_email: str = Query(default="", description="Customer email"),
    company_name: str = Query(default="", description="Company name"),
    whatsapp_phone: str = Query(default="", description="WhatsApp phone number"),
) -> HTMLResponse:
    """Personalized Landing Page for cold mail end customers."""
    
    # Parameter-Validierung - Blockiere wenn wichtige Parameter fehlen
    required_params = {
        "customer_domain": customer_domain,
        "customer_name": customer_name,
        "customer_email": customer_email
    }
    
    missing_params = [param for param, value in required_params.items() if not value or value.strip() == ""]
    
    if missing_params:
        # Zeige Fehlerseite mit fehlenden Parametern
        return templates.TemplateResponse("error_missing_params.html", {
            "request": request,
            "missing_params": missing_params,
            "required_params": required_params,
            "current_url": str(request.url)
        })
    # Load VAPI credentials and config - Always read from .env file directly for real-time updates
    assistant_id = ""
    public_key = ""
    calendly_link = ""
    
    # Load SAAS-Agentur config values
    saas_company_name = ""
    saas_logo_url = ""
    saas_website_url = ""
    support_email = ""
    impressum_url = ""
    privacy_url = ""
    terms_url = ""
    
    # Always read from .env file directly to get real-time updates
    import os
    from pathlib import Path
    
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('ASSISTANT_ID='):
                    assistant_id = line.split('=', 1)[1]
                elif line.startswith('PUBLIC_KEY='):
                    public_key = line.split('=', 1)[1]
                elif line.startswith('CALENDLY_LINK='):
                    calendly_link = line.split('=', 1)[1]
                elif line.startswith('COMPANY_NAME='):
                    saas_company_name = line.split('=', 1)[1]
                elif line.startswith('LOGO_URL='):
                    saas_logo_url = line.split('=', 1)[1]
                elif line.startswith('WEBSITE_URL='):
                    saas_website_url = line.split('=', 1)[1]
                elif line.startswith('SUPPORT_EMAIL='):
                    support_email = line.split('=', 1)[1]
                elif line.startswith('IMPRESSUM_URL='):
                    impressum_url = line.split('=', 1)[1]
                elif line.startswith('PRIVACY_POLICY_URL='):
                    privacy_url = line.split('=', 1)[1]
                elif line.startswith('TERMS_URL='):
                    terms_url = line.split('=', 1)[1]
    
    # Extract company name from domain for personalization
    if customer_domain:
        clean_domain = customer_domain.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
        if not company_name:  # Only extract from domain if company_name not provided
            company_name = clean_domain.replace('.com', '').replace('.de', '').replace('.org', '').replace('.net', '')
            company_name = company_name.replace('-', ' ').replace('_', ' ').title()
    else:
        clean_domain = ""
        if not company_name:  # Default company name when no domain and no company_name
            company_name = "VAPI"
    
    # Extract brand colors from domain if provided
    primary_color = "#4361ee"    # Default blue
    secondary_color = "#3a0ca3"  # Default dark blue  
    accent_color = "#4cc9f0"     # Default light blue
    
    if customer_domain and clean_domain:
        try:
            # Extract brand colors using the color extractor service
            extracted_primary, extracted_secondary, extracted_accent = extract_brand_colors(clean_domain)
            primary_color = extracted_primary
            secondary_color = extracted_secondary
            accent_color = extracted_accent
            print(f"✅ Brand colors extracted for {clean_domain}: {primary_color}, {secondary_color}, {accent_color}")
        except Exception as e:
            print(f"⚠️ Color extraction failed for {clean_domain}: {e}, using defaults")
            # Keep default colors

    # Generate multiple logo URLs with fallbacks (only if domain is provided)
    # Clearbit has priority 1 for high-quality logos
    logo_urls = []
    if customer_domain and clean_domain:
        logo_urls = [
            f"https://logo.clearbit.com/{clean_domain}",  # Priority 1: Clearbit (best quality)
            f"https://logo.clearbit.com/{clean_domain}?size=200",  # Priority 2: Clearbit large
            f"https://{clean_domain}/favicon.ico",  # Priority 3: Official favicon
            f"https://www.google.com/s2/favicons?domain={clean_domain}&sz=128",  # Priority 4: Google
            f"https://icons.duckduckgo.com/ip3/{clean_domain}.ico"  # Priority 5: DuckDuckGo fallback
        ]
    
    # Personalized configuration based on parameters
    demo_agent_title = f"{company_name} KI-Assistent"
    
    # Create personalized messages
    if customer_name and company_name:
        welcome_message = f"Willkommen {customer_name}! Wir haben einen KI-Agenten für Sie zum Ausprobieren erstellt. Stellen Sie dem KI-Assistenten Fragen über {company_name}."
        first_message = f"Hallo {customer_name}! Ich bin der KI-Assistent von {company_name} und helfe Ihnen gerne bei allen Fragen. Wie kann ich Ihnen behilflich sein?"
        hero_title = f"Hallo {customer_name}!"
        hero_subtitle = f"Ihr persönlicher KI-Assistent für {company_name}"
    elif customer_name:
        welcome_message = f"Willkommen {customer_name}! Wir haben einen KI-Agenten für Sie zum Ausprobieren erstellt. Stellen Sie dem KI-Assistenten Ihre Fragen."
        first_message = f"Hallo {customer_name}! Ich bin Ihr KI-Assistent. Wie kann ich Ihnen helfen?"
        hero_title = f"Hallo {customer_name}!"
        hero_subtitle = "Ihr persönlicher KI-Assistent"
    elif company_name:
        welcome_message = f"Willkommen! Wir haben einen KI-Agenten für Sie zum Ausprobieren erstellt. Stellen Sie dem KI-Assistenten Fragen über {company_name}."
        first_message = f"Hallo! Ich bin der KI-Assistent von {company_name}. Wie kann ich Ihnen helfen?"
        hero_title = f"Willkommen bei {company_name}"
        hero_subtitle = "Ihr KI-Assistent"
    else:
        welcome_message = "Willkommen! Wir haben einen KI-Agenten für Sie zum Ausprobieren erstellt. Stellen Sie dem KI-Assistenten Ihre Fragen."
        first_message = "Hallo! Ich bin Ihr KI-Assistent. Wie kann ich Ihnen helfen?"
        hero_title = "Willkommen"
        hero_subtitle = "Ihr KI-Assistent"
    
    config = {
        "customer_name": customer_name or "",
        "customer_email": customer_email,
        "customer_domain": clean_domain,
        "company_name": company_name,
        "demo_agent_title": demo_agent_title,
        "logo_url": logo_urls[0] if logo_urls else "",  # Primary logo URL
        "logo_urls": logo_urls,    # All fallback URLs
        "website_url": f"https://{clean_domain}" if clean_domain else "",
        "whatsapp_phone": whatsapp_phone,
        "calendly_link": calendly_link,
        "welcome_message": welcome_message,
        "hero_title": hero_title,
        "hero_subtitle": hero_subtitle,
        "primary_color": primary_color,
        "secondary_color": secondary_color,
        "accent_color": accent_color,
        "first_message": first_message,
        # SAAS Agency data from config
        "saas_company_name": saas_company_name,
        "saas_logo_url": saas_logo_url,
        "saas_website_url": saas_website_url,
        "support_email": support_email,
        "impressum_url": impressum_url,
        "privacy_url": privacy_url,
        "terms_url": terms_url
    }
    
    return templates.TemplateResponse(
        "public_webapp.html",
        {
            "request": request,
            "assistant_id": assistant_id,
            "public_key": public_key,
            **config
        },
    )


# Main Landing Page (React)
@app.get("/", response_class=HTMLResponse)
def landing_page(
    request: Request,
    customer_domain: str = Query(default="", description="Customer domain"),
    customer_name: str = Query(default="", description="Customer name"),
    customer_email: str = Query(default="", description="Customer email"),
    company_name: str = Query(default="", description="Company name"),
) -> HTMLResponse:
    """Landing page - redirects to webapp with parameters."""
    # Redirect to webapp with all parameters
    from urllib.parse import urlencode
    params = {}
    if customer_domain:
        params["customer_domain"] = customer_domain
    if customer_name:
        params["customer_name"] = customer_name
    if customer_email:
        params["customer_email"] = customer_email
    if company_name:
        params["company_name"] = company_name
    
    query_string = urlencode(params)
    redirect_url = f"/webapp?{query_string}" if query_string else "/webapp"
    return RedirectResponse(url=redirect_url)


# SaaS Admin Routes
@app.get("/config", response_class=HTMLResponse)
def config_page(request: Request) -> HTMLResponse:
    """Password-protected configuration page - shows login form."""
    import os
    
    # Get password from environment
    config_password = os.getenv("CONFIG_PASSWORD", "")
    if not config_password:
        return HTMLResponse(
            content="""
            <html>
                <head><title>Config Error</title></head>
                <body style="font-family: Arial, sans-serif; padding: 40px; text-align: center;">
                    <h1>❌ Configuration Error</h1>
                    <p>CONFIG_PASSWORD not set in environment variables.</p>
                    <a href="/webapp" style="color: blue;">← Back to WebApp</a>
                </body>
            </html>
            """,
            status_code=500
        )
    
    # Show password form (no password check in GET)
    return HTMLResponse(
        content=f"""
        <html>
            <head>
                <title>Config Access</title>
                <style>
                    body {{ font-family: Arial, sans-serif; padding: 40px; text-align: center; background: #f5f5f5; }}
                    .container {{ max-width: 400px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    input {{ width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }}
                    button {{ width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }}
                    button:hover {{ background: #0056b3; }}
                    .error {{ color: red; margin-top: 10px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🔐 Config Access</h1>
                    <p>Enter password to access configuration:</p>
                    <form method="post" action="/config">
                        <input type="password" name="password" placeholder="Enter password" required>
                        <button type="submit">Access Config</button>
                    </form>
                    <a href="/webapp" style="color: #666; text-decoration: none;">← Back to WebApp</a>
                </div>
            </body>
        </html>
        """,
        status_code=200
    )

@app.post("/config", response_class=HTMLResponse)
def config_page_post(password: str = Form(...)) -> HTMLResponse:
    """Handle password authentication for config page."""
    import os
    
    # Get password from environment
    config_password = os.getenv("CONFIG_PASSWORD", "")
    if not config_password:
        return HTMLResponse(
            content="""
            <html>
                <head><title>Config Error</title></head>
                <body style="font-family: Arial, sans-serif; padding: 40px; text-align: center;">
                    <h1>❌ Configuration Error</h1>
                    <p>CONFIG_PASSWORD not set in environment variables.</p>
                    <a href="/webapp" style="color: blue;">← Back to WebApp</a>
                </body>
            </html>
            """,
            status_code=500
        )
    
    # Check password
    if not password or password != config_password:
        return HTMLResponse(
            content=f"""
            <html>
                <head>
                    <title>Config Access</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; padding: 40px; text-align: center; background: #f5f5f5; }}
                        .container {{ max-width: 400px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                        input {{ width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }}
                        button {{ width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }}
                        button:hover {{ background: #0056b3; }}
                        .error {{ color: red; margin-top: 10px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>🔐 Config Access</h1>
                        <p style="color: red;">❌ Invalid password. Please try again.</p>
                        <form method="post" action="/config">
                            <input type="password" name="password" placeholder="Enter password" required>
                            <button type="submit">Access Config</button>
                        </form>
                        <a href="/webapp" style="color: #666; text-decoration: none;">← Back to WebApp</a>
                    </div>
                </body>
            </html>
            """,
            status_code=401
        )
    
    # Password correct - serve React config page
    from pathlib import Path
    
    # Check if React build exists
    react_build_path = Path("app/static/react-config/index.html")
    if react_build_path.exists():
        # Load current config to build preview URL
        config = get_env_config_internal()
        
        # Build preview URL with all parameters
        # Start with required parameters for /webapp route
        preview_url = "/webapp"
        
        # Use analyzedDomain if available, otherwise create domain from companyName
        domain = config.get('analyzedDomain', '')
        if not domain and config.get('companyName'):
            # Create domain from company name (lowercase, no spaces, add .com)
            domain = config.get('companyName', '').lower().replace(' ', '').replace('-', '') + '.com'
        elif not domain:
            domain = 'example.com'
            
        preview_url += f"?customer_domain={domain}"
        preview_url += f"&customer_name={config.get('companyName', 'Demo User')}"
        preview_url += f"&customer_email=demo@{domain}"
        
        # Add optional parameters
        if config.get('companyName'):
            preview_url += f"&company_name={config.get('companyName', '')}"
        if config.get('whatsappPhone'):
            preview_url += f"&whatsapp_phone={config.get('whatsappPhone', '')}"
        if config.get('logoUrl'):
            preview_url += f"&logo_url={config.get('logoUrl', '')}"
        if config.get('primaryColor'):
            preview_url += f"&primary_color={config.get('primaryColor', '')}"
        if config.get('secondaryColor'):
            preview_url += f"&secondary_color={config.get('secondaryColor', '')}"
        if config.get('accentColor'):
            preview_url += f"&accent_color={config.get('accentColor', '')}"
        if config.get('calendlyLink'):
            preview_url += f"&calendly_link={config.get('calendlyLink', '')}"
        if config.get('facebookBusinessWhatsApp'):
            preview_url += f"&facebook_whatsapp={config.get('facebookBusinessWhatsApp', '')}"
        
        # Add SAAS agency data
        if config.get('saasCompanyName'):
            preview_url += f"&saas_company_name={config.get('saasCompanyName', '')}"
        if config.get('saasLogoUrl'):
            preview_url += f"&saas_logo_url={config.get('saasLogoUrl', '')}"
        if config.get('saasWebsiteUrl'):
            preview_url += f"&saas_website_url={config.get('saasWebsiteUrl', '')}"
        if config.get('impressumUrl'):
            preview_url += f"&impressum_url={config.get('impressumUrl', '')}"
        if config.get('privacyPolicyUrl'):
            preview_url += f"&privacy_url={config.get('privacyPolicyUrl', '')}"
        if config.get('termsUrl'):
            preview_url += f"&terms_url={config.get('termsUrl', '')}"
        
        # Read the React HTML file
        html_content = react_build_path.read_text()
        
        # Add preview button
        preview_button = f'''
        <div style="position: fixed; top: 20px; right: 20px; z-index: 1000;">
            <a href="{preview_url}" 
               style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                      color: white; 
                      padding: 12px 24px; 
                      border-radius: 8px; 
                      text-decoration: none; 
                      font-weight: 600; 
                      box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                      transition: all 0.3s ease;
                      display: inline-block;">
                🚀 Preview Demo
            </a>
        </div>
        '''
        
        # Inject the preview button before the closing body tag
        html_content = html_content.replace('</body>', f'{preview_button}</body>')
        
        return HTMLResponse(content=html_content, status_code=200)
    else:
        # Fallback to development message
        return HTMLResponse(
            content="""
            <html>
                <head><title>React Config - Development</title></head>
                <body style="font-family: Arial, sans-serif; padding: 40px; text-align: center;">
                    <h1>🚀 React Config Page</h1>
                    <p>The React configuration page is in development mode.</p>
                    <p>Run <code>cd frontend && npm run dev</code> to start the development server.</p>
                    <p>Then visit <a href="http://localhost:3000">http://localhost:3000</a></p>
                    <br>
                    <a href="/webapp" style="color: blue;">← Back to WebApp</a>
                </body>
            </html>
            """,
            status_code=200
        )





@app.post("/api/secure-config")
def get_secure_config(password: str = Form(...)) -> dict:
    """Get configuration values with password protection via POST."""
    import os
    
    # Get password from environment
    config_password = os.getenv("CONFIG_PASSWORD", "")
    if not config_password:
        raise HTTPException(status_code=500, detail="CONFIG_PASSWORD not configured")
    
    # Check password
    if password != config_password:
        raise HTTPException(status_code=401, detail="Invalid password")
    
    # Return config (same logic as before)
    return get_env_config_internal()

def get_env_config_internal() -> dict:
    """Internal function to get configuration values from .env file."""
    assistant_id = ""
    public_key = ""
    private_key = ""
    
    try:
        settings = get_settings()
        assistant_id = settings.assistant_id
        public_key = settings.public_key
        private_key = settings.vapi_private_key
    except Exception:
        # If settings can't be loaded, try to read from .env file directly
        import os
        from pathlib import Path
        
        env_file = Path(".env")
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('ASSISTANT_ID='):
                        assistant_id = line.split('=', 1)[1]
                    elif line.startswith('PUBLIC_KEY='):
                        public_key = line.split('=', 1)[1]
                    elif line.startswith('VAPI_PRIVATE_KEY='):
                        private_key = line.split('=', 1)[1]
    
    # Also load manual inputs and domain analysis
    facebook_business_whatsapp = ""
    calendly_link = ""
    analyzed_domain = ""
    company_name = ""
    website_url = ""
    support_email = ""
    impressum_url = ""
    privacy_policy_url = ""
    terms_url = ""
    hero_title = ""
    hero_text = ""
    primary_color = ""
    secondary_color = ""
    accent_color = ""
    logo_url = ""
    
    try:
        facebook_business_whatsapp = settings.facebook_business_whatsapp
        calendly_link = settings.calendly_link
        analyzed_domain = settings.analyzed_domain
        company_name = settings.company_name

        primary_color = settings.primary_color
        secondary_color = settings.secondary_color
        accent_color = settings.accent_color
        logo_url = settings.logo_url
    except:
        # Fallback to direct .env reading
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('FACEBOOK_BUSINESS_WHATSAPP='):
                        facebook_business_whatsapp = line.split('=', 1)[1]
                    elif line.startswith('CALENDLY_LINK='):
                        calendly_link = line.split('=', 1)[1]
                    elif line.startswith('ANALYZED_DOMAIN='):
                        analyzed_domain = line.split('=', 1)[1]
                    elif line.startswith('COMPANY_NAME='):
                        company_name = line.split('=', 1)[1]
                    elif line.startswith('WEBSITE_URL='):
                        website_url = line.split('=', 1)[1]
                    elif line.startswith('SUPPORT_EMAIL='):
                        support_email = line.split('=', 1)[1]
                    elif line.startswith('IMPRESSUM_URL='):
                        impressum_url = line.split('=', 1)[1]
                    elif line.startswith('PRIVACY_POLICY_URL='):
                        privacy_policy_url = line.split('=', 1)[1]
                    elif line.startswith('TERMS_URL='):
                        terms_url = line.split('=', 1)[1]
                    elif line.startswith('HERO_TITLE='):
                        hero_title = line.split('=', 1)[1]
                    elif line.startswith('HERO_TEXT='):
                        hero_text = line.split('=', 1)[1]
                    elif line.startswith('PRIMARY_COLOR='):
                        primary_color = line.split('=', 1)[1]
                    elif line.startswith('SECONDARY_COLOR='):
                        secondary_color = line.split('=', 1)[1]
                    elif line.startswith('ACCENT_COLOR='):
                        accent_color = line.split('=', 1)[1]
                    elif line.startswith('LOGO_URL='):
                        logo_url = line.split('=', 1)[1]
    
    return {
        "assistantId": assistant_id,
        "publicKey": public_key,
        # "privateKey": private_key,  # REMOVED: Private key should never be exposed to frontend
        "facebookBusinessWhatsApp": facebook_business_whatsapp,
        "calendlyLink": calendly_link,
        "analyzedDomain": analyzed_domain,
        "companyName": company_name,
        "websiteUrl": website_url,
        "supportEmail": support_email,
        "impressumUrl": impressum_url,
        "privacyPolicyUrl": privacy_policy_url,
        "termsUrl": terms_url,
        "heroTitle": hero_title,
        "heroText": hero_text,
        "primaryColor": primary_color,
        "secondaryColor": secondary_color,
        "accentColor": accent_color,
        "logoUrl": logo_url
    }

@app.get("/api/env-config")
def get_env_config() -> dict:
    """Public API for configuration values (deprecated - use /api/secure-config)."""
    return get_env_config_internal()

@app.get("/api/config-status")
def get_config_status() -> dict:
    """Check if configuration is complete and valid."""
    config = get_env_config_internal()
    
    # Check required VAPI credentials
    vapi_configured = bool(config.get("assistantId") and config.get("publicKey"))
    
    # Check if we have basic company info
    company_configured = bool(config.get("companyName"))
    
    # Check if we have contact info
    contact_configured = bool(config.get("facebookBusinessWhatsApp") or config.get("calendlyLink"))
    
    # Overall status
    is_complete = vapi_configured and company_configured
    
    missing_items = []
    if not config.get("assistantId"):
        missing_items.append("VAPI Assistant ID")
    if not config.get("publicKey"):
        missing_items.append("VAPI Public Key")
    if not config.get("companyName"):
        missing_items.append("Company Name")
    if not contact_configured:
        missing_items.append("Contact Information (WhatsApp or Calendly)")
    
    return {
        "isComplete": is_complete,
        "vapiConfigured": vapi_configured,
        "companyConfigured": company_configured,
        "contactConfigured": contact_configured,
        "missingItems": missing_items,
        "config": config
    }









@app.post("/save-vapi-credentials")
async def save_vapi_credentials(
    assistant_id: str = Form(...),
    public_key: str = Form(...),
    private_key: str = Form(default=""),
) -> dict[str, str]:
    """Save VAPI credentials to .env file."""
    try:
        from pathlib import Path
        
        env_file = Path(".env")
        
        # Create .env file if it doesn't exist
        if not env_file.exists():
            with open(env_file, 'w') as f:
                f.write("# VAPI Configuration\n")
                f.write("# Generated by VAPI Demo Platform\n\n")
                f.write("# VAPI Assistant ID (UUID format) - REQUIRED\n")
                f.write(f"ASSISTANT_ID={assistant_id}\n\n")
                f.write("# VAPI Public Key (UUID format) - REQUIRED\n")
                f.write(f"PUBLIC_KEY={public_key}\n\n")
                if private_key:
                    f.write("# VAPI Private Key - OPTIONAL (for chat functionality)\n")
                    f.write(f"VAPI_PRIVATE_KEY={private_key}\n")
        else:
            # Update existing .env file
            lines = []
            with open(env_file, 'r') as f:
                lines = f.readlines()
            
            # Update or add credentials
            assistant_found = False
            public_key_found = False
            private_key_found = False
            
            for i, line in enumerate(lines):
                if line.strip().startswith('ASSISTANT_ID='):
                    lines[i] = f"ASSISTANT_ID={assistant_id}\n"
                    assistant_found = True
                elif line.strip().startswith('PUBLIC_KEY='):
                    lines[i] = f"PUBLIC_KEY={public_key}\n"
                    public_key_found = True
                elif line.strip().startswith('VAPI_PRIVATE_KEY='):
                    if private_key:
                        lines[i] = f"VAPI_PRIVATE_KEY={private_key}\n"
                    else:
                        lines[i] = ""  # Remove line if private_key is empty
                    private_key_found = True
            
            # Add missing credentials
            if not assistant_found:
                lines.append(f"ASSISTANT_ID={assistant_id}\n")
            if not public_key_found:
                lines.append(f"PUBLIC_KEY={public_key}\n")
            if not private_key_found and private_key:
                lines.append(f"VAPI_PRIVATE_KEY={private_key}\n")
            
            # Write back to file
            with open(env_file, 'w') as f:
                f.writelines(lines)
        
        # Reset settings cache to reload new values
        from .config import reset_settings_cache
        reset_settings_cache()
        
        return {
            "status": "success",
            "message": "VAPI credentials saved successfully to .env file"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to save credentials: {str(e)}"
        }


@app.post("/save-manual-inputs")
async def save_manual_inputs(
    facebook_business_whatsapp: str = Form(default=""),
    calendly_link: str = Form(default=""),
) -> dict[str, str]:
    """Save manual inputs to .env file."""
    try:
        from pathlib import Path
        
        env_file = Path(".env")
        
        # Read existing .env content
        lines = []
        if env_file.exists():
            with open(env_file, 'r') as f:
                lines = f.readlines()
        
        # Update or add manual inputs
        whatsapp_found = False
        calendly_found = False
        
        for i, line in enumerate(lines):
            if line.strip().startswith('FACEBOOK_BUSINESS_WHATSAPP='):
                if facebook_business_whatsapp:
                    lines[i] = f"FACEBOOK_BUSINESS_WHATSAPP={facebook_business_whatsapp}\n"
                else:
                    lines[i] = ""  # Remove line if empty
                whatsapp_found = True
            elif line.strip().startswith('CALENDLY_LINK='):
                if calendly_link:
                    lines[i] = f"CALENDLY_LINK={calendly_link}\n"
                else:
                    lines[i] = ""  # Remove line if empty
                calendly_found = True
        
        # Add missing entries
        if not whatsapp_found and facebook_business_whatsapp:
            lines.append(f"FACEBOOK_BUSINESS_WHATSAPP={facebook_business_whatsapp}\n")
        if not calendly_found and calendly_link:
            lines.append(f"CALENDLY_LINK={calendly_link}\n")
        
        # Write back to file
        with open(env_file, 'w') as f:
            f.writelines(lines)
        
        # Reset settings cache to reload new values
        from .config import reset_settings_cache
        reset_settings_cache()
        
        return {
            "status": "success",
            "message": "Manuelle Eingaben erfolgreich in .env gespeichert"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Fehler beim Speichern der manuellen Eingaben: {str(e)}"
        }


@app.post("/save-domain-analysis")
async def save_domain_analysis(
    analyzed_domain: str = Form(default=""),
    company_name: str = Form(default=""),
    website_url: str = Form(default=""),
    support_email: str = Form(default=""),
    impressum_url: str = Form(default=""),
    privacy_policy_url: str = Form(default=""),
    terms_url: str = Form(default=""),
    hero_title: str = Form(default=""),
    hero_text: str = Form(default=""),
    primary_color: str = Form(default=""),
    secondary_color: str = Form(default=""),
    accent_color: str = Form(default=""),
    logo_url: str = Form(default=""),
) -> dict[str, str]:
    """Save domain analysis results to .env file."""
    try:
        from pathlib import Path
        
        env_file = Path(".env")
        
        # Read existing .env content
        lines = []
        if env_file.exists():
            with open(env_file, 'r') as f:
                lines = f.readlines()
        
        # Track which fields we've found
        fields_found = {
            'ANALYZED_DOMAIN': False,
            'COMPANY_NAME': False,
            'WEBSITE_URL': False,
            'SUPPORT_EMAIL': False,
            'IMPRESSUM_URL': False,
            'PRIVACY_POLICY_URL': False,
            'TERMS_URL': False,
            'HERO_TITLE': False,
            'HERO_TEXT': False,
            'PRIMARY_COLOR': False,
            'SECONDARY_COLOR': False,
            'ACCENT_COLOR': False,
            'LOGO_URL': False
        }
        
        # Update existing lines
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('ANALYZED_DOMAIN='):
                lines[i] = f"ANALYZED_DOMAIN={analyzed_domain}\n" if analyzed_domain else ""
                fields_found['ANALYZED_DOMAIN'] = True
            elif stripped.startswith('COMPANY_NAME='):
                lines[i] = f"COMPANY_NAME={company_name}\n" if company_name else ""
                fields_found['COMPANY_NAME'] = True
            elif stripped.startswith('WEBSITE_URL='):
                if website_url:  # Only update if not empty
                    lines[i] = f"WEBSITE_URL={website_url}\n"
                    fields_found['WEBSITE_URL'] = True
            elif stripped.startswith('SUPPORT_EMAIL='):
                if support_email:  # Only update if not empty
                    lines[i] = f"SUPPORT_EMAIL={support_email}\n"
                    fields_found['SUPPORT_EMAIL'] = True
            elif stripped.startswith('IMPRESSUM_URL='):
                if impressum_url:  # Only update if not empty
                    lines[i] = f"IMPRESSUM_URL={impressum_url}\n"
                    fields_found['IMPRESSUM_URL'] = True
            elif stripped.startswith('PRIVACY_POLICY_URL='):
                if privacy_policy_url:  # Only update if not empty
                    lines[i] = f"PRIVACY_POLICY_URL={privacy_policy_url}\n"
                    fields_found['PRIVACY_POLICY_URL'] = True
            elif stripped.startswith('TERMS_URL='):
                if terms_url:  # Only update if not empty
                    lines[i] = f"TERMS_URL={terms_url}\n"
                    fields_found['TERMS_URL'] = True
            elif stripped.startswith('HERO_TITLE='):
                lines[i] = f"HERO_TITLE={hero_title}\n" if hero_title else ""
                fields_found['HERO_TITLE'] = True
            elif stripped.startswith('HERO_TEXT='):
                lines[i] = f"HERO_TEXT={hero_text}\n" if hero_text else ""
                fields_found['HERO_TEXT'] = True
            elif stripped.startswith('PRIMARY_COLOR='):
                lines[i] = f"PRIMARY_COLOR={primary_color}\n" if primary_color else ""
                fields_found['PRIMARY_COLOR'] = True
            elif stripped.startswith('SECONDARY_COLOR='):
                lines[i] = f"SECONDARY_COLOR={secondary_color}\n" if secondary_color else ""
                fields_found['SECONDARY_COLOR'] = True
            elif stripped.startswith('ACCENT_COLOR='):
                lines[i] = f"ACCENT_COLOR={accent_color}\n" if accent_color else ""
                fields_found['ACCENT_COLOR'] = True
            elif stripped.startswith('LOGO_URL='):
                lines[i] = f"LOGO_URL={logo_url}\n" if logo_url else ""
                fields_found['LOGO_URL'] = True
        
        # Add missing entries
        new_entries = []
        if not fields_found['ANALYZED_DOMAIN'] and analyzed_domain:
            new_entries.append(f"ANALYZED_DOMAIN={analyzed_domain}\n")
        if not fields_found['COMPANY_NAME'] and company_name:
            new_entries.append(f"COMPANY_NAME={company_name}\n")
        if not fields_found['WEBSITE_URL'] and website_url:
            new_entries.append(f"WEBSITE_URL={website_url}\n")
        if not fields_found['SUPPORT_EMAIL'] and support_email:
            new_entries.append(f"SUPPORT_EMAIL={support_email}\n")
        if not fields_found['IMPRESSUM_URL'] and impressum_url:
            new_entries.append(f"IMPRESSUM_URL={impressum_url}\n")
        if not fields_found['PRIVACY_POLICY_URL'] and privacy_policy_url:
            new_entries.append(f"PRIVACY_POLICY_URL={privacy_policy_url}\n")
        if not fields_found['TERMS_URL'] and terms_url:
            new_entries.append(f"TERMS_URL={terms_url}\n")
        if not fields_found['HERO_TITLE'] and hero_title:
            new_entries.append(f"HERO_TITLE={hero_title}\n")
        if not fields_found['HERO_TEXT'] and hero_text:
            new_entries.append(f"HERO_TEXT={hero_text}\n")
        if not fields_found['PRIMARY_COLOR'] and primary_color:
            new_entries.append(f"PRIMARY_COLOR={primary_color}\n")
        if not fields_found['SECONDARY_COLOR'] and secondary_color:
            new_entries.append(f"SECONDARY_COLOR={secondary_color}\n")
        if not fields_found['ACCENT_COLOR'] and accent_color:
            new_entries.append(f"ACCENT_COLOR={accent_color}\n")
        if not fields_found['LOGO_URL'] and logo_url:
            new_entries.append(f"LOGO_URL={logo_url}\n")
        
        # Add new entries if any
        if new_entries:
            # Add section header if needed
            if not any('Domain Analysis' in line for line in lines):
                lines.append("\n# Domain Analysis Results\n")
            lines.extend(new_entries)
        
        # Write back to file
        with open(env_file, 'w') as f:
            f.writelines(lines)
        
        # Reset settings cache to reload new values
        from .config import reset_settings_cache
        reset_settings_cache()
        
        return {
            "status": "success",
            "message": "Domain-Analyse-Ergebnisse erfolgreich in .env gespeichert"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Fehler beim Speichern der Domain-Analyse: {str(e)}"
        }





@app.get("/analyze-brand")
async def analyze_brand(domain: str = Query(..., description="Domain to analyze")) -> dict:
    """Analyze a brand/domain and extract company information."""
    try:
        # Clean domain
        clean_domain = domain.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
        
        # Extract company name from domain
        company_name = clean_domain.replace('.com', '').replace('.de', '').replace('.org', '').replace('.net', '')
        company_name = company_name.replace('-', ' ').replace('_', ' ').title()
        
        # Generate URLs with fallback system
        logo_url_primary = f"https://t1.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=http://{clean_domain}&size=128"
        logo_url_fallback = f"https://www.google.com/s2/favicons?domain={clean_domain}&sz=128"
        website_url = f"https://{clean_domain}"
        support_email = f"info@{clean_domain}"
        impressum_url = f"https://{clean_domain}/impressum"
        privacy_url = f"https://{clean_domain}/datenschutz"
        terms_url = f"https://{clean_domain}/agb"
        
        # Extract brand colors using the color extractor service
        try:
            primary_color, secondary_color, accent_color = extract_brand_colors(clean_domain)
            print(f"✅ Brand colors extracted: {primary_color}, {secondary_color}, {accent_color}")
        except Exception as e:
            print(f"⚠️ Color extraction failed: {e}, using defaults")
            primary_color = "#4361ee"    # Standard blue
            secondary_color = "#3a0ca3"  # Standard dark blue  
            accent_color = "#4cc9f0"     # Standard light blue
        
        # Automatically save to .env file
        try:
            await save_domain_analysis(
                analyzed_domain=clean_domain,
                company_name=company_name,
                website_url=website_url,
                support_email=support_email,
                impressum_url=impressum_url,
                privacy_policy_url=privacy_url,
                terms_url=terms_url,
                hero_title="",  # Empty, user can fill manually
                hero_text="",   # Empty, user can fill manually
                primary_color=primary_color,
                secondary_color=secondary_color,
                accent_color=accent_color,
                logo_url=logo_url_primary
            )
            print(f"✅ Domain analysis results automatically saved to .env")
        except Exception as e:
            print(f"⚠️ Failed to save domain analysis to .env: {e}")

        return {
            "success": True,
            "domain": clean_domain,
            "company_name": company_name,
            "logo_url": logo_url_primary,
            "logo_url_fallback": logo_url_fallback,
            "website_url": website_url,
            "support_email": support_email,
            "impressum_url": impressum_url,
            "privacy_url": privacy_url,
            "terms_url": terms_url,
            "colors": {
                "primary": primary_color,
                "secondary": secondary_color,
                "accent": accent_color
            },
            "extracted_info": {
                "companyName": company_name,
                "logoUrl": logo_url_primary,
                "logoUrlFallback": logo_url_fallback,
                "websiteUrl": website_url,
                "supportEmail": support_email,
                "impressumUrl": impressum_url,
                "privacyPolicyUrl": privacy_url,
                "termsUrl": terms_url,
                "primaryColor": primary_color,
                "secondaryColor": secondary_color,
                "accentColor": accent_color
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "domain": domain
        }


@app.get("/test_web_sdk", response_class=HTMLResponse)
def test_web_sdk_page(request: Request) -> HTMLResponse:
    """Test page for VapiAI Web SDK with Assistant Overrides."""
    return templates.TemplateResponse("test_web_sdk.html", {"request": request})


@app.get("/test-webhook")
async def test_webhook() -> dict:
    """Test endpoint für den VAPI Webhook."""
    return {
        "message": "VAPI Webhook ist bereit!",
        "endpoints": {
            "send_message": "/webhook/vapi/send-message",
            "general_webhook": "/webhook/vapi"
        },
        "usage": {
            "send_message": "POST mit JSON: {'message': {'role': 'assistant', 'content': 'Nachricht'}}",
            "general_webhook": "POST mit VAPI Webhook Event"
        }
    }


# Shlink URL Shortening Endpoints
@app.post("/api/shorten-url", response_model=ShortUrlResponse)
async def shorten_url(request: ShortUrlRequest) -> ShortUrlResponse:
    """Create a short URL using Shlink."""
    try:
        result = await shlink_service.create_short_url(
            long_url=request.longUrl,
            tags=request.tags,
            title=request.title,
            crawlable=request.crawlable,
            forward_query=request.forwardQuery
        )
        
        if result is None:
            raise HTTPException(status_code=500, detail="Failed to create short URL")
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating short URL: {str(e)}")

@app.get("/api/short-urls")
async def list_short_urls(limit: int = Query(default=10, ge=1, le=100)) -> dict:
    """List short URLs from Shlink."""
    try:
        urls = await shlink_service.list_short_urls(limit=limit)
        if urls is None:
            raise HTTPException(status_code=500, detail="Failed to list short URLs")
        
        return {
            "success": True,
            "shortUrls": urls,
            "count": len(urls)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing short URLs: {str(e)}")

@app.get("/api/short-url/{short_code}/stats")
async def get_short_url_stats(short_code: str) -> dict:
    """Get statistics for a short URL."""
    try:
        stats = await shlink_service.get_short_url_stats(short_code)
        if stats is None:
            raise HTTPException(status_code=404, detail="Short URL not found or stats unavailable")
        
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint with Redis status."""
    redis_info = await redis_service.get_redis_info()
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "redis": redis_info
    }

@app.get("/api/messages-OLD-DISABLED/{session_id}")
async def get_session_messages_OLD_DISABLED(session_id: str):
    """Get messages for a specific session."""
    try:
        messages = await redis_service.get_session_messages(session_id)
        return {
            "success": True,
            "messages": messages,
            "count": len(messages)
        }
    except Exception as e:
        print(f"❌ Error getting messages for session {session_id}: {e}")
        return {
            "success": False,
            "error": str(e),
            "messages": []
        }

@app.delete("/api/messages/{session_id}")
async def clear_session_messages(session_id: str):
    """Clear all messages for a specific session."""
    try:
        success = await redis_service.clear_session_messages(session_id)
        return {
            "success": success,
            "message": "Messages cleared" if success else "Failed to clear messages"
        }
    except Exception as e:
        print(f"❌ Error clearing messages for session {session_id}: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/debug/sessions")
async def debug_sessions():
    """Debug endpoint to see current session mappings"""
    return {
        "browser_session_mapping": dict(browser_session_mapping),
        "webhook_messages_keys": list(webhook_messages.keys()),
        "redis_connected": redis_service.redis_client is not None
    }
