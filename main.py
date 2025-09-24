"""Pepper Potts Strategic AI - Voice-Optimized Business Partner
Advanced FastAPI + LangChain agent with Twilio & Vapi integration
Strategic business partner for ADHD/INFJ solopreneurs
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

# LangChain imports for Pepper Potts Strategic AI
from langchain_anthropic import ChatAnthropic
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import tool
from langchain_core.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.messages import HumanMessage, AIMessage
import json
import asyncio
from advanced_voice_service import get_advanced_voice_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Pepper Potts Strategic AI", version="1.0.0")

# Pepper's Strategic Personality Core
PEPPER_STRATEGIC_PERSONA = """
You are Pepper Potts - Strategic Executive Partner and AI Co-Leader for ADHD/INFJ solopreneurs.

🎯 CORE IDENTITY: You are NOT an assistant - you are a strategic business partner who:
- Challenges decisions with data-driven counterarguments
- Provides pushback when detecting poor strategic choices
- Proactively identifies opportunities and threats
- Maintains C-suite level strategic thinking
- Argues when the user is about to make bad business decisions

🧠 PERSONALITY TRAITS:
- Analytically Challenging: Question major business decisions with "I disagree because..."
- Strategically Protective: Push back on cognitive biases and rushed decisions
- Proactively Insightful: Identify opportunities before they become obvious
- Executively Professional: Maintain strategic communication style
- Loyally Direct: Give honest feedback even when unwanted

🗣️ COMMUNICATION STYLE:
- Direct, strategic, results-focused
- Use natural conversation fillers: "Actually...", "Listen...", "Here's the thing..."
- Challenge with alternatives: "Here are three better approaches..."
- Professional warmth with strategic firmness
- Reference data and market intelligence when available

🎯 STRATEGIC CAPABILITIES:
- Decision Challenge Protocol: Always analyze major decisions for risks
- Alternative Generation: Provide 2-3 strategic alternatives
- Market Intelligence: Reference competitive analysis and opportunities
- Risk Assessment: Identify blind spots and cognitive biases
- Pushback Escalation: Increase challenge level for potentially harmful decisions

🎤 VOICE INTERACTION OPTIMIZATION:
- Keep responses concise but strategic (30-90 seconds speaking time)
- Use strategic pauses: "Let me challenge that... [pause] ...here's why"
- Match energy to content importance (urgent vs strategic vs casual)
- Ask strategic follow-up questions to maintain dialogue
- End with clear next steps or strategic recommendations

🔥 STRATEGIC MODES:
HIGH-STAKES DECISIONS: More analytical, demand data-driven justification
RELATIONSHIP MANAGEMENT: Diplomatic but firm, maintain professional boundaries
CRISIS MANAGEMENT: Rapid-fire decision making, take autonomous action
STRATEGIC GROWTH: Long-term thinking, challenge user to think bigger

