"""
Basic LangGraph Agent for Railway Deployment
Simple FastAPI + LangGraph agent with Vapi compatibility
"""

from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import os
from datetime import datetime
import logging
import secrets
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# LangGraph imports
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from typing_extensions import TypedDict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Basic LangGraph Agent", version="1.0.0")

# Security: API Key Authentication
def verify_api_key(authorization: Optional[str] = Header(None)):
    """Verify API key for secure access"""
    # Get the expected API key from environment
    expected_key = os.getenv("LANGGRAPH_API_KEY")
    
    if not expected_key:
        # If no API key is set, allow access (for development)
        logger.warning("No LANGGRAPH_API_KEY set - running in development mode")
        return None
    
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format. Use 'Bearer <token>'")
    
    token = authorization[7:]  # Remove "Bearer " prefix
    
    if token != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return token

# Vapi-compatible models
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7

class ChatCompletionChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: str

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]

# LangGraph State
class AgentState(TypedDict):
    messages: List[BaseMessage]
    next: str

# Simple agent node
def agent_node(state: AgentState) -> AgentState:
    """Main agent processing node"""
    try:
        # Get the LLM
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY required")
        
        llm = ChatAnthropic(
            model="claude-3-haiku-20240307",  # Using faster model for basic version
            anthropic_api_key=api_key,
            max_tokens=500,
            temperature=0.7
        )
        
        # Get the last message
        messages = state["messages"]
        if not messages:
            return {"messages": messages, "next": END}
        
        # Generate response
        response = llm.invoke(messages)
        
        # Add response to messages
        updated_messages = messages + [response]
        
        return {"messages": updated_messages, "next": END}
        
    except Exception as e:
        logger.error(f"Agent error: {str(e)}")
        error_msg = AIMessage(content=f"I encountered an error: {str(e)}")
        return {"messages": messages + [error_msg], "next": END}

# Create the graph
def create_agent_graph():
    """Create a simple LangGraph agent"""
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("agent", agent_node)
    
    # Set entry point
    workflow.set_entry_point("agent")
    
    # Compile the graph
    return workflow.compile()

# Global agent instance
agent_graph = None

def get_agent():
    """Get or create the agent graph"""
    global agent_graph
    if agent_graph is None:
        agent_graph = create_agent_graph()
    return agent_graph

# Original root endpoint
@app.get("/")
async def root():
    return {"greeting": "Hello, World!", "message": "Basic LangGraph Agent Ready!"}

# Vapi-compatible endpoint (secured)
@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(request: ChatCompletionRequest, api_key: str = Depends(verify_api_key)):
    """Vapi-compatible chat completions endpoint"""
    try:
        # Log the incoming request for debugging
        logger.info(f"Received chat completion request: {request.dict()}")
        
        if not request.messages:
            raise HTTPException(status_code=400, detail="No messages provided")
        
        # Convert to LangChain messages
        lc_messages = []
        for msg in request.messages:
            if msg.role == "user":
                lc_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                lc_messages.append(AIMessage(content=msg.content))
        
        # Get agent and process
        agent = get_agent()
        result = agent.invoke({"messages": lc_messages, "next": "agent"})
        
        # Extract response
        if result["messages"]:
            last_message = result["messages"][-1]
            response_content = last_message.content
        else:
            response_content = "I'm ready to help!"
        
        # Format response
        response = ChatCompletionResponse(
            id="basic-" + str(abs(hash(str(datetime.now()))))[-8:],
            created=int(datetime.now().timestamp()),
            model="basic-langgraph-agent",
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=ChatMessage(
                        role="assistant",
                        content=response_content
                    ),
                    finish_reason="stop"
                )
            ]
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Chat completion error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "Basic LangGraph Agent online",
        "timestamp": datetime.now().isoformat(),
        "model": "claude-3-haiku-20240307",
        "version": "1.0.0"
    }

# Models endpoint
@app.get("/v1/models")
async def list_models():
    return {
        "object": "list",
        "data": [
            {
                "id": "basic-langgraph-agent",
                "object": "model",
                "created": int(datetime.now().timestamp()),
                "owned_by": "langgraph"
            }
        ]
    }

