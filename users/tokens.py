from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type

class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{timestamp}{user.is_verified}"

email_verification_token = EmailVerificationTokenGenerator()

