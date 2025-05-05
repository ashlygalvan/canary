from flask import Flask, request, render_template, redirect, url_for
import uuid
import json
from email.message import EmailMessage
from datetime import datetime

app = Flask(__name__)
TOKENS = 'tokens.json'

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

if __name__ == "__main__":
    app.run(debug=True)