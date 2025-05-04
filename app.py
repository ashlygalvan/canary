from flask import Flask, request, render_template, redirect, url_for
import uuid
import json
from email.message import EmailMessage
from datetime import datetime

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