#!/usr/bin/env python3
"""
Redis Startup Test Script
Testet die Redis-Initialisierung wie in der main.py.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.services.redis_service import redis_service
from app.config import get_settings


async def test_redis_startup():
    """Test Redis startup like in main.py."""
    print("🚀 Testing Redis Startup (like in main.py)")
    print("=" * 50)
    
    # Load settings
    settings = get_settings()
    print(f"📋 Settings loaded:")
    print(f"   REDIS_URL: {'✅ Set' if settings.redis_url else '❌ Not set'}")
    
    if settings.redis_url:
        print(f"   URL Value: {settings.redis_url[:50]}...")
    
    print("\n🔌 Testing Redis Connection (startup event)...")
    
    # Simulate startup event
    await redis_service.connect()
    if redis_service.is_connected():
        print("✅ Redis service initialized successfully")
    else:
        print("ℹ️ Redis service not available - using in-memory storage (single-worker only)")
    
    # Test basic operations
    print("\n🧪 Testing Basic Operations...")
    
    # Test session storage
    session_id = "test_startup_session"
    session_data = {"user_id": "test_user", "status": "active"}
    
    stored = await redis_service.store_session(session_id, session_data)
    if stored:
        print("✅ Session storage successful")
    else:
        print("❌ Session storage failed")
    
    # Test session retrieval
    retrieved = await redis_service.get_session(session_id)
    if retrieved and retrieved.get("user_id") == "test_user":
        print("✅ Session retrieval successful")
    else:
        print(f"❌ Session retrieval failed: {retrieved}")
    
    # Test message storage
    message_data = {
        "content": "Test message from startup",
        "role": "assistant",
        "timestamp": "2024-01-01T00:00:00Z"
    }
    
    message_stored = await redis_service.add_message_to_session(session_id, message_data)
    if message_stored:
        print("✅ Message storage successful")
    else:
        print("❌ Message storage failed")
    
    # Test message retrieval
    messages = await redis_service.get_session_messages(session_id)
    if messages and len(messages) > 0:
        print(f"✅ Message retrieval successful: {len(messages)} messages")
    else:
        print("❌ Message retrieval failed")
    
    # Get Redis info
    print("\n📊 Redis Server Info:")
    info = await redis_service.get_redis_info()
    for key, value in info.items():
        print(f"   {key}: {value}")
    
    # Cleanup
    await redis_service.delete_session(session_id)
    await redis_service.clear_session_messages(session_id)
    print("\n🧹 Cleanup completed")
    
    # Disconnect
    await redis_service.disconnect()
    print("🔌 Redis connection closed")


async def test_redis_connection_status():
    """Test Redis connection status checking."""
    print("\n🔍 Testing Redis Connection Status...")
    print("=" * 50)
    
    # Test before connection
    print(f"Before connection: {redis_service.is_connected()}")
    
    # Connect
    await redis_service.connect()
    print(f"After connection: {redis_service.is_connected()}")
    
    # Test operations
    if redis_service.is_connected():
        print("✅ Redis is connected - operations should work")
        
        # Test a simple operation
        try:
            await redis_service.redis_client.ping()
            print("✅ Ping successful")
        except Exception as e:
            print(f"❌ Ping failed: {e}")
    else:
        print("❌ Redis is not connected - operations will fail")
    
    # Disconnect
    await redis_service.disconnect()
    print(f"After disconnect: {redis_service.is_connected()}")


if __name__ == "__main__":
    print("🚀 Starting Redis Startup Test...")
    asyncio.run(test_redis_startup())
    asyncio.run(test_redis_connection_status())
    print("\n✅ Redis Startup Test completed!")
