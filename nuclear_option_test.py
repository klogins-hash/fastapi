#!/usr/bin/env python3
"""
Nuclear option: Make a test call FROM Twilio TO your number to see what happens
"""

import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

def main():
    print("☢️  NUCLEAR OPTION: Making test call FROM Twilio...")
    
    # Initialize Twilio client
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    
    if not account_sid or not auth_token:
        print("❌ Missing Twilio credentials")
        return
    
    client = Client(account_sid, auth_token)
    
    # Your phone numbers
    twilio_numbers = ['+18555722404', '+12182414667']
    
    print("🎯 This will make a test call to see what actually happens...")
    print("⚠️  WARNING: This will use Twilio credits!")
    
    # Get your personal number to call FROM
    test_from_number = input("Enter YOUR personal phone number to call FROM (e.g., +12184094823): ")
    
    if not test_from_number.startswith('+'):
        test_from_number = '+' + test_from_number.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
    
    print(f"📞 Will call FROM: {test_from_number}")
    
    # Choose which Twilio number to test
    print("\nWhich Twilio number should we test?")
    for i, number in enumerate(twilio_numbers):
        print(f"{i+1}. {number}")
    
    choice = input("Enter choice (1 or 2): ")
    
    if choice == '1':
        to_number = twilio_numbers[0]
    elif choice == '2':
        to_number = twilio_numbers[1]
    else:
        print("Invalid choice")
        return
    
    print(f"📞 Will call TO: {to_number}")
    
    # Create a simple TwiML that will call your Twilio number
    twiml_url = f"https://fastapi-production-7282.up.railway.app/twilio/webhook/test-call-twiml"
    
    # First, let me create that endpoint
    print("🔧 Creating test TwiML endpoint...")
    
    try:
        # Make the test call
        print(f"\n☎️  Making test call...")
        print(f"   FROM: {test_from_number}")
        print(f"   TO: {to_number}")
        
        call = client.calls.create(
            to=to_number,
            from_=test_from_number,
            url=twiml_url,
            method='POST'
        )
        
        print(f"✅ Test call initiated!")
        print(f"📞 Call SID: {call.sid}")
        print(f"🔗 Status: {call.status}")
        
        print(f"\n🎯 What should happen:")
        print(f"1. Your phone ({test_from_number}) will ring")
        print(f"2. Answer it")
        print(f"3. You'll hear a message, then it will call {to_number}")
        print(f"4. Listen to what greeting you hear on {to_number}")
        print(f"5. This will tell us if the webhook is really working")
        
    except Exception as e:
        print(f"❌ Error making test call: {str(e)}")

if __name__ == "__main__":
    main()
