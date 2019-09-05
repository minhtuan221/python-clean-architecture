"""
    flaskext.mail
    ~~~~~~~~~~~~~

    Flask extension for sending email.

    :copyright: (c) 2010 by Dan Jacob.
    :license: BSD, see LICENSE for more details.
"""
from contextlib import contextmanager

from .connection import Connection
from .message import Message, Attachment, BadHeaderError
from .signals import email_dispatched


class Mail(object):
    """
    Manages email messaging

    :param app: Flask instance
    """

    def __init__(self, mail_username, mail_password, app=None, mail_server='127.0.0.1', mail_port=25,
                 mail_use_TLS=False, mail_use_SSL=False, mail_debug=False, default_max_emails=None,
                 mail_suppress_end=False, mail_fail_silently=True):
        """
        Initializes your mail settings from the application
        settings.

        You can use this if you want to set up your Mail instance
        at configuration time.

        :param app: Flask application instance
        """

        self.server = mail_server
        self.username = mail_username
        self.password = mail_password
        self.port = mail_port
        self.use_tls = mail_use_TLS
        self.use_ssl = mail_use_SSL
        self.debug = int(mail_debug)
        self.max_emails = default_max_emails
        self.suppress = mail_suppress_end
        self.fail_silently = mail_fail_silently

        self.suppress = self.suppress or app.testing
        self.app = app

    @contextmanager
    def record_messages(self):
        """
        Records all messages. Use in unit tests for example::

            with mail.record_messages() as outbox:
                response = app.test_client.get("/email-sending-view/")
                assert len(outbox) == 1
                assert outbox[0].subject == "testing"

        You must have blinker installed in order to use this feature.
        :versionadded: 0.4
        """

        if not email_dispatched:
            raise RuntimeError("blinker must be installed")

        outbox = []

        def _record(message, app):
            outbox.append(message)

        email_dispatched.connect(_record)

        try:
            yield outbox
        finally:
            email_dispatched.disconnect(_record)

    def send(self, message):
        """
        Sends a single message instance. If TESTING is True
        the message will not actually be sent.

        :param message: a Message instance.
        """

        with self.connect() as connection:
            message.send(connection)

    def send_message(self, *args, **kwargs):
        """
        Shortcut for send(msg).

        Takes same arguments as Message constructor.

        :versionadded: 0.3.5
        """

        self.send(Message(*args, **kwargs))

    def connect(self, max_emails=None):
        """
        Opens a connection to the mail host.

        :param max_emails: the maximum number of emails that can
                           be sent in a single connection. If this
                           number is exceeded the Connection instance
                           will reconnect to the mail server. The
                           DEFAULT_MAX_EMAILS config setting is used
                           if this is None.
        """
        return Connection(self, max_emails)
