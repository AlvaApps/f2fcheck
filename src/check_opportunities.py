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
    test_url = "https://httpbin.org/get"
    actual_url = "https://folk2folk.com/opportunities/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }
    
    try:
        print("Testing connection through httpbin...")
        test_response = requests.get(test_url, headers=headers)
        print(f"Test connection successful! Status: {test_response.status_code}")
        
        print("\nTrying to access Folk2Folk...")
        session = requests.Session()
        session.verify = False
        response = session.get(actual_url, headers=headers, timeout=30)
        
        print(f"\nConnection successful!")
        print(f"Status code: {response.status_code}")
        print(f"Content type: {response.headers.get('Content-Type', 'Not specified')}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all opportunity elements using the correct class
        opportunities = soup.find_all('li', class_='market_list grid-item')
        
        if not opportunities:
            print("No opportunities found with market_list class")
            return None
        
        print(f"Found {len(opportunities)} opportunities")
        
        current_opportunities = []
        for opp in opportunities:
            # Extract the details based on the actual HTML structure
            title = opp.find('h2', class_='box_title')
            description = opp.find('p', class_='box_para common')
            location = opp.find('h3', class_='location common')
            interest = opp.find('h4', class_='interest common')
            ltv = opp.find('h5', class_='ltv common')
            
            opportunity = {
                'title': title.text.strip() if title else 'Unknown',
                'description': description.text.strip() if description else 'Unknown',
                'location': location.text.replace('Location:', '').strip() if location else 'Unknown',
                'interest': interest.text.replace('Interest:', '').strip() if interest else 'Unknown',
                'ltv': ltv.text.replace('LTV:', '').strip() if ltv else 'Unknown',
                'timestamp': datetime.utcnow().isoformat()
            }
            current_opportunities.append(opportunity)
            
        return current_opportunities
        
    except Exception as e:
        print(f"\nError fetching opportunities: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        
        try:
            import socket
            ip = socket.gethostbyname('folk2folk.com')
            print(f"\nServer IP address: {ip}")
        except Exception as ip_error:
            print(f"Could not resolve IP: {str(ip_error)}")
        
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
        body += f"Description: {opp['description']}\n"
        body += f"Location: {opp['location']}\n"
        body += f"Interest Rate: {opp['interest']}\n"
        body += f"LTV: {opp['ltv']}\n"
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
    try:
        current_opportunities = get_opportunities()
        if current_opportunities is None:
            print("Failed to fetch opportunities. Exiting.")
            return
        
        previous_opportunities = load_previous_opportunities()
        new_opportunities = find_new_opportunities(current_opportunities, previous_opportunities)
        
        if new_opportunities:
            print("::set-output name=has_new::true")
            print("New opportunities found:")
            for opp in new_opportunities:
                print(f"- {opp['title']} | {opp['amount']} | {opp['rate']}")
            send_email(new_opportunities)
        else:
            print("::set-output name=has_new::false")
            print("No new opportunities found")
        
        save_opportunities(current_opportunities)
        
    except Exception as e:
        print(f"Critical error in main: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        print(f"Traceback:\n{traceback.format_exc()}")

if __name__ == "__main__":
    main() 