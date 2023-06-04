from itsdangerous import URLSafeTimedSerializer


class TokenFactory(object):

    def __init__(self, secret_key: str, security_salt: str):
        self.secret_key = secret_key
        self.security_salt = security_salt

    def generate_confirmation_token(self, email: str):
        serializer = URLSafeTimedSerializer(self.secret_key)
        return str(serializer.dumps(email, salt=self.security_salt))

    def confirm_token(self, token, expiration=3600):
        serializer = URLSafeTimedSerializer(self.secret_key)
        try:
            email: str = serializer.loads(
                token,
                salt=self.security_salt,
                max_age=expiration
            )
        except Exception as e:
            raise e
        return email

