"""
Advanced Voice Service using Deepgram + Cartesia
Ultra-high-quality speech-to-text and text-to-speech for Pepper Potts
"""

import os
import asyncio
import json
import base64
from typing import Optional, Dict, Any
import logging
from deepgram import DeepgramClient, PrerecordedOptions, LiveOptions
from cartesia import Cartesia
import aiofiles
import tempfile

logger = logging.getLogger(__name__)

class AdvancedVoiceService:
    def __init__(self):
        # Initialize Deepgram client
        self.deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")
        if not self.deepgram_api_key:
            raise ValueError("DEEPGRAM_API_KEY environment variable required")
        
        self.deepgram = DeepgramClient(self.deepgram_api_key)
        
        # Initialize Cartesia client
        self.cartesia_api_key = os.getenv("CARTESIA_API_KEY")
        if not self.cartesia_api_key:
            raise ValueError("CARTESIA_API_KEY environment variable required")
        
        self.cartesia = Cartesia(api_key=self.cartesia_api_key)
        
        # Pepper's voice configuration
        self.pepper_voice_config = {
            "model_id": "sonic-english",
            "voice": {
                "mode": "id",
                "id": "a0e99841-438c-4a64-b679-ae501e7d6091"  # Confident female voice
            },
            "output_format": {
                "container": "wav",
                "encoding": "pcm_s16le",
                "sample_rate": 8000  # Optimized for phone calls
            }
        }
        
        # Business vocabulary for better recognition
        self.business_keywords = [
            "strategy", "strategic", "business", "marketing", "pricing", "competition", 
            "revenue", "growth", "decision", "planning", "consulting", "coaching",
            "ADHD", "entrepreneur", "solopreneur", "challenge", "opportunity", "risk",
            "analysis", "ROI", "KPI", "metrics", "conversion", "funnel", "acquisition",
            "retention", "churn", "pivot", "scale", "optimize", "monetize", "validate"
        ]
    
    async def transcribe_audio(self, audio_data: bytes, content_type: str = "audio/wav") -> Dict[str, Any]:
        """
        Transcribe audio using Deepgram Nova-2 with business vocabulary
        """
        try:
            # Configure Deepgram for business conversations
            options = PrerecordedOptions(
                model="nova-2",
                language="en-US",
                smart_format=True,
                punctuate=True,
                diarize=False,
                keywords=self.business_keywords,
                interim_results=False,
                endpointing=300,  # 5 seconds of silence
                utterances=True,
                confidence=True,
                sentiment=True,
                topics=True
            )
            
            # Create payload
            payload = {"buffer": audio_data}
            
            # Transcribe
            response = await self.deepgram.listen.asyncprerecorded.v("1").transcribe_file(
                payload, options
            )
            
            # Extract results
            if response.results and response.results.channels:
                channel = response.results.channels[0]
                if channel.alternatives:
                    alternative = channel.alternatives[0]
                    
                    return {
                        "transcript": alternative.transcript,
                        "confidence": alternative.confidence,
                        "words": alternative.words if hasattr(alternative, 'words') else [],
                        "sentiment": response.results.sentiment if hasattr(response.results, 'sentiment') else None,
                        "topics": response.results.topics if hasattr(response.results, 'topics') else None,
                        "success": True
                    }
            
            return {
                "transcript": "",
                "confidence": 0.0,
                "success": False,
                "error": "No transcription results"
            }
            
        except Exception as e:
            logger.error(f"Deepgram transcription error: {str(e)}")
            return {
                "transcript": "",
                "confidence": 0.0,
                "success": False,
                "error": str(e)
            }
    
    async def generate_speech(self, text: str, emotion: str = "confident") -> Optional[bytes]:
        """
        Generate speech using Cartesia with Pepper's strategic voice
        """
        try:
            # Adjust voice parameters based on emotion/context
            voice_config = self.pepper_voice_config.copy()
            
            # Emotional control for strategic responses
            if emotion == "challenging":
                voice_config["voice"]["__experimental_controls"] = {
                    "speed": "normal",
                    "emotion": ["assertive", "confident"]
                }
            elif emotion == "analytical":
                voice_config["voice"]["__experimental_controls"] = {
                    "speed": "slightly_slow",
                    "emotion": ["thoughtful", "professional"]
                }
            elif emotion == "encouraging":
                voice_config["voice"]["__experimental_controls"] = {
                    "speed": "normal",
                    "emotion": ["warm", "supportive"]
                }
            
            # Generate speech
            response = await self.cartesia.tts.sse(
                model_id=voice_config["model_id"],
                transcript=text,
                voice=voice_config["voice"],
                output_format=voice_config["output_format"]
            )
            
            # Collect audio chunks
            audio_chunks = []
            async for chunk in response:
                if chunk.get("data"):
                    audio_chunks.append(base64.b64decode(chunk["data"]))
            
            if audio_chunks:
                return b''.join(audio_chunks)
            
            return None
            
        except Exception as e:
            logger.error(f"Cartesia TTS error: {str(e)}")
            return None
    
    async def create_twiml_with_cartesia_audio(self, text: str, emotion: str = "confident") -> str:
        """
        Create TwiML that plays Cartesia-generated audio
        """
        try:
            # Generate audio
            audio_data = await self.generate_speech(text, emotion)
            
            if not audio_data:
                # Fallback to regular TwiML Say
                return f'<Say voice="Polly.Joanna-Neural" language="en-US">{text}</Say>'
            
            # Save audio to temporary file (in production, use cloud storage)
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            async with aiofiles.open(temp_file.name, 'wb') as f:
                await f.write(audio_data)
            
            # For now, return regular Say - in production you'd upload to S3/CDN
            # and use <Play> verb with the URL
            return f'<Say voice="Polly.Joanna-Neural" language="en-US">{text}</Say>'
            
        except Exception as e:
            logger.error(f"TwiML audio creation error: {str(e)}")
            return f'<Say voice="Polly.Joanna-Neural" language="en-US">{text}</Say>'
    
    def analyze_speech_intent(self, transcript: str, confidence: float, sentiment: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze speech for strategic context and intent
        """
        intent_analysis = {
            "is_business_question": False,
            "is_decision_request": False,
            "urgency_level": "normal",
            "strategic_keywords": [],
            "confidence_level": "high" if confidence > 0.8 else "medium" if confidence > 0.5 else "low"
        }
        
        # Check for business-related content
        business_indicators = ["business", "strategy", "marketing", "pricing", "revenue", "growth", "decision"]
        decision_indicators = ["should i", "thinking of", "planning to", "considering", "what do you think"]
        
        transcript_lower = transcript.lower()
        
        # Detect business questions
        if any(indicator in transcript_lower for indicator in business_indicators):
            intent_analysis["is_business_question"] = True
        
        # Detect decision requests
        if any(indicator in transcript_lower for indicator in decision_indicators):
            intent_analysis["is_decision_request"] = True
        
        # Extract strategic keywords
        found_keywords = [keyword for keyword in self.business_keywords if keyword.lower() in transcript_lower]
        intent_analysis["strategic_keywords"] = found_keywords
        
        # Determine urgency from sentiment and keywords
        urgent_keywords = ["urgent", "asap", "immediately", "crisis", "problem", "issue"]
        if any(keyword in transcript_lower for keyword in urgent_keywords):
            intent_analysis["urgency_level"] = "high"
        
        # Add sentiment analysis if available
        if sentiment:
            intent_analysis["sentiment"] = sentiment
        
        return intent_analysis

# Global instance
advanced_voice = None

def get_advanced_voice_service():
    global advanced_voice
    if advanced_voice is None:
        advanced_voice = AdvancedVoiceService()
    return advanced_voice
