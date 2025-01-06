import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_opportunities():
    url = "https://folk2folk.com/opportunities/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all opportunity elements (you may need to adjust these selectors based on the actual page structure)
        opportunities = soup.find_all('div', class_='opportunity-card')
        
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