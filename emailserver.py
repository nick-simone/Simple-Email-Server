from flask import Flask, request
import json
import boto3
import sqlite3
from requests.models import Response

app = Flask(__name__)

class EmailClientFactory:
    def getEmailClient(self, from_address, to_address, subject, body_text, body_html):
        
        with open("config.json", "r") as f:
            config = json.load(f)

        if config["SERVICE"] == "AWS":
            return AWSEmailClient(from_address, to_address, subject, body_text, body_html)
        elif config["SERVICE"] == "Test":
            return TestEmailClient(from_address, to_address, subject, body_text, body_html)

class EmailClient:
    def __init__(self, from_address, to_address, subject, body_text, body_html):
        self.from_address = from_address
        self.to_address = to_address
        self.subject = subject
        self.body_text = body_text
        self.body_html = body_html

class AWSEmailClient(EmailClient):
    def __init__(self, from_address, to_address, subject, body_text, body_html):
        super().__init__(from_address, to_address, subject, body_text, body_html)
        self._client = boto3.client(
            "ses",
            "id",
            "secret_key"
        )
    def send_email(self):
        response = self._client.send_email(Destination={
        'ToAddresses': [
            self.to_address
        ],
    },
    Message={
        'Body': {
            'Html': {
                'Charset': "utf-8",
                'Data': self.body_html,
            },
            'Text': {
                'Charset': "utf-8",
                'Data': self.body_text,
            },
        },
        'Subject': {
            'Charset': "utf-8",
            'Data': self.subject,
        },
    },
    Source=self.from_address)

        return response

class TestEmailClient(EmailClient):
    def __init__(self, from_address, to_address, subject, body_text, body_html):
        super().__init__(from_address, to_address, subject, body_text, body_html)

    def send_email(self):
        return create_response(200, b'{ "status" : "success: email sent" }')

def create_response(status_code, content):
    response = Response()
    response.status_code = status_code
    response._content = content
    return response

@app.route("/send-email", methods = ["POST"])
def send_email():
    
    from_address = request.args.get("from")
    to_address = request.args.get("to")
    subject = request.args.get("subject")
    body_text = request.args.get("body_text")
    body_html = request.args.get("body_html")

    # before sending, check database for blacklisted email
    con = sqlite3.connect("blacklist.db")
    cur = con.cursor()

    cur.execute("SELECT * FROM blacklisted_emails WHERE email = ?", (from_address,))

    if cur.fetchone():
        return create_response(400, b'{ "status" : "email blacklisted; not sent" }').json()

    cur.close()

    emailClientFactory = EmailClientFactory()
    client = emailClientFactory.getEmailClient(from_address, to_address, subject, body_text, body_html)
    response = client.send_email()

    return response.json()

@app.route("/bounced-email", methods = ["POST"])
def bounced_email():
    email_address = request.args.get("email_address")

    con = sqlite3.connect("blacklist.db")
    cur = con.cursor()

    # put into database
    cur.execute("SELECT email FROM blacklisted_emails WHERE email=?", (email_address,))

    if cur.fetchone():
        response = create_response(400,  b'{ "status" : "failure - email already blacklisted" }')
    else:    
        cur.execute("INSERT INTO blacklisted_emails (email) VALUES (?)", (email_address,))
        con.commit()
        response = create_response(200,  b'{ "status" : "success - email added to blacklist" }')

    cur.close()

    return response.json()
    
if __name__ == "__main__":
    app.run(debug=True, port=80, host="0.0.0.0")