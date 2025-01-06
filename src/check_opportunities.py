import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import urllib3
import certifi

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_opportunities():
    # First try accessing through a proxy to debug
    test_url = "https://httpbin.org/get"
    actual_url = "https://folk2folk.com/opportunities/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Test connection through httpbin first
        print("Testing connection through httpbin...")
        test_response = requests.get(test_url, headers=headers)
        print(f"Test connection successful! Status: {test_response.status_code}")
        
        print("\nTrying to access Folk2Folk...")
        # Try with different options for SSL
        try:
            # Try with default settings
            response = requests.get(actual_url, headers=headers, timeout=10)
        except requests.exceptions.SSLError:
            print("SSL Error occurred, trying with custom SSL context...")
            import ssl
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            session = requests.Session()
            session.verify = False
            response = session.get(actual_url, headers=headers, timeout=10)
        
        response.raise_for_status()
        
        # Print detailed response information for debugging
        print(f"Connection successful!")
        print(f"Status code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Content length: {len(response.text)}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all opportunity elements
        opportunities = soup.find_all('div', class_='opportunity-card')
        
        if not opportunities:
            print("Warning: No opportunities found. Page content preview:")
            print(response.text[:1000])
            print("\nTrying alternative selectors...")
            # Try some alternative selectors that might be used
            print("Looking for tables...")
            tables = soup.find_all('table')
            print(f"Found {len(tables)} tables")
            print("Looking for divs with 'opportunity' in class or id...")
            opp_divs = soup.find_all('div', class_=lambda x: x and 'opportunity' in x.lower())
            print(f"Found {len(opp_divs)} potential opportunity divs")
        
        current_opportunities = []
        for opp in opportunities:
            opportunity = {
                'title': opp.find('h3').text.strip() if opp.find('h3') else 'Unknown',
                'amount': opp.find('div', class_='amount').text.strip() if opp.find('div', class_='amount') else 'Unknown',
                'rate': opp.find('div', class_='rate').text.strip() if opp.find('div', class_='rate') else 'Unknown',
                'timestamp': datetime.utcnow().isoformat()
            }
            current_opportunities.append(opportunity)
            
        return current_opportunities
        
    except Exception as e:
        print(f"Error fetching opportunities: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        if hasattr(e, 'response'):
            print(f"Response status code: {e.response.status_code}")
            print(f"Response headers: {e.response.headers}")
        
        # Try to get the IP address of the server
        try:
            import socket
            ip = socket.gethostbyname('folk2folk.com')
            print(f"\nServer IP address: {ip}")
        except Exception as e:
            print(f"Could not resolve IP: {str(e)}")
            
        return None

def load_previous_opportunities():
    if os.path.exists('opportunities.json'):
        with open('opportunities.json', 'r') as f:
            return json.load(f)
    return []

def save_opportunities(opportunities):
    with open('opportunities.json', 'w') as f:
        json.dump(opportunities, f, indent=2)

def find_new_opportunities(current, previous):
    if not previous:
        return current
    
    current_titles = {opp['title'] for opp in current}
    previous_titles = {opp['title'] for opp in previous}
    
    new_titles = current_titles - previous_titles
    return [opp for opp in current if opp['title'] in new_titles]

def send_email(new_opportunities):
    sender_email = os.environ.get('EMAIL_SENDER')
    sender_password = os.environ.get('EMAIL_PASSWORD')
    recipients_str = os.environ.get('EMAIL_RECIPIENT', '')
    recipients = [email.strip() for email in recipients_str.split(';') if email.strip()]
    
    if not all([sender_email, sender_password, recipients]):
        print("Missing email configuration. Please check EMAIL_SENDER, EMAIL_PASSWORD, and EMAIL_RECIPIENT secrets.")
        return
    
    # Create message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = ", ".join(recipients)  # Join all recipients with commas
    message["Subject"] = "New Folk2Folk Investment Opportunities"
    
    # Create the email body
    body = "New investment opportunities have been found:\n\n"
    for opp in new_opportunities:
        body += f"Title: {opp['title']}\n"
        body += f"Amount: {opp['amount']}\n"
        body += f"Rate: {opp['rate']}\n"
        body += f"Found at: {opp['timestamp']}\n"
        body += "-" * 40 + "\n"
    
    message.attach(MIMEText(body, "plain"))
    
    try:
        # Create SMTP session
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)
        print("Email notification sent successfully")
    except Exception as e:
        print(f"Failed to send email notification: {str(e)}")

def main():
    current_opportunities = get_opportunities()
    if current_opportunities is None:
        return
    
    previous_opportunities = load_previous_opportunities()
    new_opportunities = find_new_opportunities(current_opportunities, previous_opportunities)
    
    if new_opportunities:
        print("::set-output name=has_new::true")
        print("New opportunities found:")
        for opp in new_opportunities:
            print(f"- {opp['title']} | {opp['amount']} | {opp['rate']}")
        # Send email notification
        send_email(new_opportunities)
    else:
        print("::set-output name=has_new::false")
        print("No new opportunities found")
    
    save_opportunities(current_opportunities)

if __name__ == "__main__":
    main() 