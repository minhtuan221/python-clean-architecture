from app.infrastructure.smtp import Mail, create_message
from app.pkgs.token import TokenFactory
from flask import render_template


class EmailService(object):

    token_factory: TokenFactory

    def __init__(self, mail: Mail, default_mail_sender: str, token: TokenFactory):
        self.mail = mail
        self.mail_sender = default_mail_sender
        self.token_factory = token

    def send_email(self, to: str, subject: str, template, sender=None):
        msg = create_message(sender_email=sender or self.mail_sender, receiver_email=to, subject=subject, html_body=template)
        self.mail.send(msg)

    def send_confirm_email(self, email: str, confirm_url: str, template):
        token = self.token_factory.generate_confirmation_token(email)
        confirm_url = confirm_url + str(token)
        html = render_template(template, confirm_url=confirm_url)  # 'user/activate.html'
        subject = "Please confirm your email"
        self.send_email(email, subject, html)

    def confirm_email(self, token: str) -> str:
        return self.token_factory.confirm_token(token)

    def send_reset_password(self, email: str, reset_password: str, template='user/new_password.html'):
        token = self.token_factory.generate_confirmation_token(email)
        html = render_template(template, password=reset_password)
        subject = "Reset password"
        self.send_email(email, subject, html)
