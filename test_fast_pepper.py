#!/usr/bin/env python3
"""
Quick test of Pepper Potts at FAST speed
"""

import os
import base64
import wave
from cartesia import Cartesia

# Set API key
os.environ["CARTESIA_API_KEY"] = "sk_car_9fM7KFZEfqeEfiETkHXwaH"

def test_fast_pepper():
    print("🚀 Testing Pepper Potts at FAST speed...")
    
    cartesia = Cartesia(api_key=os.getenv("CARTESIA_API_KEY"))
    
    # Authoritative female voice ID
    authoritative_voice_id = "79a125e8-cd45-4c13-8a67-188112f4dd22"
    
    # Strategic test text
    pepper_text = """
    I disagree with that approach. Here's the thing - you're thinking too small. 
    Let me challenge your assumptions and give you three better strategic alternatives. 
    First, instead of competing on price, position yourself as the premium solution. 
    What's your response to this strategic analysis?
    """
    
    try:
        print("🗣️ Generating FAST authoritative Pepper voice...")
        
        # Generate speech with FAST speed
        response = cartesia.tts.sse(
            model_id="sonic-2-2025-03-07",
            transcript=pepper_text,
            voice={
                "id": authoritative_voice_id,
                "experimental_controls": {
                    "speed": "fast",
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
                if chunk_count % 20 == 0:
                    print(f"   📦 Received {chunk_count} chunks...")
        
        if audio_chunks:
            # Save the audio file
            audio_data = b''.join(audio_chunks)
            output_file = "pepper_fast_authoritative.wav"
            
            # Convert raw PCM to WAV format
            with wave.open(output_file, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(22050)  # Sample rate
                wav_file.writeframes(audio_data)
            
            print(f"✅ Generated: {output_file}")
            print(f"📊 Size: {len(audio_data)} bytes, Chunks: {chunk_count}")
            print(f"🎵 Playing FAST Pepper...")
            
            # Play the audio
            os.system(f"afplay {output_file}")
            
            print(f"\n🎯 FAST PEPPER RESULTS:")
            print(f"✅ Speed: FAST")
            print(f"✅ Voice: Authoritative Female")
            print(f"✅ Quality: Ultra-high (22kHz)")
            print(f"✅ Perfect for strategic challenges and pushback!")
            
            return True
        else:
            print("❌ No audio generated")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_fast_pepper()
