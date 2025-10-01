#!/usr/bin/env python3
"""
Redis Debug Test Script
Testet die Redis-Verbindung und zeigt detaillierte Debug-Informationen.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.services.redis_service import RedisService
from app.config import get_settings


async def test_redis_connection():
    """Test Redis connection with detailed debugging."""
    print("🔍 Redis Debug Test")
    print("=" * 50)
    
    # Load settings
    settings = get_settings()
    print(f"📋 Settings loaded:")
    print(f"   REDIS_URL: {'✅ Set' if settings.redis_url else '❌ Not set'}")
    print(f"   REDIS_USERNAME: {'✅ Set' if settings.redis_username else '❌ Not set'}")
    print(f"   REDIS_PASSWORD: {'✅ Set' if settings.redis_password else '❌ Not set'}")
    
    if settings.redis_url:
        print(f"   URL Value: {settings.redis_url[:50]}...")
    if settings.redis_username:
        print(f"   Username: {settings.redis_username}")
    if settings.redis_password:
        print(f"   Password: {settings.redis_password[:10]}...")
    
    print("\n🔌 Testing Redis Connection...")
    
    # Create Redis service
    redis_service = RedisService()
    
    # Test connection
    connected = await redis_service.connect()
    
    if connected:
        print("✅ Redis connection successful!")
        
        # Test basic operations
        print("\n🧪 Testing Redis Operations...")
        
        # Test ping
        try:
            await redis_service.redis_client.ping()
            print("✅ Ping successful")
        except Exception as e:
            print(f"❌ Ping failed: {e}")
        
        # Test set/get
        try:
            await redis_service.redis_client.set("test_key", "test_value", ex=60)
            value = await redis_service.redis_client.get("test_key")
            if value == "test_value":
                print("✅ Set/Get operations successful")
            else:
                print(f"❌ Set/Get failed: expected 'test_value', got '{value}'")
        except Exception as e:
            print(f"❌ Set/Get operations failed: {e}")
        
        # Test session operations
        print("\n📝 Testing Session Operations...")
        session_id = "test_session_123"
        session_data = {"user_id": "test_user", "status": "active"}
        
        # Store session
        stored = await redis_service.store_session(session_id, session_data)
        if stored:
            print("✅ Session storage successful")
        else:
            print("❌ Session storage failed")
        
        # Retrieve session
        retrieved = await redis_service.get_session(session_id)
        if retrieved and retrieved.get("user_id") == "test_user":
            print("✅ Session retrieval successful")
        else:
            print(f"❌ Session retrieval failed: {retrieved}")
        
        # Get Redis info
        print("\n📊 Redis Server Info:")
        info = await redis_service.get_redis_info()
        for key, value in info.items():
            print(f"   {key}: {value}")
        
        # Cleanup
        await redis_service.redis_client.delete("test_key")
        await redis_service.delete_session(session_id)
        print("\n🧹 Cleanup completed")
        
    else:
        print("❌ Redis connection failed!")
        print("\n🔍 Debug Information:")
        print(f"   Connection attempted: {redis_service._connection_attempted}")
        print(f"   Redis client: {redis_service.redis_client}")
        
        # Check environment variables
        print("\n🌍 Environment Variables:")
        env_vars = ["REDIS_URL", "REDIS_USERNAME", "REDIS_PASSWORD"]
        for var in env_vars:
            value = os.getenv(var)
            if value:
                print(f"   {var}: {'✅ Set' if value else '❌ Empty'}")
                if var == "REDIS_URL":
                    print(f"      Value: {value[:50]}...")
                elif var == "REDIS_PASSWORD":
                    print(f"      Value: {value[:10]}...")
                else:
                    print(f"      Value: {value}")
            else:
                print(f"   {var}: ❌ Not set")
    
    # Disconnect
    await redis_service.disconnect()
    print("\n🔌 Redis connection closed")


async def test_redis_with_different_configs():
    """Test Redis with different configuration approaches."""
    print("\n🔧 Testing Different Redis Configurations...")
    print("=" * 50)
    
    # Test 1: Direct URL connection
    print("\n1️⃣ Testing Direct URL Connection...")
    try:
        import redis.asyncio as redis
        
        # Try with REDIS_URL
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            print(f"   Testing URL: {redis_url[:50]}...")
            client = redis.from_url(redis_url, decode_responses=True)
            await client.ping()
            print("   ✅ Direct URL connection successful")
            await client.close()
        else:
            print("   ❌ REDIS_URL not set")
            
    except Exception as e:
        print(f"   ❌ Direct URL connection failed: {e}")
    
    # Test 2: Username/Password connection
    print("\n2️⃣ Testing Username/Password Connection...")
    try:
        import redis.asyncio as redis
        
        username = os.getenv("REDIS_USERNAME")
        password = os.getenv("REDIS_PASSWORD")
        
        if username and password:
            print(f"   Testing with username: {username}")
            client = redis.Redis(
                host='causal-dinosaur-63242.upstash.io',
                port=6379,
                username=username,
                password=password,
                decode_responses=True,
                ssl=True
            )
            await client.ping()
            print("   ✅ Username/Password connection successful")
            await client.close()
        else:
            print("   ❌ REDIS_USERNAME or REDIS_PASSWORD not set")
            
    except Exception as e:
        print(f"   ❌ Username/Password connection failed: {e}")


if __name__ == "__main__":
    print("🚀 Starting Redis Debug Test...")
    asyncio.run(test_redis_connection())
    asyncio.run(test_redis_with_different_configs())
    print("\n✅ Redis Debug Test completed!")
