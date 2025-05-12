Objective: Create a canary server that will notify the user when their token that was created was triggered. Currently only uses an embedded link for token.

Requirments: 
- must be using python for this program
- must download the following modules:
    - pip install flask
    - pip install python-dotenv
- create a .env file (is is where your notifications will be sent by)
    - eg. 
        - EMAIL_USER=youremail@gmail.com
        - EMAIL_PASS=your_email_app_password