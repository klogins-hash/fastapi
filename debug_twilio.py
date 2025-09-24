#!/usr/bin/env python3
"""
Debug Twilio Configuration - Check what's actually configured
"""

import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

def main():
    print("🔍 DEBUGGING Twilio Configuration...")
    
    # Initialize Twilio client
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    
    if not account_sid or not auth_token:
        print("❌ Missing Twilio credentials")
        return
    
    client = Client(account_sid, auth_token)
    
    try:
        # Get all phone numbers and their EXACT configuration
        phone_numbers = client.incoming_phone_numbers.list()
        
        print(f"\n📱 Found {len(phone_numbers)} phone number(s):")
        
        for number in phone_numbers:
            print(f"\n" + "="*60)
            print(f"📞 NUMBER: {number.phone_number} ({number.friendly_name})")
            print(f"📞 SID: {number.sid}")
            print(f"🔗 Voice URL: {number.voice_url}")
            print(f"🔗 Voice Method: {number.voice_method}")
            print(f"🔗 Voice Fallback URL: {number.voice_fallback_url}")
            print(f"🔗 Voice Fallback Method: {number.voice_fallback_method}")
            print(f"📊 Status Callback: {number.status_callback}")
            print(f"📊 Status Callback Method: {number.status_callback_method}")
            print(f"📱 SMS URL: {number.sms_url}")
            print(f"📱 SMS Method: {number.sms_method}")
            print(f"🆔 Voice Caller ID Lookup: {number.voice_caller_id_lookup}")
            print(f"📅 Date Created: {number.date_created}")
            print(f"📅 Date Updated: {number.date_updated}")
            
            # Test the webhook URL directly
            print(f"\n🧪 Testing webhook URL...")
            import requests
            try:
                response = requests.post(number.voice_url, data={
                    'From': '+12184094823',
                    'To': number.phone_number,
                    'CallSid': 'DEBUG_TEST',
                    'AccountSid': account_sid
                }, timeout=10)
                
                print(f"✅ Webhook Response Status: {response.status_code}")
                if response.status_code == 200:
                    content = response.text
                    if "Pepper Potts" in content:
                        print("✅ Webhook returns PEPPER POTTS greeting")
                    else:
                        print("❌ Webhook returns OLD greeting")
                        print(f"Response preview: {content[:200]}...")
                else:
                    print(f"❌ Webhook failed: {response.text[:200]}")
                    
            except Exception as e:
                print(f"❌ Webhook test failed: {str(e)}")
        
        print(f"\n" + "="*60)
        print(f"🎯 EXPECTED CONFIGURATION:")
        print(f"   Voice URL: https://fastapi-production-7282.up.railway.app/twilio/webhook/incoming-call")
        print(f"   Voice Method: POST")
        print(f"   Should contain: 'Pepper Potts, your Strategic AI Partner'")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
