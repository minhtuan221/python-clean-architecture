import smtplib
import ssl
from email.message import Message
from typing import List


def create_message(sender_email: str, receiver_email: str, subject: str, html_body):
    message = Message()
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email
    message.add_header('Content-Type', 'text/html')
    message.set_payload(html_body)
    return message


class Mail(object):

    def __init__(self, sender_email: str, sender_password: str, port=456, smtp_server="smtp.gmail.com"):
        self.sender_email = sender_email
        self.password = sender_password
        self.port = port  # For SSL
        self.smtp_server = smtp_server

    def send(self, message: Message):
        # Create secure connection with server and send email
        sender_email = message["From"]
        receiver_email = message["To"]
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(self.smtp_server, self.port, context=context) as server:
            server.login(self.sender_email, self.password)
            server.sendmail(sender_email, receiver_email, message.as_string())

    def create_message(self, receiver_email: str, subject: str, html_body):
        return create_message(self.sender_email, receiver_email, subject, html_body)
