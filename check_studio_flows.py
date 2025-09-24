#!/usr/bin/env python3
"""
Check for Twilio Studio flows that might be intercepting calls
"""

import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

def main():
    print("🎭 CHECKING TWILIO STUDIO FLOWS...")
    
    # Initialize Twilio client
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    
    if not account_sid or not auth_token:
        print("❌ Missing Twilio credentials")
        return
    
    client = Client(account_sid, auth_token)
    
    try:
        # Check for Studio flows
        flows = client.studio.flows.list()
        
        if flows:
            print(f"🎭 Found {len(flows)} Studio flow(s):")
            for flow in flows:
                print(f"\n📋 Flow: {flow.friendly_name}")
                print(f"   SID: {flow.sid}")
                print(f"   Status: {flow.status}")
                print(f"   Created: {flow.date_created}")
                print(f"   Updated: {flow.date_updated}")
                
                # Check if any phone numbers are assigned to this flow
                try:
                    phone_numbers = client.incoming_phone_numbers.list()
                    for number in phone_numbers:
                        # Check if the voice URL points to this Studio flow
                        if flow.sid in str(number.voice_url):
                            print(f"   ⚠️  PHONE NUMBER {number.phone_number} is using this Studio flow!")
                            print(f"   🔗 Voice URL: {number.voice_url}")
                except Exception as e:
                    print(f"   Error checking phone numbers: {e}")
        else:
            print("✅ No Studio flows found")
        
        # Also check for any applications that might be interfering
        print(f"\n📱 CHECKING TWILIO APPLICATIONS...")
        applications = client.applications.list()
        
        if applications:
            print(f"📱 Found {len(applications)} application(s):")
            for app in applications:
                print(f"\n📋 App: {app.friendly_name}")
                print(f"   SID: {app.sid}")
                print(f"   Voice URL: {app.voice_url}")
                print(f"   Voice Method: {app.voice_method}")
        else:
            print("✅ No applications found")
            
        # Check for any TwiML Bins
        print(f"\n📄 CHECKING TWIML BINS...")
        try:
            # Note: TwiML Bins might not be available in all accounts
            pass
        except Exception as e:
            print(f"TwiML Bins check skipped: {e}")
            
        print(f"\n🔍 FINAL CHECK - Phone Number Details:")
        phone_numbers = client.incoming_phone_numbers.list()
        for number in phone_numbers:
            print(f"\n📞 {number.phone_number}:")
            print(f"   Voice URL: {number.voice_url}")
            
            # Check if URL contains Studio flow reference
            if "studio" in number.voice_url.lower():
                print(f"   ⚠️  THIS NUMBER IS USING STUDIO FLOW!")
            elif "fastapi-production-7282.up.railway.app" in number.voice_url:
                print(f"   ✅ Correctly pointing to Railway app")
            else:
                print(f"   ❓ Unknown webhook destination")
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
