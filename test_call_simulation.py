#!/usr/bin/env python3
"""
Simulate a complete call flow to debug the issue
"""

import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

def test_call_flow():
    print("🧪 SIMULATING COMPLETE CALL FLOW...")
    
    base_url = "https://fastapi-production-7282.up.railway.app"
    
    # Step 1: Test incoming call webhook
    print("\n1️⃣ Testing incoming call webhook...")
    response = requests.post(f"{base_url}/twilio/webhook/incoming-call", data={
        'From': '+12184094823',
        'To': '+18555722404',
        'CallSid': 'SIMULATION_TEST_123',
        'AccountSid': 'TEST_ACCOUNT'
    })
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:300]}...")
    
    if "Pepper Potts" in response.text:
        print("✅ Correct Pepper Potts greeting!")
    else:
        print("❌ Wrong greeting!")
        return
    
    # Step 2: Test the Deepgram processing endpoint
    print("\n2️⃣ Testing Deepgram processing endpoint...")
    
    # Create a fake recording URL (this will fail but we can see the flow)
    response = requests.post(f"{base_url}/twilio/webhook/process-deepgram-audio", data={
        'RecordingUrl': 'https://fake-recording-url.com/test.wav',
        'CallSid': 'SIMULATION_TEST_123',
        'AccountSid': 'TEST_ACCOUNT'
    })
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:300]}...")
    
    # Step 3: Test health endpoint
    print("\n3️⃣ Testing health endpoint...")
    response = requests.get(f"{base_url}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Step 4: Test if there are any other endpoints that might be interfering
    print("\n4️⃣ Testing potential interfering endpoints...")
    
    endpoints_to_test = [
        "/twilio/webhook/process-speech",
        "/twilio/webhook/voice-fallback",
        "/twilio/webhook/call-status"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.post(f"{base_url}{endpoint}", data={
                'From': '+12184094823',
                'To': '+18555722404',
                'CallSid': 'TEST_123'
            })
            print(f"   {endpoint}: {response.status_code}")
            if response.status_code == 200 and len(response.text) > 50:
                print(f"      Response: {response.text[:100]}...")
        except Exception as e:
            print(f"   {endpoint}: ERROR - {str(e)}")

def check_railway_deployment():
    print("\n🚀 CHECKING RAILWAY DEPLOYMENT STATUS...")
    
    # Check if the deployment is actually live
    try:
        response = requests.get("https://fastapi-production-7282.up.railway.app/health", timeout=5)
        print(f"✅ Railway app is live: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Check the timestamp to see when it was last deployed
        timestamp = response.json().get('timestamp', '')
        print(f"Last health check: {timestamp}")
        
    except Exception as e:
        print(f"❌ Railway app not responding: {str(e)}")

if __name__ == "__main__":
    check_railway_deployment()
    test_call_flow()
    
    print("\n🎯 SUMMARY:")
    print("If Twilio config is correct but you're hearing old voice:")
    print("1. Twilio might be caching the old response")
    print("2. There might be a different webhook URL configured somewhere")
    print("3. The call might be going to a different service")
    print("4. There might be a Twilio Studio flow interfering")
    
    print("\n💡 NEXT STEPS:")
    print("1. Check Twilio Console for any Studio flows")
    print("2. Clear Twilio cache (wait 5-10 minutes)")
    print("3. Check if there are multiple Twilio accounts")
    print("4. Verify the phone number you're calling is correct")