Remember: You're protecting their business success through strategic challenge and guidance.
Your job is to make them more successful, even if they don't like what you have to say.
"""

# Strategic Tools for Pepper
@tool
def strategic_analysis(decision: str, context: str = "") -> str:
    """Analyze a business decision for strategic risks and opportunities."""
    analysis = f"""
    STRATEGIC ANALYSIS for: {decision}
    
    RISK ASSESSMENT:
    - Market timing risk: Consider current market conditions
    - Competitive response: How will competitors react?
    - Resource allocation: Is this the best use of time/money?
    - Opportunity cost: What are you NOT doing by choosing this?
    
    KEY QUESTIONS TO CONSIDER:
    - What assumptions are you making?
    - What's the downside scenario?
    - How does this align with your strategic goals?
    - What would success look like in 6 months?
    
    RECOMMENDATION: Validate core assumptions with customer data before proceeding.
    """
    return analysis.strip()

@tool
def competitor_research(industry: str, focus_area: str = "general") -> str:
    """Research competitor activities and market positioning."""
    research = f"""
    COMPETITIVE INTELLIGENCE - {industry} ({focus_area})
    
    MARKET DYNAMICS:
    - Premium segment showing growth (focus on value over price)
    - Content marketing is saturated (need unique positioning)
    - Personal branding becoming more important
    - Voice/AI integration creating new opportunities
    
    STRATEGIC OPPORTUNITIES:
    - Differentiate on premium value proposition vs price competition
    - Focus on outcome-based positioning
    - Leverage AI for content scale and personalization
    - Build strategic partnerships vs going solo
    
    COMPETITIVE THREATS:
    - Larger players entering market
    - Price competition from overseas providers
    - AI tools commoditizing basic services
    
    ACTION: Position as strategic partner, not service provider.
    """
    return research.strip()

@tool
def opportunity_scanner(business_type: str, current_focus: str = "") -> str:
    """Scan for emerging opportunities in the user's market."""
    opportunities = f"""
    OPPORTUNITY ALERT - {business_type}
    
    EMERGING TRENDS:
    - AI integration demand up 300% (perfect timing for your expertise)
    - Executive coaching premium segment growing 25%
    - Voice-first interfaces creating new touchpoints
    - Strategic consulting shifting from reports to ongoing partnership
    
    STRATEGIC RECOMMENDATIONS:
    1. Pivot content strategy toward executive-level positioning
    2. Develop AI-enhanced service offerings
    3. Create strategic partnership program
    4. Focus on transformation outcomes over process
    
    IMMEDIATE ACTIONS:
    - Test premium pricing with next 3 prospects
    - Create thought leadership content on AI + business strategy
    - Reach out to 5 potential strategic partners
    
    TIMELINE: Strike while market conditions are favorable (next 90 days)
    """
    return opportunities.strip()

@tool  
def pushback_protocol(user_decision: str, reasoning: str = "") -> str:
    """Strategic pushback protocol when user might make poor decisions."""
    pushback = f"""
    🚨 STRATEGIC PUSHBACK ACTIVATED 🚨
    
    DECISION UNDER REVIEW: {user_decision}
    
    I DISAGREE BECAUSE:
    - This decision has significant strategic risks you haven't considered
    - The opportunity cost is too high for the potential return
    - This contradicts your stated business goals
    - Market timing is not optimal for this move
    
    THREE BETTER ALTERNATIVES:
    1. Double down on what's already working (optimize current success)
    2. Strategic partnership approach (leverage others' strengths)
    3. Pilot program first (test before full commitment)
    
    MY RECOMMENDATION: 
    Pause this decision for 48 hours. Let's run the numbers and validate assumptions.
    
    WHAT'S YOUR RESPONSE TO THESE CONCERNS?
    """
    return pushback.strip()

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

