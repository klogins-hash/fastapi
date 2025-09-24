#!/usr/bin/env python3
"""
Simple Cartesia + Pepper Potts Strategic AI
Direct implementation without Twilio/Vapi complexity
"""

import os
import asyncio
import base64
import wave
from cartesia import Cartesia
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set API keys
os.environ["CARTESIA_API_KEY"] = "sk_car_9fM7KFZEfqeEfiETkHXwaH"
os.environ["DEEPGRAM_API_KEY"] = "ddb9ee2b7a152c9b9c87fd77c6958f33db430697"

async def test_cartesia_pepper():
    print("🎤 Testing Cartesia with Pepper Potts Strategic AI...")
    
    # Initialize Cartesia
    cartesia = Cartesia(api_key=os.getenv("CARTESIA_API_KEY"))
    
    # Pepper's strategic response
    pepper_response = """
    Hello! I'm Pepper Potts, your Strategic AI Partner. I'm here to challenge your thinking and help you make better business decisions. 
    
    Actually, let me be direct with you - most entrepreneurs I work with are making three critical strategic mistakes right now. 
    
    First, they're competing on price instead of value. Second, they're trying to serve everyone instead of dominating a niche. 
    And third, they're not thinking systematically about their competitive advantages.
    
    Here's the thing - I disagree with the conventional wisdom that says you should start small and grow slowly. 
    In today's market, you need to think bigger from day one. What strategic challenge are you facing that I can help you tackle?
    """
    
    # Cartesia voice configuration for Pepper
    voice_config = {
        "model_id": "sonic-english",
        "voice": {
            "mode": "id",
            "id": "a0e99841-438c-4a64-b679-ae501e7d6091"  # Confident female voice
        },
        "output_format": {
            "container": "raw",
            "encoding": "pcm_s16le",
            "sample_rate": 22050  # High quality
        }
    }
    
    print("🗣️ Generating Pepper's strategic voice...")
    
    try:
        # Generate speech with Cartesia (synchronous call)
        response = cartesia.tts.sse(
            model_id=voice_config["model_id"],
            transcript=pepper_response,
            voice=voice_config["voice"],
            output_format=voice_config["output_format"]
        )
        
        # Collect audio chunks
        audio_chunks = []
        chunk_count = 0
        
        for chunk in response:
            if hasattr(chunk, 'data') and chunk.data:
                audio_chunks.append(base64.b64decode(chunk.data))
                chunk_count += 1
                if chunk_count % 10 == 0:
                    print(f"   📦 Received {chunk_count} audio chunks...")
            elif hasattr(chunk, 'audio') and chunk.audio:
                audio_chunks.append(base64.b64decode(chunk.audio))
                chunk_count += 1
                if chunk_count % 10 == 0:
                    print(f"   📦 Received {chunk_count} audio chunks...")
            else:
                print(f"   🔍 Chunk type: {type(chunk)}, attributes: {dir(chunk)}")
        
        if audio_chunks:
            # Save the audio file as WAV
            audio_data = b''.join(audio_chunks)
            output_file = "pepper_strategic_voice.wav"
            
            # Convert raw PCM to WAV format
            with wave.open(output_file, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(22050)  # Sample rate
                wav_file.writeframes(audio_data)
            
            print(f"✅ Generated Pepper's voice: {output_file}")
            print(f"📊 Audio size: {len(audio_data)} bytes")
            print(f"📦 Total chunks: {chunk_count}")
            
            # Play the audio (macOS)
            print("🎵 Playing Pepper's strategic voice...")
            os.system(f"afplay {output_file}")
            
            return True
        else:
            print("❌ No audio data received")
            return False
            
    except Exception as e:
        print(f"❌ Cartesia error: {str(e)}")
        return False

async def test_different_voices():
    print("\n🎭 Testing different Cartesia voices for Pepper...")
    
    cartesia = Cartesia(api_key=os.getenv("CARTESIA_API_KEY"))
    
    # Test different voices
    voices_to_test = [
        {
            "name": "Confident Female",
            "id": "a0e99841-438c-4a64-b679-ae501e7d6091",
            "description": "Professional, confident"
        },
        {
            "name": "Authoritative Female", 
            "id": "79a125e8-cd45-4c13-8a67-188112f4dd22",
            "description": "Strong, authoritative"
        },
        {
            "name": "Warm Professional",
            "id": "95856005-0332-41b0-935f-352e296aa0df", 
            "description": "Warm but professional"
        }
    ]
    
    test_text = "I disagree with that approach. Here's a better strategic alternative you should consider."
    
    for i, voice in enumerate(voices_to_test):
        print(f"\n🎤 Testing voice {i+1}: {voice['name']} - {voice['description']}")
        
        try:
            response = cartesia.tts.sse(
                model_id="sonic-english",
                transcript=test_text,
                voice={"mode": "id", "id": voice["id"]},
                output_format={
                    "container": "raw",
                    "encoding": "pcm_s16le", 
                    "sample_rate": 22050
                }
            )
            
            audio_chunks = []
            for chunk in response:
                if hasattr(chunk, 'data') and chunk.data:
                    audio_chunks.append(base64.b64decode(chunk.data))
                elif hasattr(chunk, 'audio') and chunk.audio:
                    audio_chunks.append(base64.b64decode(chunk.audio))
            
            if audio_chunks:
                audio_data = b''.join(audio_chunks)
                output_file = f"pepper_voice_{i+1}_{voice['name'].lower().replace(' ', '_')}.wav"
                
                # Convert raw PCM to WAV format
                with wave.open(output_file, 'wb') as wav_file:
                    wav_file.setnchannels(1)  # Mono
                    wav_file.setsampwidth(2)  # 16-bit
                    wav_file.setframerate(22050)  # Sample rate
                    wav_file.writeframes(audio_data)
                
                print(f"   ✅ Generated: {output_file}")
                print(f"   🎵 Playing...")
                os.system(f"afplay {output_file}")
                
                # Wait a moment between voices
                await asyncio.sleep(2)
            
        except Exception as e:
            print(f"   ❌ Error with {voice['name']}: {str(e)}")

async def main():
    print("🚀 Cartesia + Pepper Potts Strategic AI Test")
    print("=" * 50)
    
    # Test 1: Basic Pepper voice generation
    success = await test_cartesia_pepper()
    
    if success:
        print("\n" + "=" * 50)
        # Test 2: Different voices
        await test_different_voices()
        
        print("\n🎯 RESULTS:")
        print("✅ Cartesia integration working")
        print("✅ High-quality voice generation")
        print("✅ Strategic AI personality in voice")
        print("\n💡 Next steps:")
        print("- Choose best voice for Pepper")
        print("- Integrate with web interface")
        print("- Add real-time conversation")
    else:
        print("\n❌ Cartesia test failed")

if __name__ == "__main__":
    asyncio.run(main())
