# Folk2Folk Opportunity Monitor

This project monitors the Folk2Folk investment opportunities page for new investment listings. It runs every 5 minutes using GitHub Actions.

## How it works

1. A GitHub Action runs every 5 minutes
2. It scrapes the Folk2Folk opportunities page
3. Compares the current opportunities with the previously saved ones
4. If new opportunities are found:
   - They are printed in the action logs
   - The new list is saved to opportunities.json
   - Changes are committed to the repository
   - Email notifications are sent to configured recipients
   - SMS notifications are sent via Twilio

## Setup

1. Fork this repository
2. Enable GitHub Actions in your fork
3. Add the following secrets in your repository's Settings > Secrets and Variables > Actions:
   - `EMAIL_SENDER`: Your Gmail address that will send notifications
   - `EMAIL_PASSWORD`: Your Gmail password or App Password
   - `EMAIL_RECIPIENT`: Email addresses where notifications should be sent (separate multiple addresses with semicolons, e.g., "email1@example.com;email2@example.com")
   - `TWILIO_ACCOUNT_SID`: Your Twilio Account SID
   - `TWILIO_AUTH_TOKEN`: Your Twilio Auth Token
   - `TWILIO_PHONE_NUMBER`: Your Twilio phone number (must be in E.164 format, e.g., +1234567890)
   - `SMS_RECIPIENT`: The phone number to receive SMS notifications (must be in E.164 format)
4. The monitoring will start automatically

You can also manually trigger the check using the "Run workflow" button in the Actions tab.

## Viewing Results

- Check the Action logs to see if any new opportunities were found
- View the opportunities.json file for the complete list of current opportunities
- Enable notifications on the repository to get alerts when new commits are made (indicating new opportunities)
- Email and SMS notifications will be sent automatically when new opportunities are found

## Setting up Twilio

1. Sign up for a Twilio account at https://www.twilio.com/
2. Purchase a phone number with SMS capabilities
3. Find your Account SID and Auth Token in the Twilio console
4. Add these credentials to your GitHub secrets as described in the Setup section
