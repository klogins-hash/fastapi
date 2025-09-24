#!/usr/bin/env python3
"""
Pepper Potts Strategic AI with Cartesia Ultra-High-Quality Voice
Clean implementation with fast authoritative voice
"""

import os
import asyncio
import base64
import wave
import tempfile
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from cartesia import Cartesia
import logging
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set API keys
os.environ["CARTESIA_API_KEY"] = "sk_car_9fM7KFZEfqeEfiETkHXwaH"
os.environ["DEEPGRAM_API_KEY"] = "ddb9ee2b7a152c9b9c87fd77c6958f33db430697"

# Global Cartesia client
cartesia_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global cartesia_client
    cartesia_client = Cartesia(api_key=os.getenv("CARTESIA_API_KEY"))
    logger.info("🎤 Cartesia client initialized")
    yield
    # Shutdown
    logger.info("🛑 Shutting down Pepper Cartesia AI")

# Initialize FastAPI with lifespan
app = FastAPI(
    title="Pepper Potts Strategic AI",
    description="Ultra-high-quality voice AI with Cartesia",
    version="2.0.0",
    lifespan=lifespan
)

# Pepper Potts configuration
PEPPER_CONFIG = {
    "voice_id": "79a125e8-cd45-4c13-8a67-188112f4dd22",  # Authoritative female
    "model_id": "sonic-2-2025-03-07",  # Supports speed controls
    "speed": "fast",  # Your preferred speed
    "sample_rate": 44100,
    "encoding": "pcm_f32le"
}

def get_pepper_agent():
    """Get Pepper Potts strategic agent (simplified for demo)"""
    class PepperAgent:
        def generate_strategic_response(self, user_input: str) -> str:
            # Simplified strategic responses
            responses = [
                f"Actually, let me challenge your thinking on '{user_input}'. Here are three strategic alternatives you should consider instead.",
                f"I disagree with that approach to '{user_input}'. You're thinking too small - here's how successful companies handle this differently.",
                f"Before you decide on '{user_input}', let's analyze the strategic implications and opportunity costs you haven't considered.",
                f"That's a tactical move, not strategic. For '{user_input}', here's what will actually move the needle for your business.",
                f"Listen, '{user_input}' has serious risks. Let me give you a better framework for making this decision."
            ]
            import random
            return random.choice(responses)
    
    return PepperAgent()

async def generate_pepper_voice(text: str) -> bytes:
    """Generate Pepper's voice using Cartesia with fast authoritative settings"""
    try:
        logger.info(f"🗣️ Generating Pepper voice for: {text[:50]}...")
        
        # Generate speech with Cartesia
        response = cartesia_client.tts.sse(
            model_id=PEPPER_CONFIG["model_id"],
            transcript=text,
            voice={
                "id": PEPPER_CONFIG["voice_id"],
                "experimental_controls": {
                    "speed": PEPPER_CONFIG["speed"],
                    "emotion": []
                }
            },
            output_format={
                "container": "raw",
                "encoding": PEPPER_CONFIG["encoding"],
                "sample_rate": PEPPER_CONFIG["sample_rate"]
            },
            language="en"
        )
        
        # Collect audio chunks
        audio_chunks = []
        chunk_count = 0
        
        for chunk in response:
            if hasattr(chunk, 'data') and chunk.data:
                audio_chunks.append(base64.b64decode(chunk.data))
                chunk_count += 1
        
        if audio_chunks:
            audio_data = b''.join(audio_chunks)
            logger.info(f"✅ Generated {len(audio_data)} bytes of audio in {chunk_count} chunks")
            return audio_data
        else:
            raise Exception("No audio data generated")
            
    except Exception as e:
        logger.error(f"❌ Cartesia voice generation error: {str(e)}")
        raise

def convert_to_wav(raw_audio: bytes) -> bytes:
    """Convert raw PCM audio to WAV format"""
    with tempfile.NamedTemporaryFile() as temp_file:
        with wave.open(temp_file.name, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(4)  # 32-bit float (pcm_f32le)
            wav_file.setframerate(PEPPER_CONFIG["sample_rate"])
            wav_file.writeframes(raw_audio)
        
        temp_file.seek(0)
        return temp_file.read()

@app.get("/", response_class=HTMLResponse)
async def home():
    """Simple web interface for Pepper Potts"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Pepper Potts Strategic AI</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 800px; margin: 0 auto; padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; min-height: 100vh;
            }
            .container { background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; backdrop-filter: blur(10px); }
            h1 { text-align: center; margin-bottom: 30px; font-size: 2.5em; }
            .input-group { margin: 20px 0; }
            label { display: block; margin-bottom: 10px; font-weight: bold; }
            input[type="text"] { 
                width: 100%; padding: 15px; border: none; border-radius: 8px;
                font-size: 16px; background: rgba(255,255,255,0.9);
            }
            button { 
                background: #ff6b6b; color: white; border: none; padding: 15px 30px;
                border-radius: 8px; font-size: 16px; cursor: pointer; margin: 10px 5px;
                transition: background 0.3s;
            }
            button:hover { background: #ff5252; }
            button:disabled { background: #ccc; cursor: not-allowed; }
            .response { 
                margin: 20px 0; padding: 20px; background: rgba(255,255,255,0.2);
                border-radius: 8px; min-height: 100px;
            }
            .loading { text-align: center; font-style: italic; }
            audio { width: 100%; margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎯 Pepper Potts Strategic AI</h1>
            <p style="text-align: center; font-size: 1.2em; margin-bottom: 30px;">
                Ultra-high-quality voice AI for strategic business guidance
            </p>
            
            <div class="input-group">
                <label for="challenge">What's your strategic challenge or business question?</label>
                <input type="text" id="challenge" placeholder="e.g., Should I raise prices or focus on volume?" />
            </div>
            
            <div style="text-align: center;">
                <button onclick="askPepper()" id="askBtn">Ask Pepper Potts</button>
                <button onclick="testVoice()" id="testBtn">Test Voice Quality</button>
            </div>
            
            <div id="response" class="response" style="display: none;">
                <h3>Pepper's Strategic Response:</h3>
                <p id="responseText"></p>
                <audio id="audioPlayer" controls style="display: none;"></audio>
            </div>
        </div>

        <script>
            async function askPepper() {
                const challenge = document.getElementById('challenge').value.trim();
                if (!challenge) {
                    alert('Please enter a strategic challenge or business question.');
                    return;
                }
                
                const askBtn = document.getElementById('askBtn');
                const responseDiv = document.getElementById('response');
                const responseText = document.getElementById('responseText');
                const audioPlayer = document.getElementById('audioPlayer');
                
                askBtn.disabled = true;
                askBtn.textContent = 'Pepper is thinking...';
                responseDiv.style.display = 'block';
                responseText.innerHTML = '<div class="loading">🧠 Analyzing your strategic challenge...</div>';
                audioPlayer.style.display = 'none';
                
                try {
                    const response = await fetch('/ask-pepper', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ challenge: challenge })
                    });
                    
                    if (response.ok) {
                        const result = await response.json();
                        responseText.textContent = result.response;
                        
                        if (result.audio_url) {
                            audioPlayer.src = result.audio_url;
                            audioPlayer.style.display = 'block';
                            audioPlayer.play();
                        }
                    } else {
                        responseText.textContent = 'Sorry, I encountered a technical issue. Please try again.';
                    }
                } catch (error) {
                    responseText.textContent = 'Network error. Please check your connection and try again.';
                }
                
                askBtn.disabled = false;
                askBtn.textContent = 'Ask Pepper Potts';
            }
            
            async function testVoice() {
                const testBtn = document.getElementById('testBtn');
                const responseDiv = document.getElementById('response');
                const responseText = document.getElementById('responseText');
                const audioPlayer = document.getElementById('audioPlayer');
                
                testBtn.disabled = true;
                testBtn.textContent = 'Generating voice...';
                responseDiv.style.display = 'block';
                responseText.innerHTML = '<div class="loading">🎤 Generating ultra-high-quality voice sample...</div>';
                
                try {
                    const response = await fetch('/test-voice');
                    
                    if (response.ok) {
                        const result = await response.json();
                        responseText.textContent = result.text;
                        
                        if (result.audio_url) {
                            audioPlayer.src = result.audio_url;
                            audioPlayer.style.display = 'block';
                            audioPlayer.play();
                        }
                    } else {
                        responseText.textContent = 'Voice test failed. Please try again.';
                    }
                } catch (error) {
                    responseText.textContent = 'Network error. Please try again.';
                }
                
                testBtn.disabled = false;
                testBtn.textContent = 'Test Voice Quality';
            }
            
            // Allow Enter key to submit
            document.getElementById('challenge').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    askPepper();
                }
            });
        </script>
    </body>
    </html>
    """
    return html_content

@app.post("/ask-pepper")
async def ask_pepper(request: Request):
    """Process strategic challenge and return Pepper's response with voice"""
    try:
        data = await request.json()
        challenge = data.get("challenge", "").strip()
        
        if not challenge:
            raise HTTPException(status_code=400, detail="Challenge is required")
        
        logger.info(f"📝 Processing challenge: {challenge}")
        
        # Get Pepper's strategic response
        pepper_agent = get_pepper_agent()
        strategic_response = pepper_agent.generate_strategic_response(challenge)
        
        # Generate voice
        audio_data = await generate_pepper_voice(strategic_response)
        wav_data = convert_to_wav(audio_data)
        
        # Save audio file
        audio_filename = f"pepper_response_{hash(challenge) % 10000}.wav"
        audio_path = f"/tmp/{audio_filename}"
        
        with open(audio_path, 'wb') as f:
            f.write(wav_data)
        
        return {
            "response": strategic_response,
            "audio_url": f"/audio/{audio_filename}",
            "voice_config": {
                "voice": "Authoritative Female",
                "speed": "Fast",
                "quality": "Ultra-High (44kHz)"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Ask Pepper error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Strategic processing error: {str(e)}")

@app.get("/test-voice")
async def test_voice():
    """Test Pepper's voice quality"""
    try:
        test_text = "Listen, I'm going to be direct with you. That decision has serious strategic risks you haven't considered. The opportunity cost is too high, and frankly, you're thinking too small. Let me give you three alternatives that will actually move the needle for your business."
        
        # Generate voice
        audio_data = await generate_pepper_voice(test_text)
        wav_data = convert_to_wav(audio_data)
        
        # Save audio file
        audio_filename = "pepper_voice_test.wav"
        audio_path = f"/tmp/{audio_filename}"
        
        with open(audio_path, 'wb') as f:
            f.write(wav_data)
        
        return {
            "text": test_text,
            "audio_url": f"/audio/{audio_filename}",
            "info": "Ultra-high-quality Cartesia voice - Authoritative Female at Fast speed"
        }
        
    except Exception as e:
        logger.error(f"❌ Voice test error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Voice test error: {str(e)}")

@app.get("/audio/{filename}")
async def get_audio(filename: str):
    """Serve audio files"""
    audio_path = f"/tmp/{filename}"
    if os.path.exists(audio_path):
        return FileResponse(
            audio_path, 
            media_type="audio/wav",
            headers={"Cache-Control": "max-age=3600"}
        )
    else:
        raise HTTPException(status_code=404, detail="Audio file not found")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "Pepper Potts Strategic AI with Cartesia Ultra-High-Quality Voice",
        "voice_config": PEPPER_CONFIG,
        "timestamp": "2025-09-24T13:18:00Z",
        "version": "2.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    
    # Check for required API keys
    if not os.getenv("CARTESIA_API_KEY"):
        print("❌ CARTESIA_API_KEY environment variable required")
        exit(1)
    
    print("🚀 Starting Pepper Potts Strategic AI with Cartesia")
    print("🎤 Voice: Authoritative Female (Fast Speed)")
    print("🎯 Ultra-High-Quality Voice Generation")
    print("🌐 Web interface available at http://localhost:8080")
    
    uvicorn.run(app, host="0.0.0.0", port=8080)
