#!/usr/bin/env python3
"""
Force refresh Twilio webhooks with cache-busting
"""

import os
import time
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

def main():
    print("🔄 FORCING TWILIO WEBHOOK REFRESH...")
    
    # Initialize Twilio client
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    
    if not account_sid or not auth_token:
        print("❌ Missing Twilio credentials")
        return
    
    client = Client(account_sid, auth_token)
    
    # Get current timestamp for cache busting
    timestamp = int(time.time())
    
    # Railway webhook URL with cache buster
    railway_url = "https://fastapi-production-7282.up.railway.app"
    webhook_url = f"{railway_url}/twilio/webhook/incoming-call?v={timestamp}"
    fallback_url = f"{railway_url}/twilio/webhook/voice-fallback?v={timestamp}"
    status_url = f"{railway_url}/twilio/webhook/call-status?v={timestamp}"
    
    print(f"🌐 Using cache-busted URLs:")
    print(f"   Main: {webhook_url}")
    print(f"   Fallback: {fallback_url}")
    print(f"   Status: {status_url}")
    
    try:
        phone_numbers = client.incoming_phone_numbers.list()
        
        for number in phone_numbers:
            print(f"\n🔄 Force refreshing {number.phone_number}...")
            
            # Step 1: Temporarily set to a different URL to clear cache
            temp_url = f"{railway_url}/health"
            print(f"   1️⃣ Setting temporary URL: {temp_url}")
            
            client.incoming_phone_numbers(number.sid).update(
                voice_url=temp_url,
                voice_method='GET'
            )
            
            # Wait a moment
            time.sleep(2)
            
            # Step 2: Set back to correct URL with cache buster
            print(f"   2️⃣ Setting final URL with cache buster")
            
            updated_number = client.incoming_phone_numbers(number.sid).update(
                voice_url=webhook_url,
                voice_method='POST',
                voice_fallback_url=fallback_url,
                voice_fallback_method='POST',
                status_callback=status_url,
                status_callback_method='POST'
            )
            
            print(f"   ✅ Updated: {updated_number.voice_url}")
            
            # Test the new URL immediately
            print(f"   🧪 Testing new URL...")
            import requests
            try:
                response = requests.post(webhook_url, data={
                    'From': '+12184094823',
                    'To': number.phone_number,
                    'CallSid': f'CACHE_BUST_TEST_{timestamp}',
                    'AccountSid': account_sid
                }, timeout=10)
                
                if response.status_code == 200 and "Pepper Potts" in response.text:
                    print(f"   ✅ Cache-busted URL working correctly!")
                else:
                    print(f"   ❌ Cache-busted URL issue: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Test failed: {str(e)}")
        
        print(f"\n🎉 Webhook refresh complete!")
        print(f"\n⏰ IMPORTANT: Wait 2-3 minutes for Twilio's cache to fully clear")
        print(f"📞 Then test calling: +18555722404 or +12182414667")
        print(f"🎯 You should now hear Pepper Potts greeting!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
