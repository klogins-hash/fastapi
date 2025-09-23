# Basic LangGraph Agent for Railway

A FastAPI + LangGraph agent with Vapi compatibility for voice AI applications.

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/-NvLj4?referralCode=CRJ8FE)

## ✨ Features

- ✅ FastAPI web server with LangGraph agent
- ✅ Claude 3 Haiku for fast AI responses
- ✅ Vapi-compatible `/v1/chat/completions` endpoint
- ✅ API key authentication for security
- ✅ Railway deployment ready
- ✅ Health check endpoint

## 🚀 Quick Deploy to Railway

1. **Set Environment Variables in Railway:**

   ```bash
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   LANGGRAPH_API_KEY=iBO5m3Bt8occmHmpOTzx6-7UTtWWQSoTW8gGQyWnoZ0
   ```

2. **Deploy:**
   - Push changes to your GitHub repo
   - Railway will auto-deploy with the updated configuration

## 🔐 API Endpoints

- `GET /` - Welcome message
- `POST /v1/chat/completions` - **Secured** Vapi-compatible chat endpoint
- `GET /health` - Health check
- `GET /v1/models` - Available models
- `POST /test` - Test endpoint for development

## 💁‍♀️ Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ANTHROPIC_API_KEY="your-key-here"
export LANGGRAPH_API_KEY="iBO5m3Bt8occmHmpOTzx6-7UTtWWQSoTW8gGQyWnoZ0"

# Run locally
python main.py
```

## 🔗 Vapi Integration

1. **In Vapi Dashboard:**
   - Go to Models → Custom LLM
   - **Endpoint URL:** `https://your-railway-app.railway.app/v1/chat/completions`
   - **Authentication:** Select "API Key"
   - **API Key:** `iBO5m3Bt8occmHmpOTzx6-7UTtWWQSoTW8gGQyWnoZ0`

2. **Test Authentication:**

   ```bash
   # This will work (with correct API key):
   curl -X POST "https://your-railway-app.railway.app/v1/chat/completions" \
     -H "Authorization: Bearer iBO5m3Bt8occmHmpOTzx6-7UTtWWQSoTW8gGQyWnoZ0" \
     -H "Content-Type: application/json" \
     -d '{"model": "basic-langgraph-agent", "messages": [{"role": "user", "content": "Hello!"}]}'
   ```

## 📝 Notes

- Uses Claude 3 Haiku for fast, cost-effective responses
- API key authentication protects your endpoints
- Compatible with Vapi's custom LLM integration
- Railway handles scaling and deployment automatically
