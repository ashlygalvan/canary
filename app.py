from flask import Flask, request, render_template
import uuid
import json
import os
import smtplib
from email.message import EmailMessage
from datetime import datetime
from dotenv import load_dotenv

app = Flask(__name__)
TOKENS = 'tokens.json'
load_dotenv()

def load_token():
    try:
        with open(TOKENS, 'r') as token_file:
            return json.load(token_file)
    except FileNotFoundError:
        return {}
    
def save_token(token):
        with open(TOKENS, 'w') as token_file:
            json.dump(token, token_file, indent=1)

@app.route('/generate', methods=['POST'])
def generate_token():
     email = request.form['email']
     token_id = str(uuid.uuid4())
     time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    
     token = load_token()
     token[token_id] = {"created_at": time, "email": email}
     save_token(token)

     return f"Your canary token is: <strong>{token_id}</strong><br>Email alerts will go to: <strong>{email}</strong>"

@app.route('/')
def index():
     return render_template("index.html")

@app.route('/token/<token_id>')
def trigger(token_id):
     token = load_token()

     #our error handling
     if token_id not in token:
          print("Not a valid token."), 404

     user_email = token[token_id]['email']
     triggered_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
     ip = request.remote_addr
     user_agent = request.headers.get('User-Agent', 'Unknown')
     token[token_id]['last_triggered'] = {
        'timestamp': triggered_time,
        'ip': ip,
        'user_agent': user_agent
    }
     save_token(token)
     try:
        msg = EmailMessage()
        msg['Subject'] = 'Canary Token was Triggered'
        msg['From'] = f"Canary Alert <{user_email}>"

        msg['To'] = user_email
        msg.set_content(f"""
We would like to notify you that your token was triggered!
                        
Token ID: {token_id}

Time of trigger: {triggered_time}

IP Address that triggered the token: {ip}

From what user agent it came from: 

{user_agent}

If this is something that unexpectly done, review your systems.

- Canary Token Notifications
        """)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(os.getenv('EMAIL_USER'), os.getenv('EMAIL_PASS'))
            smtp.send_message(msg)

        return f"Token triggered! An alert was sent to {user_email}."
     except Exception as e:
        return f"Token triggered, but failed to send email: {str(e)}"



if __name__ == "__main__":
    app.run(debug=True)