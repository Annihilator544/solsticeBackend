import base64
import email
import re

from flask import Flask, jsonify
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

app = Flask(__name__)

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    # This will initiate an OAuth flow in your browser when hit via the Flask route.
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    service = build('gmail', 'v1', credentials=creds)
    return service

@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/fetch_bank_emails')
def fetch_bank_emails():
    # Authenticate and build the service
    service = get_gmail_service()
    
    # Basic Gmail search query to find potential banking emails:
    # Searching for specific bank domains or keywords.
    query = '(from:@hdfcbank.com OR from:@icicibank.com OR from:@axisbank.com OR debited OR credited OR bank)'
    
    # Retrieve message IDs matching the query
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])
    
    # We'll store the parsed emails here
    email_data_list = []
    
    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        
        # Extract subject from headers
        subject = ''
        headers = msg_data['payload'].get('headers', [])
        for h in headers:
            if h.get('name') == 'Subject':
                subject = h.get('value')
                break
        
        # If the email has multiple parts, parse them
        payload_parts = msg_data['payload'].get('parts', [])
        
        # For demonstration, we'll just gather all text parts we find
        body_texts = []
        
        for part in payload_parts:
            data = part['body'].get('data')
            if data:
                decoded_text = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                # If it matches typical bank keywords, we consider it relevant
                if re.search(r'\b(debited|credited|transaction|account|bank)\b', decoded_text.lower()):
                    body_texts.append(decoded_text)
        
        # If we found any relevant text, add it to the results
        if body_texts:
            email_data_list.append({
                'subject': subject,
                'body': "\n\n".join(body_texts)
            })
    
    # Return the found emails as JSON
    return jsonify(email_data_list)

if __name__ == '__main__':
    app.run(debug=True)