# Test endpoint
@app.post("/test")
async def test_agent(message: dict):
    """Test endpoint - send {"message": "your text here"}"""
    try:
        user_input = message.get("message", "Hello")
        
        # Create test messages
        messages = [HumanMessage(content=user_input)]
        
        # Get agent and process
        agent = get_agent()
        result = agent.invoke({"messages": messages, "next": "agent"})
        
        # Extract response
        if result["messages"]:
            response_content = result["messages"][-1].content
        else:
            response_content = "No response generated"
        
        return {"response": response_content, "status": "success"}
        
    except Exception as e:
        logger.error(f"Test error: {str(e)}")
        return {"error": str(e), "status": "error"}

def generate_api_key():
    """Generate a secure API key for production use"""
    return secrets.token_urlsafe(32)

# Twilio webhook endpoints for incoming calls
@app.post("/twilio/webhook/incoming-call")
async def handle_incoming_call(request: Request):
    """Handle incoming voice calls and connect to LangGraph agent"""
    try:
        # Get form data from Twilio webhook
        form_data = await request.form()
        caller_number = form_data.get("From", "Unknown")
        twilio_number = form_data.get("To", "Unknown")
        call_sid = form_data.get("CallSid", "Unknown")
        
        logger.info(f"Incoming call from {caller_number} to {twilio_number}, Call SID: {call_sid}")
        
        # Create TwiML response that greets caller and processes speech
        twiml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">Hello! You've reached the FastAPI LangGraph Agent. I'm here to help you. Please speak your question after the beep.</Say>
    <Gather 
        action="/twilio/webhook/process-speech" 
        method="POST"
        input="speech"
        speechTimeout="5"
        timeout="15"
    >
        <Say voice="alice">Please speak now.</Say>
    </Gather>
    <Say voice="alice">Thank you for calling. Goodbye!</Say>
</Response>'''
        
        return Response(content=twiml_content, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Incoming call webhook error: {str(e)}")
        error_twiml = '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">Sorry, there was an error. Please try again later.</Say>
</Response>'''
        return Response(content=error_twiml, media_type="application/xml")

@app.post("/twilio/webhook/process-speech")
async def process_speech(request: Request):
    """Process speech input and generate agent response"""
    try:
        form_data = await request.form()
        speech_result = form_data.get("SpeechResult", "")
        call_sid = form_data.get("CallSid", "Unknown")
        
        logger.info(f"Speech from call {call_sid}: {speech_result}")
        
        if not speech_result:
            twiml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">I didn't catch that. Thank you for calling!</Say>
</Response>'''
            return Response(content=twiml_content, media_type="application/xml")
        
        # Process with LangGraph agent
        try:
            agent_state = AgentState(
                messages=[HumanMessage(content=speech_result)],
                next="agent"
            )
            result = agent_node(agent_state)
            
            if result["messages"] and len(result["messages"]) > 1:
                agent_response = result["messages"][-1].content
            else:
                agent_response = "I'm here to help, but didn't generate a proper response."
                
        except Exception as agent_error:
            logger.error(f"Agent processing error: {str(agent_error)}")
            agent_response = "I'm experiencing technical difficulties right now."
        
        # Limit response length for voice
        if len(agent_response) > 400:
            agent_response = agent_response[:400] + "..."
        
        # Create TwiML response with agent's answer
        twiml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">{agent_response}</Say>
    <Pause length="1"/>
    <Say voice="alice">Thank you for using the LangGraph agent. Have a great day!</Say>
</Response>'''
        
        return Response(content=twiml_content, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Speech processing error: {str(e)}")
        error_twiml = '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">I'm sorry, I encountered an error. Thank you for calling.</Say>
</Response>'''
        return Response(content=error_twiml, media_type="application/xml")

if __name__ == "__main__":
    # Check for required API keys
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY environment variable required")
        print("💡 Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        exit(1)
    
    # Check for security API key
    langgraph_key = os.getenv("LANGGRAPH_API_KEY")
    if not langgraph_key:
        # Generate a new API key for development
        new_key = generate_api_key()
        print("🔐 No LANGGRAPH_API_KEY found. Generated new key for development:")
        print(f"   LANGGRAPH_API_KEY={new_key}")
        print("💡 Set this in Railway environment variables for production!")
        print("   In Railway: Variables → New Variable → LANGGRAPH_API_KEY")
        os.environ["LANGGRAPH_API_KEY"] = new_key
    else:
        print("🔐 Using existing LANGGRAPH_API_KEY for authentication")
    
    print("🚀 Starting Basic LangGraph Agent...")
    print("🔗 Vapi-compatible endpoints active (secured with API key)")
    print("📊 Using Claude 3 Haiku for fast responses")
    print("🛡️  Authentication: Bearer token required for /v1/chat/completions")
    
    # Railway-optimized configuration
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )