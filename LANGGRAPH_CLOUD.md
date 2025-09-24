# LangGraph Cloud Deployment Guide

This project is optimized for deployment on LangGraph Cloud via the LangSmith platform.

## 🚀 Quick Deploy to LangGraph Cloud

### 1. Prerequisites
- LangSmith account at [smith.langchain.com](https://smith.langchain.com)
- Anthropic API key
- LangGraph CLI installed: `pip install langgraph-cli`

### 2. Environment Setup

Create a `.env` file:
```bash
cp .env.example .env
```

Fill in your API keys:
```bash
ANTHROPIC_API_KEY=your_anthropic_api_key_here
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=langgraph-cloud-agent
```

### 3. Deploy to LangGraph Cloud

```bash
# Login to LangSmith
langgraph login

# Deploy the agent
langgraph deploy

# Or deploy with a specific name
langgraph deploy --name "my-agent"
```

### 4. Test Your Deployment

```bash
# Test via CLI
langgraph test

# Or test via Python SDK
python test_deployment.py
```

## 📊 Features

- ✅ **Optimized for LangGraph Cloud**: Proper state management and graph structure
- ✅ **Tool Integration**: Example tools with easy expansion
- ✅ **Memory Persistence**: Conversation memory across interactions
- ✅ **LangSmith Tracing**: Full observability and debugging
- ✅ **Scalable Architecture**: Cloud-native design
- ✅ **Type Safety**: Full TypeScript-style typing

## 🔧 Local Development

```bash
# Install dependencies
pip install -e .

# Run locally
python agent.py
```

## 🌐 API Endpoints (LangGraph Cloud)

Once deployed, your agent will be available at:
- **Invoke**: `POST /invoke`
- **Stream**: `POST /stream`
- **Async Invoke**: `POST /ainvoke`
- **Health Check**: `GET /health`

## 🔗 Integration

### With Vapi (Voice AI)
Use the LangGraph Cloud endpoint URL in Vapi's custom LLM configuration:
- **Endpoint**: `https://your-deployment.langraph.app/invoke`
- **Authentication**: LangSmith API Key

### With Other Applications
The deployed agent provides a standard LangGraph API that can be integrated with any application supporting HTTP requests.

## 📝 Configuration

The `langgraph.json` file defines:
- **Dependencies**: Python packages and local modules
- **Graphs**: Entry points for your agents
- **Environment**: Environment variable configuration

## 🔍 Monitoring

Access your deployment dashboard at:
- **LangSmith**: [smith.langchain.com](https://smith.langchain.com)
- **Traces**: View all agent interactions and performance
- **Metrics**: Monitor usage, latency, and errors
