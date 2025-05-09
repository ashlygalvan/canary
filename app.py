from flask import Flask, request, render_template, send_file, url_for
import uuid
import json
import os
import smtplib
import tempfile
from email.message import EmailMessage
from datetime import datetime
from dotenv import load_dotenv
from fpdf import FPDF

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
     name_of_token = request.form['name_of_token']
     email = request.form['email']
     token_type = request.form['token_type']
     token_id = str(uuid.uuid4())
     time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    
     token = load_token()
     token[token_id] = {"created_at": time, 
                        "email": email, 
                        "name_of_token": name_of_token,
                        "token_type": token_type}
     save_token(token)

     return render_template('token_page.html', token_id=token_id, email=email, name_of_token=name_of_token, token_type=token_type)

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
     name_of_token = token[token_id]['name_of_token']
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
        msg.set_content("Your token was triggered. Please use an email client that supports HTML to see full details.", subtype='plain')

        html_content = f"""
<html>
  <body style="font-family: 'Georgia', serif; color: #333;">
    <h2 style="color: #b22222;">Canary Token Triggered</h2>
    <p>We would like to notify you that your token was triggered!</p>

    <p><strong>Name of Token:</strong> {name_of_token}</p>
    <p><strong>Token ID:</strong> {token_id}</p>
    <p><strong>Time of Trigger:</strong> {triggered_time}</p>
    <p><strong>IP Address:</strong> {ip}</p>
    <p><strong>User Agent:</strong>{user_agent}</p>

    <p>If this was not expected, please review your systems immediately.</p>
    <br>
    <hr>
    <p style="font-size: 0.9em; color: #777;">– Canary Token Notifications</p>
  </body>
</html>
"""

        msg.add_alternative(html_content, subtype='html')
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(os.getenv('EMAIL_USER'), os.getenv('EMAIL_PASS'))
            smtp.send_message(msg)

        return f"Token triggered! An alert was sent to {user_email}."
     except Exception as e:
        return f"Token triggered, but failed to send email: {str(e)}"

@app.route('/generate_doc/<token_id>', methods=['GET'])
def generate_doc(token_id):
    return f"This would generate a Word Doc for token: {token_id}"

@app.route('/generate_image/<token_id>', methods=['GET'])
def generate_image(token_id):
    return f"This would generate an image for token: {token_id}"



if __name__ == "__main__":
    app.run(debug=True)