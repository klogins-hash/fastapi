#!/usr/bin/env python3
"""
Rebuild Twilio Configuration from Scratch
Complete reset and reconfiguration for premium Deepgram+Cartesia pipeline
"""

import os
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    print("🔧 REBUILDING Twilio Configuration from Scratch...")
    print("🗑️  Clearing old configurations and setting up premium pipeline")
    
    # Initialize Twilio client
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    
    if not account_sid or not auth_token:
        print("❌ Missing Twilio credentials in environment variables")
        print("💡 Make sure TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN are set")
        return
    
    client = Client(account_sid, auth_token)
    
    # Railway webhook URL for premium pipeline
    railway_url = "https://fastapi-production-7282.up.railway.app"
    premium_webhook = f"{railway_url}/twilio/webhook/incoming-call"
    status_callback = f"{railway_url}/twilio/webhook/call-status"
    
    print(f"🌐 Railway URL: {railway_url}")
    print(f"📞 Premium Webhook: {premium_webhook}")
    
    try:
        # Get all phone numbers
        phone_numbers = client.incoming_phone_numbers.list()
        
        print(f"\n📱 Found {len(phone_numbers)} phone number(s) to reconfigure:")
        
        for number in phone_numbers:
            print(f"\n📞 Reconfiguring {number.friendly_name} ({number.phone_number})")
            
            # COMPLETELY RESET the phone number configuration
            updated_number = client.incoming_phone_numbers(number.sid).update(
                # Voice configuration - PREMIUM PIPELINE ONLY
                voice_url=premium_webhook,
                voice_method='POST',
                voice_fallback_url=f"{railway_url}/twilio/webhook/voice-fallback",
                voice_fallback_method='POST',
                
                # Status callbacks
                status_callback=status_callback,
                status_callback_method='POST',
                
                # SMS configuration (keep existing or disable)
                sms_url=number.sms_url,  # Keep existing SMS config
                sms_method=number.sms_method,
                
                # Clear any old configurations
                voice_caller_id_lookup=False,
            )
            
            print(f"   ✅ Voice URL: {updated_number.voice_url}")
            print(f"   ✅ Voice Method: {updated_number.voice_method}")
            print(f"   ✅ Status Callback: {updated_number.status_callback}")
            print(f"   🔄 Configuration completely rebuilt")
        
        print(f"\n🎉 Twilio configuration rebuild complete!")
        print(f"\n📋 Summary:")
        print(f"   🌐 All numbers point to: {premium_webhook}")
        print(f"   🎯 Premium pipeline: Deepgram Nova-2 + Cartesia")
        print(f"   🤖 Strategic AI: Pepper Potts")
        
        print(f"\n🧪 Test by calling your numbers:")
        for number in phone_numbers:
            print(f"   📱 {number.phone_number}")
        
        print(f"\n🎯 Expected flow:")
        print(f"   1. Premium greeting from Pepper Potts")
        print(f"   2. Record your strategic question (60 seconds)")
        print(f"   3. Deepgram Nova-2 transcription")
        print(f"   4. Strategic intent analysis")
        print(f"   5. Pepper's strategic response")
        print(f"   6. Follow-up conversation")
        
    except Exception as e:
        print(f"❌ Error rebuilding Twilio configuration: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Twilio rebuild successful!")
    else:
        print("\n❌ Twilio rebuild failed!")
