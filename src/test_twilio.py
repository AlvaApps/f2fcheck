import os
import sys
from twilio.rest import Client
from datetime import datetime

def test_send_sms():
    """Test Twilio SMS integration with sample data"""
    # Use environment variables instead of hardcoded credentials
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    twilio_number = os.environ.get('TWILIO_PHONE_NUMBER')
    recipient_number = os.environ.get('SMS_RECIPIENT')
    
    # Check if all required variables are set
    if not all([account_sid, auth_token, twilio_number, recipient_number]):
        missing = []
        if not account_sid:
            missing.append("TWILIO_ACCOUNT_SID")
        if not auth_token:
            missing.append("TWILIO_AUTH_TOKEN")
        if not twilio_number:
            missing.append("TWILIO_PHONE_NUMBER")
        if not recipient_number:
            missing.append("SMS_RECIPIENT")
        
        print(f"⚠️ Missing Twilio configuration: {', '.join(missing)}")
        print("Please set these environment variables before running the test.")
        sys.exit(1)
    
    print(f"✅ All Twilio environment variables are set.")
    print(f"  - Sender number: {twilio_number}")
    print(f"  - Recipient number: {recipient_number}")
    
    # Sample investment opportunities
    test_opportunities = [
        {
            'title': 'Test Investment #1',
            'description': 'This is a test investment opportunity',
            'location': 'Devon',
            'interest': '9.0% p.a.',
            'ltv': '60% (Open Market Value)',
            'timestamp': datetime.utcnow().isoformat()
        },
        {
            'title': 'Test Investment #2',
            'description': 'Another test investment',
            'location': 'Cornwall',
            'interest': '8.75% p.a.',
            'ltv': '50% (Open Market Value)',
            'timestamp': datetime.utcnow().isoformat()
        }
    ]
    
    try:
        print("\n🔄 Initializing Twilio client...")
        client = Client(account_sid, auth_token)
        
        # Create the SMS message content
        message_body = f"FOLK2FOLK TEST MESSAGE - New Investment Opportunities:\n"
        for i, opp in enumerate(test_opportunities, 1):
            message_body += f"{i}. {opp['title']} - {opp['location']} - {opp['interest']}\n"
        
        print(f"\n📝 Message to be sent:\n{message_body}")
        
        print("\n📱 Sending test SMS...")
        message = client.messages.create(
            body=message_body,
            from_=twilio_number,
            to=recipient_number
        )
        
        print(f"\n✅ SMS sent successfully!")
        print(f"  - Message SID: {message.sid}")
        print(f"  - Status: {message.status}")
        return True
        
    except Exception as e:
        print(f"\n❌ Failed to send SMS: {str(e)}")
        print(f"  - Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    print("🧪 TWILIO SMS INTEGRATION TEST 🧪")
    print("-" * 50)
    result = test_send_sms()
    print("-" * 50)
    if result:
        print("✅ Test completed successfully!")
    else:
        print("❌ Test failed!") 