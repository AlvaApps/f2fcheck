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

## Setup

1. Fork this repository
2. Enable GitHub Actions in your fork
3. Add the following secrets in your repository's Settings > Secrets and Variables > Actions:
   - `EMAIL_SENDER`: Your Gmail address that will send notifications
   - `EMAIL_PASSWORD`: Your Gmail password or App Password
   - `EMAIL_RECIPIENT`: Email addresses where notifications should be sent (separate multiple addresses with semicolons, e.g., "email1@example.com;email2@example.com")
4. The monitoring will start automatically

You can also manually trigger the check using the "Run workflow" button in the Actions tab.

## Viewing Results

- Check the Action logs to see if any new opportunities were found
- View the opportunities.json file for the complete list of current opportunities
- Enable notifications on the repository to get alerts when new commits are made (indicating new opportunities)