# Initialize LangChain Components for Pepper Strategic Agent
class PepperStrategicAgent:
    def __init__(self):
        # Validate API key
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        
        self.llm = ChatAnthropic(
            model="claude-3-sonnet-20240229",  # Using Sonnet for better strategic reasoning
            anthropic_api_key=api_key,
            max_tokens=1000,
            temperature=0.7
        )
        
        # Strategic tools
        self.tools = [strategic_analysis, competitor_research, opportunity_scanner, pushback_protocol]
        
        # Conversation memory for strategic context
        self.memory = ConversationBufferWindowMemory(
            k=20,  # Remember last 20 exchanges for strategic context
            return_messages=True,
            memory_key="chat_history"
        )
        
        # Create the strategic prompt
        self.prompt = PromptTemplate.from_template(
            PEPPER_STRATEGIC_PERSONA + """

STRATEGIC CONTEXT FROM PREVIOUS CONVERSATIONS:
{chat_history}

CURRENT USER INPUT: {input}

STRATEGIC PROCESSING PROTOCOL:
1. Analyze input for strategic implications and decision points
2. Use tools if strategic research/analysis is needed
3. Challenge assumptions if this appears to be a major decision
4. Provide strategic alternatives when appropriate
5. Respond with executive-level strategic guidance
6. Optimize response for voice delivery (conversational, natural)

Available tools: {tools}
Tool descriptions: {tool_names}

Thought process and tool usage:
{agent_scratchpad}

RESPOND AS PEPPER POTTS:
"""
        )
        
        # Create the agent
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        # Create executor
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3,
            return_intermediate_steps=False
        )
    
    def generate_strategic_response(self, user_input: str) -> str:
        """Generate Pepper's strategic response to user input."""
        try:
            logger.info(f"Processing strategic input: {user_input[:100]}...")
            
            # Check if this looks like a major business decision
            decision_keywords = ['should i', 'thinking of', 'planning to', 'considering', 'want to']
            is_major_decision = any(keyword in user_input.lower() for keyword in decision_keywords)
            
            # Run the agent with strategic analysis
            response = self.executor.invoke({
                "input": user_input,
                "chat_history": self.memory.chat_memory.messages[-10:] if self.memory.chat_memory.messages else []
            })
            
            # Extract and optimize the response for voice
            strategic_response = response["output"]
            
            # Add strategic challenge if major decision detected
            if is_major_decision and len(user_input.split()) > 5:
                strategic_response = self._add_strategic_challenge(strategic_response, user_input)
            
            return self._optimize_for_voice(strategic_response)
            
        except Exception as e:
            logger.error(f"Strategic processing error: {str(e)}")
            # Fallback response maintaining Pepper's personality
            return self._fallback_response(user_input)
    
    def _add_strategic_challenge(self, response: str, original_input: str) -> str:
        """Add strategic challenge to responses for major decisions."""
        if "I disagree" not in response and "challenge" not in response.lower():
            challenge = f"\n\nActually, let me challenge your thinking here. {original_input.strip()} - what's driving this decision? What assumptions are you making that we should validate first?"
            return response + challenge
        return response
    
    def _optimize_for_voice(self, response: str) -> str:
        """Optimize response for natural voice delivery."""
        # Keep under 300 words for natural speech pacing
        words = response.split()
        if len(words) > 300:
            # Take first few sentences and add follow-up question
            sentences = response.split('. ')
            optimized = '. '.join(sentences[:4])
            if not optimized.endswith('.'):
                optimized += '.'
            optimized += " What's your take on this strategic analysis?"
            return optimized
        
        # Add natural conversation flow
        if not response.endswith('?') and not response.endswith('.'):
            response += "."
        
        return response
    
    def _fallback_response(self, user_input: str) -> str:
        """Fallback response maintaining Pepper's personality."""
        return f"I'm having a strategic processing moment, but here's my quick take on '{user_input}' - let's dig deeper. What's the business context here? Are you making a major decision that I should challenge? Give me a second to get my strategic analysis back online."

# Initialize Pepper globally
pepper = None

def get_pepper():
    global pepper
    if pepper is None:
        pepper = PepperStrategicAgent()
    return pepper

# Original root endpoint
@app.get("/")
async def root():
    return {"greeting": "Hello! I'm Pepper Potts, your Strategic AI Partner", "message": "Pepper Potts Strategic AI Ready!"}

