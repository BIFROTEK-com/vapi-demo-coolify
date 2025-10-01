#!/bin/bash

echo "🚀 Testing VAPI Demo Docker Setup"
echo "=================================="

# Build the Docker image
echo "📦 Building Docker image..."
docker build -t vapi-demo-test .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed!"
    exit 1
fi

echo "✅ Docker image built successfully"

# Test the container with minimal environment
echo "🧪 Testing container startup..."
docker run --rm \
  -e ASSISTANT_ID="test-assistant-id" \
  -e PUBLIC_KEY="test-public-key" \
  -e VAPI_PRIVATE_KEY="test-private-key" \
  -e REDIS_URL="redis://localhost:6379" \
  -e SHLINK_API_KEY="test-shlink-key" \
  -e SHLINK_BASE_URL="http://localhost:8080/rest/v3" \
  vapi-demo-test python -c "import app.main; print('✅ Import successful')"

if [ $? -eq 0 ]; then
    echo "✅ Container test passed!"
else
    echo "❌ Container test failed!"
    exit 1
fi

# Test with docker-compose
echo "🐳 Testing docker-compose..."
docker-compose up --build -d

if [ $? -eq 0 ]; then
    echo "✅ Docker-compose started successfully"
    
    # Wait a bit for services to start
    echo "⏳ Waiting for services to start..."
    sleep 30
    
    # Test health endpoint
    echo "🏥 Testing health endpoint..."
    curl -f http://localhost:8000/health
    
    if [ $? -eq 0 ]; then
        echo "✅ Health check passed!"
    else
        echo "❌ Health check failed!"
    fi
    
    # Stop services
    echo "🛑 Stopping services..."
    docker-compose down
else
    echo "❌ Docker-compose failed!"
    exit 1
fi

echo "🎉 All tests completed!"
