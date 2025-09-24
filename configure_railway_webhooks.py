#!/usr/bin/env python3
"""
Configure Twilio phone numbers with Railway webhook URLs
"""

from dotenv import load_dotenv
from twilio.rest import Client
import os

# Load environment variables
load_dotenv()

def configure_railway_webhooks():
    """Configure webhook URLs for Twilio phone numbers to point to Railway"""
    
    # Your Railway webhook URL
    railway_url = "https://fastapi-production-7282.up.railway.app"
    webhook_url = f"{railway_url}/twilio/webhook/incoming-call"
    
    print("🔧 Configuring Twilio phone number webhooks for Railway...")
    print(f"📞 Webhook URL: {webhook_url}")
    print()
    
    try:
        # Initialize Twilio client
        client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
        
        # Get all phone numbers
        phone_numbers = client.incoming_phone_numbers.list()
        
        if not phone_numbers:
            print("❌ No phone numbers found in your Twilio account")
            return
        
        print(f"📱 Found {len(phone_numbers)} phone number(s):")
        
        for phone_number in phone_numbers:
            print(f"\n📞 Configuring {phone_number.friendly_name} ({phone_number.phone_number})")
            
            try:
                # Update the phone number with Railway webhook URL
                phone_number.update(
                    voice_url=webhook_url,
                    voice_method='POST',
                    status_callback=f"{railway_url}/twilio/webhook/call-status",
                    status_callback_method='POST'
                )
                
                print(f"   ✅ Successfully configured webhook")
                print(f"   🔗 Voice URL: {webhook_url}")
                print(f"   📊 Status Callback: {railway_url}/twilio/webhook/call-status")
                
            except Exception as e:
                print(f"   ❌ Failed to configure {phone_number.phone_number}: {str(e)}")
        
        print("\n🎉 Webhook configuration complete!")
        print("\n📋 Your phone numbers are now connected to your Railway app:")
        print(f"   🌐 Railway URL: {railway_url}")
        print(f"   📞 Webhook: {webhook_url}")
        print("\n🧪 Test by calling your Twilio numbers:")
        for phone_number in phone_numbers:
            print(f"   📱 {phone_number.phone_number}")
        
        print("\n🎯 What happens when someone calls:")
        print("   1. Twilio receives the call")
        print("   2. Twilio sends webhook to your Railway app")
        print("   3. Your LangGraph agent processes the speech")
        print("   4. Claude generates a response")
        print("   5. Response is spoken back to the caller")
        
    except Exception as e:
        print(f"❌ Error configuring webhooks: {str(e)}")
        print("💡 Make sure your Twilio credentials are correct in .env file")

if __name__ == "__main__":
    configure_railway_webhooks()
