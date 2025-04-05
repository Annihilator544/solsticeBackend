import base64
import re
from flask import Flask, jsonify
import quickstart

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/fetch_bank_emails')
def fetch_bank_emails():
    # Authenticate and build the service
    service = quickstart.auth()
    # This function will authenticate the user and return a Gmail service instance.
    
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
        transactions_found = []
        
        for part in payload_parts:
            data = part['body'].get('data')
            if data:
                decoded_text = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                # If it matches typical bank keywords, we consider it relevant
                if re.search(r'\b(debited|credited|transaction|account|bank)\b', decoded_text.lower()):
                    info = {}

                    amount_match = re.search(r'Rs\.?\s?(\d+(?:\.\d+))', decoded_text)
                    if amount_match:
                        info['amount'] = amount_match.group(1)

                    detail_match = re.search(
                        r'to\s+VPA\s+([\S]+)\s+(.*?)\s+on\s+(\d{2}-\d{2}-\d{2})',
                        decoded_text
                    )
                    if detail_match:
                        info['upi_id'] = detail_match.group(1)
                        info['receiver'] = detail_match.group(2)
                        info['date'] = detail_match.group(3)

                    ref_match = re.search(
                        r'UPI transaction reference number is\s+(\S+)',
                        decoded_text
                    )
                    if ref_match:
                        info['upi_reference'] = ref_match.group(1)

                    if info:
                        transactions_found.append(info)
        
        # If we found any relevant text, add it to the results
        if transactions_found:
            email_data_list.append({
                'subject': subject,
                'info': transactions_found,
            })
    
    # Return the found emails as JSON
    return jsonify(email_data_list)

if __name__ == '__main__':
    app.run(debug=True)
