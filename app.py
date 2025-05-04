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

def generate_token():
     token_id = str(uuid.uuid4())
     time = datetime.utcnow()
     formatted_time = time.strftime('%Y-%m-%d %H:%M:%S')
     token = load_token()
     token[token_id] = {"created_at": formatted_time}
     save_token(token)
     print("Generated token: {}".format(token_id))
     return token_id
