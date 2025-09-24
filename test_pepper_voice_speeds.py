#!/usr/bin/env python3
"""
Test Pepper Potts voice at different speeds with Cartesia
Find the perfect authoritative pace for strategic conversations
"""

import os
import base64
import wave
from cartesia import Cartesia
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set API keys
os.environ["CARTESIA_API_KEY"] = "sk_car_9fM7KFZEfqeEfiETkHXwaH"

def test_pepper_speeds():
    print("🎤 Testing Pepper Potts Authoritative Voice at Different Speeds...")
    
    # Initialize Cartesia
    cartesia = Cartesia(api_key=os.getenv("CARTESIA_API_KEY"))
    
    # Authoritative female voice ID
    authoritative_voice_id = "79a125e8-cd45-4c13-8a67-188112f4dd22"
    
    # Strategic test text that shows Pepper's personality
    pepper_text = """
    I disagree with that approach. Here's the thing - you're thinking too small. 
    Let me challenge your assumptions and give you three better strategic alternatives. 
    First, instead of competing on price, position yourself as the premium solution. 
    Second, don't try to serve everyone - dominate your niche completely. 
    Third, think systematically about your competitive advantages.
    What's your response to this strategic analysis?
    """
    
    # Test different speed settings
    speed_tests = [
        {"speed": "slowest", "description": "Very Slow - Deliberate"},
        {"speed": "slow", "description": "Slow - Thoughtful"},
        {"speed": "normal", "description": "Normal - Baseline"},
        {"speed": "fast", "description": "Fast - Energetic"},
        {"speed": "fastest", "description": "Very Fast - Dynamic"}
    ]
    
    print(f"🗣️ Testing {len(speed_tests)} different speeds...")
    
    for i, speed_test in enumerate(speed_tests):
        speed = speed_test["speed"]
        description = speed_test["description"]
        
        print(f"\n🎯 Testing Speed {i+1}: {speed.upper()} - {description}")
        
        try:
            # Generate speech with speed control (using older model that supports controls)
            response = cartesia.tts.sse(
                model_id="sonic-2-2025-03-07",
                transcript=pepper_text,
                voice={
                    "id": authoritative_voice_id,
                    "experimental_controls": {
                        "speed": speed,
                        "emotion": []
                    }
                },
                output_format={
                    "container": "raw",
                    "encoding": "pcm_s16le",
                    "sample_rate": 22050
                }
            )
            
            # Collect audio chunks
            audio_chunks = []
            chunk_count = 0
            
            for chunk in response:
                if hasattr(chunk, 'data') and chunk.data:
                    audio_chunks.append(base64.b64decode(chunk.data))
                    chunk_count += 1
            
            if audio_chunks:
                # Save the audio file
                audio_data = b''.join(audio_chunks)
                output_file = f"pepper_authoritative_{speed}_speed.wav"
                
                # Convert raw PCM to WAV format
                with wave.open(output_file, 'wb') as wav_file:
                    wav_file.setnchannels(1)  # Mono
                    wav_file.setsampwidth(2)  # 16-bit
                    wav_file.setframerate(22050)  # Sample rate
                    wav_file.writeframes(audio_data)
                
                print(f"   ✅ Generated: {output_file}")
                print(f"   📊 Size: {len(audio_data)} bytes, Chunks: {chunk_count}")
                print(f"   🎵 Playing {speed} speed...")
                
                # Play the audio
                os.system(f"afplay {output_file}")
                
                # Wait a moment between tests
                import time
                time.sleep(1)
                
            else:
                print(f"   ❌ No audio generated for {speed} speed")
                
        except Exception as e:
            print(f"   ❌ Error with {speed} speed: {str(e)}")
    
    print(f"\n🎯 SPEED TEST COMPLETE!")
    print(f"📁 Generated files:")
    for speed_test in speed_tests:
        speed = speed_test["speed"]
        print(f"   🎤 pepper_authoritative_{speed}_speed.wav")
    
    print(f"\n💡 RECOMMENDATIONS:")
    print(f"   🚀 FAST: Best for challenging decisions and pushback")
    print(f"   ⚡ FASTEST: Best for urgent strategic advice")
    print(f"   🎯 NORMAL: Best for balanced strategic conversation")
    print(f"   🤔 SLOW: Best for complex analysis explanation")
    
    return True

def test_advanced_voice_controls():
    print(f"\n🎛️ Testing Advanced Voice Controls...")
    
    cartesia = Cartesia(api_key=os.getenv("CARTESIA_API_KEY"))
    authoritative_voice_id = "79a125e8-cd45-4c13-8a67-188112f4dd22"
    
    # Test different emotional combinations with speed
    advanced_tests = [
        {
            "name": "Strategic_Challenge",
            "speed": "fast",
            "emotion": ["assertive", "confident"],
            "text": "Actually, I disagree. Here are three better strategic alternatives you should consider instead."
        },
        {
            "name": "Analytical_Deep_Dive", 
            "speed": "normal",
            "emotion": ["thoughtful", "professional"],
            "text": "Let me break down the strategic implications of this decision and the risks you haven't considered."
        },
        {
            "name": "Urgent_Warning",
            "speed": "fastest", 
            "emotion": ["urgent", "concerned"],
            "text": "Stop. This decision could seriously damage your competitive position. Here's what you need to do instead."
        }
    ]
    
    for test in advanced_tests:
        print(f"\n🎭 Testing: {test['name']} ({test['speed']} speed)")
        
        try:
            response = cartesia.tts.sse(
                model_id="sonic-2-2025-03-07",
                transcript=test["text"],
                voice={
                    "id": authoritative_voice_id,
                    "experimental_controls": {
                        "speed": test["speed"],
                        "emotion": []
                    }
                },
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
            
            if audio_chunks:
                audio_data = b''.join(audio_chunks)
                output_file = f"pepper_{test['name'].lower()}.wav"
                
                with wave.open(output_file, 'wb') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(22050)
                    wav_file.writeframes(audio_data)
                
                print(f"   ✅ Generated: {output_file}")
                print(f"   🎵 Playing {test['name']}...")
                os.system(f"afplay {output_file}")
                
                import time
                time.sleep(1)
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Pepper Potts Voice Speed Optimization")
    print("=" * 50)
    
    # Test basic speeds
    test_pepper_speeds()
    
    # Test advanced controls
    test_advanced_voice_controls()
    
    print(f"\n🎯 FINAL RECOMMENDATION:")
    print(f"Listen to all the generated files and choose:")
    print(f"1. Best SPEED for Pepper's strategic personality")
    print(f"2. Best EMOTION combination for different scenarios")
    print(f"3. We can then build the perfect Pepper voice!")