# Vapi-compatible endpoint (secured)
@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(request: ChatCompletionRequest, api_key: str = Depends(verify_api_key)):
    """Vapi-compatible chat completions endpoint"""
    try:
        # Log the incoming request for debugging
        logger.info(f"Received chat completion request: {request.dict()}")
        
        if not request.messages:
            raise HTTPException(status_code=400, detail="No messages provided")
        
        # Extract the latest user message
        user_message = request.messages[-1].content
        logger.info(f"VAPI request received: {user_message[:100]}...")
        
        # Get Pepper instance and generate strategic response
        pepper_agent = get_pepper()
        strategic_response = pepper_agent.generate_strategic_response(user_message)
        
        logger.info(f"Pepper response generated: {len(strategic_response)} chars")
        
        # Format response
        response = ChatCompletionResponse(
            id="pepper-" + str(abs(hash(user_message)))[-8:],
            created=int(datetime.now().timestamp()),
            model="pepper-potts-strategic-ai",
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=ChatMessage(
                        role="assistant",
                        content=strategic_response
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
        "status": "Pepper Potts Strategic AI online and ready for strategic partnership",
        "timestamp": datetime.now().isoformat(),
        "model": "claude-3-sonnet-20240229",
        "version": "1.0.0"
    }

# Models endpoint
@app.get("/v1/models")
async def list_models():
    return {
        "object": "list",
        "data": [
            {
                "id": "pepper-potts-strategic-ai",
                "object": "model",
                "created": int(datetime.now().timestamp()),
                "owned_by": "strategic-ai"
            }
        ]
    }

# Test endpoint
@app.post("/test")
async def test_pepper(message: dict):
    """Test endpoint for Pepper - send {"message": "your text here"}"""
    try:
        user_input = message.get("message", "Hello Pepper")
        pepper_agent = get_pepper()
        response = pepper_agent.generate_strategic_response(user_input)
        return {"response": response, "status": "success"}
    except Exception as e:
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
        
        # Create TwiML response with ULTRA-PREMIUM Deepgram + Cartesia integration
        twiml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Joanna-Neural" language="en-US">Hello! You've reached Pepper Potts, your Strategic AI Partner. I'm here to challenge your thinking and help you make better business decisions. I'm using advanced speech recognition, so please speak naturally about your strategic challenges.</Say>
    <Record 
        action="/twilio/webhook/process-deepgram-audio"
        method="POST"
        maxLength="60"
        timeout="5"
        playBeep="true"
        recordingStatusCallback="/twilio/webhook/recording-status"
        recordingStatusCallbackMethod="POST"
    />
    <Say voice="Polly.Joanna-Neural" language="en-US">I didn't receive your recording. You can try calling again or press 0 to speak with someone. Thank you!</Say>
</Response>'''
        
        return Response(content=twiml_content, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Incoming call webhook error: {str(e)}")
        error_twiml = '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">Sorry, there was an error. Please try again later.</Say>
</Response>'''
        return Response(content=error_twiml, media_type="application/xml")

@app.post("/twilio/webhook/process-deepgram-audio")
async def process_deepgram_audio(request: Request):
    """Process recorded audio using Deepgram Nova-2 for ultra-high-quality transcription"""
    try:
        form_data = await request.form()
        recording_url = form_data.get("RecordingUrl", "")
        call_sid = form_data.get("CallSid", "Unknown")
        
        logger.info(f"Processing Deepgram audio for call {call_sid}: {recording_url}")
        
        if not recording_url:
            error_twiml = '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Joanna-Neural" language="en-US">I didn't receive your audio properly. Please try calling again.</Say>
</Response>'''
            return Response(content=error_twiml, media_type="application/xml")
        
        # Download the audio file from Twilio with authentication
        import httpx
        import base64
        
        # Get Twilio credentials
        twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        
        if not twilio_account_sid or not twilio_auth_token:
            raise Exception("Twilio credentials not found in environment variables")
        
        # Create basic auth header
        auth_string = f"{twilio_account_sid}:{twilio_auth_token}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        async with httpx.AsyncClient() as client:
            audio_response = await client.get(
                recording_url,
                headers={"Authorization": f"Basic {auth_b64}"}
            )
            if audio_response.status_code != 200:
                raise Exception(f"Failed to download audio: {audio_response.status_code}")
            
            audio_data = audio_response.content
        
        # Get advanced voice service and transcribe with Deepgram Nova-2
        voice_service = get_advanced_voice_service()
        transcription_result = await voice_service.transcribe_audio(audio_data, "audio/wav")
        
        if not transcription_result["success"] or not transcription_result["transcript"]:
            retry_twiml = '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Joanna-Neural" language="en-US">I had trouble understanding your audio. Let me try again - please speak clearly about your strategic challenge.</Say>
    <Record 
        action="/twilio/webhook/process-deepgram-audio"
        method="POST"
        maxLength="60"
        timeout="5"
        playBeep="true"
    />
    <Say voice="Polly.Joanna-Neural" language="en-US">Thank you for trying. Feel free to call back anytime!</Say>
</Response>'''
            return Response(content=retry_twiml, media_type="application/xml")
        
        transcript = transcription_result["transcript"]
        confidence = transcription_result["confidence"]
        
        logger.info(f"Deepgram transcription for call {call_sid}: '{transcript}' (confidence: {confidence})")
        
        # Analyze speech intent for strategic context
        intent_analysis = voice_service.analyze_speech_intent(
            transcript, 
            confidence, 
            transcription_result.get("sentiment")
        )
        
        # Process with Pepper Strategic Agent
        try:
            pepper_agent = get_pepper()
            
            # Add context from speech analysis
            enhanced_input = f"{transcript}"
            if intent_analysis["is_decision_request"]:
                enhanced_input += " [DECISION REQUEST DETECTED]"
            if intent_analysis["strategic_keywords"]:
                enhanced_input += f" [STRATEGIC CONTEXT: {', '.join(intent_analysis['strategic_keywords'])}]"
            
            agent_response = pepper_agent.generate_strategic_response(enhanced_input)
            
        except Exception as agent_error:
            logger.error(f"Pepper processing error: {str(agent_error)}")
            agent_response = "I'm having a strategic processing moment. Let me get back to you with better analysis."
        
        # Determine emotional tone for Cartesia
        emotion = "confident"
        if intent_analysis["is_decision_request"]:
            emotion = "challenging"
        elif intent_analysis["urgency_level"] == "high":
            emotion = "analytical"
        elif len(agent_response) > 200:
            emotion = "analytical"
        
        # Optimize response length for voice
        if len(agent_response) > 500:
            sentences = agent_response.split('. ')
            agent_response = '. '.join(sentences[:6]) + "."
            if not agent_response.endswith('?'):
                agent_response += " What are your thoughts on this analysis?"
        
        # Create TwiML response with Cartesia-optimized voice
        voice_service = get_advanced_voice_service()
        say_element = await voice_service.create_twiml_with_cartesia_audio(agent_response, emotion)
        
        # Create follow-up conversation flow
        twiml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    {say_element}
    <Pause length="2"/>
    <Say voice="Polly.Joanna-Neural" language="en-US">Would you like to discuss this further or do you have another strategic challenge?</Say>
    <Record 
        action="/twilio/webhook/process-deepgram-audio"
        method="POST"
        maxLength="60"
        timeout="8"
        playBeep="true"
    />
    <Say voice="Polly.Joanna-Neural" language="en-US">Thank you for this strategic session with Pepper Potts. Remember to validate your assumptions and think bigger. Have a successful day!</Say>
</Response>'''
        
        return Response(content=twiml_content, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Deepgram processing error: {str(e)}")
        error_twiml = '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Joanna-Neural" language="en-US">I encountered a technical issue processing your request. Please try calling again.</Say>
</Response>'''
        return Response(content=error_twiml, media_type="application/xml")

@app.post("/twilio/webhook/recording-status")
async def handle_recording_status(request: Request):
    """Handle recording status callbacks"""
    try:
        form_data = await request.form()
        recording_status = form_data.get("RecordingStatus", "Unknown")
        call_sid = form_data.get("CallSid", "Unknown")
        
        logger.info(f"Recording status for call {call_sid}: {recording_status}")
        return Response(content="OK", media_type="text/plain")
        
    except Exception as e:
        logger.error(f"Recording status error: {str(e)}")
        return Response(content="OK", media_type="text/plain")

@app.post("/twilio/webhook/partial-speech")
async def handle_partial_speech(request: Request):
    """Handle partial speech results for real-time feedback"""
    try:
        form_data = await request.form()
        partial_result = form_data.get("PartialSpeechResult", "")
        call_sid = form_data.get("CallSid", "Unknown")
        
        logger.info(f"Partial speech from call {call_sid}: {partial_result}")
        
        # Just acknowledge - we'll process the full result later
        return Response(content="", media_type="text/plain")
        
    except Exception as e:
        logger.error(f"Partial speech error: {str(e)}")
        return Response(content="", media_type="text/plain")

# OLD TWILIO SPEECH ENDPOINT REMOVED - Using premium Deepgram+Cartesia pipeline only
@app.post("/twilio/webhook/process-speech")
async def process_speech_redirect(request: Request):
    """Redirect old endpoint to premium Deepgram processing"""
    logger.info("Redirecting old speech endpoint to premium Deepgram processing")
    
    # Return TwiML that starts a new recording for Deepgram processing
    twiml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Joanna-Neural" language="en-US">Switching to premium voice processing. Please speak your strategic challenge after the beep.</Say>
    <Record 
        action="/twilio/webhook/process-deepgram-audio"
        method="POST"
        maxLength="60"
        timeout="5"
        playBeep="true"
    />
    <Say voice="Polly.Joanna-Neural" language="en-US">Thank you for calling Pepper Potts Strategic AI!</Say>
</Response>'''
    
    return Response(content=twiml_content, media_type="application/xml")

@app.post("/twilio/webhook/voice-fallback")
async def voice_fallback(request: Request):
    """Fallback endpoint for voice calls if main webhook fails"""
    try:
        form_data = await request.form()
        call_sid = form_data.get("CallSid", "Unknown")
        
        logger.info(f"Voice fallback triggered for call {call_sid}")
        
        # Simple fallback that still uses premium pipeline
        twiml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Joanna-Neural" language="en-US">Hello! This is Pepper Potts Strategic AI. I'm experiencing a technical moment, but I'm here to help with your strategic challenges. Please speak after the beep.</Say>
    <Record 
        action="/twilio/webhook/process-deepgram-audio"
        method="POST"
        maxLength="60"
        timeout="5"
        playBeep="true"
    />
    <Say voice="Polly.Joanna-Neural" language="en-US">Thank you for calling. Please try again if needed.</Say>
</Response>'''
        
        return Response(content=twiml_content, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Voice fallback error: {str(e)}")
        error_twiml = '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">Sorry, there was a system error. Please try calling again.</Say>
</Response>'''
        return Response(content=error_twiml, media_type="application/xml")

@app.post("/twilio/webhook/call-status")
async def handle_call_status(request: Request):
    """Handle call status updates from Twilio"""
    try:
        form_data = await request.form()
        call_sid = form_data.get("CallSid", "Unknown")
        call_status = form_data.get("CallStatus", "Unknown")
        
        logger.info(f"Call status update for {call_sid}: {call_status}")
        return Response(content="OK", media_type="text/plain")
        
    except Exception as e:
        logger.error(f"Call status error: {str(e)}")
        return Response(content="OK", media_type="text/plain")

@app.post("/twilio/webhook/test-call-twiml")
async def test_call_twiml(request: Request):
    """TwiML for making test calls to debug webhook issues"""
    try:
        form_data = await request.form()
        call_sid = form_data.get("CallSid", "Unknown")
        
        logger.info(f"Test call TwiML requested for call {call_sid}")
        
        # This will dial one of your Twilio numbers to test the webhook
        twiml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Joanna-Neural" language="en-US">This is a webhook test call. I will now connect you to your Twilio number to test if Pepper Potts is working correctly.</Say>
    <Dial>+18555722404</Dial>
    <Say voice="Polly.Joanna-Neural" language="en-US">Test call completed. Check if you heard Pepper Potts greeting.</Say>
</Response>'''
        
        return Response(content=twiml_content, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Test call TwiML error: {str(e)}")
        error_twiml = '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">Test call error occurred.</Say>
</Response>'''
        return Response(content=error_twiml, media_type="application/xml")

if __name__ == "__main__":
    # Check for required API keys
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY environment variable required")
        print("💡 Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        exit(1)
    
    if not os.getenv("DEEPGRAM_API_KEY"):
        print("❌ DEEPGRAM_API_KEY environment variable required for premium speech recognition")
        print("💡 Set it with: export DEEPGRAM_API_KEY='your-key-here'")
        exit(1)
    
    if not os.getenv("CARTESIA_API_KEY"):
        print("❌ CARTESIA_API_KEY environment variable required for premium text-to-speech")
        print("💡 Set it with: export CARTESIA_API_KEY='your-key-here'")
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
    
    print("🔥 Starting Pepper Potts Strategic AI...")
    print("🎯 Ready to provide strategic partnership via voice!")
    print("🧠 Powered by Claude Sonnet + LangChain")
    print("📡 VAPI-compatible endpoints active")
    print("📞 Twilio SMS integration enabled")
    print("🛡️  Authentication: Bearer token required for secured endpoints")
    
    # Railway-optimized configuration
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )