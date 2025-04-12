import base64
import re
from flask import Flask, jsonify, request
import quickstart
import classify
import time
from flask_cors import CORS, cross_origin

app = Flask(__name__)

CORS(app, support_credentials=True)

@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/fetch_all_bank_emails', methods=["POST"])
def fetch_bank_emails():
    # Authenticate and build the service
    service = quickstart.auth()
    data = request.get_json()
    custom_config = data.get("config", None)
    # This function will authenticate the user and return a Gmail service instance.
    
    # Basic Gmail search query to find potential banking emails:
    # Searching for specific bank domains or keywords.
    query = '(from:@hdfcbank.com OR from:@icicibank.com OR from:@axisbank.com OR debited OR credited)'
    
    # Retrieve message IDs matching the query
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])
    
    
    # For demonstration, we'll just gather all text parts we find
    transactions_found = []
    
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
        
        for part in payload_parts:
            data = part['body'].get('data')
            if data:
                decoded_text = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                # If it matches typical bank keywords, we consider it relevant
                if re.search(r'\b(debited|credited|transaction|account|bank)\b', decoded_text.lower()):
                    info = {}
                    info['subject'] = subject
                    info['type'] = re.search(r'\b(debited|credited)\b', decoded_text.lower()).group(0) if re.search(r'\b(debited|credited)\b', decoded_text.lower()) else None
                    amount_match = re.search(r'Rs\.?\s?(\d+(?:\.\d+))', decoded_text)
                    if amount_match:
                        info['amount'] = float(amount_match.group(1))

                    detail_match = re.search(
                        r'to\s+VPA\s+([\S]+)\s+(.*?)\s+on\s+(\d{2}-\d{2}-\d{2})',
                        decoded_text
                    )
                    if detail_match:
                        upi_id = detail_match.group(1)
                        receiver = detail_match.group(2)
                        txn_date = detail_match.group(3)
                        
                        # 2) Pass custom config into the classify function
                        info['class'] = classify.classify_transaction(
                            receiver,
                            categories=custom_config  # If None, your classify function uses its default
                        )
                        
                        info['upi_id'] = upi_id
                        info['receiver'] = receiver
                        info['date'] = txn_date

                    ref_match = re.search(
                        r'UPI transaction reference number is\s+(\d+)',
                        decoded_text
                    )
                    if ref_match:
                        info['upi_reference'] = int(ref_match.group(1))

                    if info:
                        transactions_found.append(info)
    
    # Return the found emails as JSON
    return jsonify(transactions_found)

@app.route('/fetch_new_bank_emails')
def fetch_new_bank_emails():
    # Authenticate and build the service
    service = quickstart.auth()
    # This function will authenticate the user and return a Gmail service instance.
    currentEpoch = int(time.time())
    pastHourEpoch = currentEpoch - 86400
    # Basic Gmail search query to find potential banking emails:
    # Searching for specific bank domains or keywords.
    query = '(from:@hdfcbank.com OR from:@icicibank.com OR from:@axisbank.com OR debited OR credited AND after:' + str(pastHourEpoch) + ')'
    
    # Retrieve message IDs matching the query
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])
    
    
    # For demonstration, we'll just gather all text parts we find
    transactions_found = []
    
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
        
        for part in payload_parts:
            data = part['body'].get('data')
            if data:
                decoded_text = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                # If it matches typical bank keywords, we consider it relevant
                if re.search(r'\b(debited|credited|transaction|account|bank)\b', decoded_text.lower()):
                    info = {}
                    info['subject'] = subject
                    info['type'] = re.search(r'\b(debited|credited)\b', decoded_text.lower()).group(0) if re.search(r'\b(debited|credited)\b', decoded_text.lower()) else None
                    amount_match = re.search(r'Rs\.?\s?(\d+(?:\.\d+))', decoded_text)
                    if amount_match:
                        info['amount'] = float(amount_match.group(1))

                    detail_match = re.search(
                        r'to\s+VPA\s+([\S]+)\s+(.*?)\s+on\s+(\d{2}-\d{2}-\d{2})',
                        decoded_text
                    )
                    if detail_match:
                        info['upi_id'] = detail_match.group(1)
                        info['receiver'] = detail_match.group(2)
                        info['class'] = classify.classify_transaction(detail_match.group(2))
                        info['date'] = detail_match.group(3)

                    ref_match = re.search(
                        r'UPI transaction reference number is\s+(\d+)',
                        decoded_text
                    )
                    if ref_match:
                        info['upi_reference'] = int(ref_match.group(1))

                    if info:
                        transactions_found.append(info)
    
    # Return the found emails as JSON
    return jsonify(transactions_found)

if __name__ == '__main__':
    app.run(debug=True)
