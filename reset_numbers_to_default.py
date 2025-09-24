#!/usr/bin/env python3
"""
Reset Twilio phone numbers to absolute default state
"""

import os
import time
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

def main():
    print("🔄 RESETTING TWILIO NUMBERS TO DEFAULT STATE...")
    
    # Initialize Twilio client
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    
    if not account_sid or not auth_token:
        print("❌ Missing Twilio credentials")
        return
    
    client = Client(account_sid, auth_token)
    
    try:
        phone_numbers = client.incoming_phone_numbers.list()
        
        print(f"📱 Found {len(phone_numbers)} phone number(s) to reset:")
        
        for number in phone_numbers:
            print(f"\n🔄 RESETTING {number.phone_number} to DEFAULT...")
            
            # Step 1: Reset to absolute defaults (empty/null values)
            print("   1️⃣ Clearing ALL configurations...")
            
            reset_number = client.incoming_phone_numbers(number.sid).update(
                # Voice - set to defaults
                voice_url="",  # Empty URL
                voice_method="POST",
                voice_fallback_url="",  # No fallback
                voice_fallback_method="POST",
                voice_caller_id_lookup=False,
                
                # SMS - keep existing or clear
                sms_url="",  # Clear SMS URL
                sms_method="POST",
                sms_fallback_url="",
                sms_fallback_method="POST",
                
                # Status callbacks - clear
                status_callback="",
                status_callback_method="POST",
                
                # Other settings
                friendly_name=number.phone_number,  # Reset to just the number
            )
            
            print(f"   ✅ Reset to defaults")
            print(f"   📞 Voice URL: '{reset_number.voice_url}'")
            print(f"   📱 SMS URL: '{reset_number.sms_url}'")
            print(f"   📊 Status Callback: '{reset_number.status_callback}'")
            
            # Wait a moment for Twilio to process
            time.sleep(3)
            
            # Step 2: Verify the reset worked
            print("   2️⃣ Verifying reset...")
            
            # Fetch the number again to confirm
            verified_number = client.incoming_phone_numbers(number.sid).fetch()
            
            if not verified_number.voice_url or verified_number.voice_url == "":
                print("   ✅ Voice URL successfully cleared")
            else:
                print(f"   ⚠️  Voice URL still has: {verified_number.voice_url}")
            
            if not verified_number.status_callback or verified_number.status_callback == "":
                print("   ✅ Status callback successfully cleared")
            else:
                print(f"   ⚠️  Status callback still has: {verified_number.status_callback}")
        
        print(f"\n🎉 ALL NUMBERS RESET TO DEFAULT STATE!")
        
        # Now ask if user wants to reconfigure with fresh settings
        print(f"\n🔧 Would you like to reconfigure with fresh Pepper Potts settings?")
        reconfigure = input("Reconfigure now? (y/n): ").lower().strip()
        
        if reconfigure == 'y' or reconfigure == 'yes':
            print(f"\n🚀 RECONFIGURING WITH FRESH SETTINGS...")
            
            # Fresh Railway webhook URLs (no cache busting this time)
            railway_url = "https://fastapi-production-7282.up.railway.app"
            fresh_webhook = f"{railway_url}/twilio/webhook/incoming-call"
            fresh_fallback = f"{railway_url}/twilio/webhook/voice-fallback"
            fresh_status = f"{railway_url}/twilio/webhook/call-status"
            
            for number in phone_numbers:
                print(f"\n🔧 Reconfiguring {number.phone_number}...")
                
                # Wait a moment before reconfiguring
                time.sleep(2)
                
                # Apply fresh configuration
                fresh_number = client.incoming_phone_numbers(number.sid).update(
                    voice_url=fresh_webhook,
                    voice_method='POST',
                    voice_fallback_url=fresh_fallback,
                    voice_fallback_method='POST',
                    status_callback=fresh_status,
                    status_callback_method='POST',
                    friendly_name=f"Pepper Potts AI - {number.phone_number}"
                )
                
                print(f"   ✅ Fresh configuration applied")
                print(f"   🔗 Voice URL: {fresh_number.voice_url}")
                
                # Test the fresh configuration
                print(f"   🧪 Testing fresh webhook...")
                import requests
                try:
                    response = requests.post(fresh_webhook, data={
                        'From': '+12184094823',
                        'To': number.phone_number,
                        'CallSid': f'FRESH_TEST_{int(time.time())}',
                        'AccountSid': account_sid
                    }, timeout=10)
                    
                    if response.status_code == 200 and "Pepper Potts" in response.text:
                        print(f"   ✅ Fresh webhook working perfectly!")
                    else:
                        print(f"   ❌ Fresh webhook issue: {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ Test failed: {str(e)}")
            
            print(f"\n🎉 FRESH RECONFIGURATION COMPLETE!")
            print(f"\n📞 Your numbers are now freshly configured:")
            for number in phone_numbers:
                print(f"   📱 {number.phone_number}")
            
            print(f"\n🎯 Test calling now - you should hear Pepper Potts!")
            
        else:
            print(f"\n✅ Numbers reset to default. You can reconfigure manually later.")
            print(f"\n📋 To reconfigure manually:")
            print(f"   1. Go to Twilio Console")
            print(f"   2. Phone Numbers → Manage → Active numbers")
            print(f"   3. Set Voice URL: https://fastapi-production-7282.up.railway.app/twilio/webhook/incoming-call")
            print(f"   4. Set Method: POST")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
