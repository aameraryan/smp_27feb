from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        if hasattr(user, 'recruiter'):
            return (
                six.text_type(user.pk) + six.text_type(timestamp) +
                six.text_type(user.recruiter.email_confirmed)
            )
        elif hasattr(user, 'candidate'):
            return (
                six.text_type(user.pk) + six.text_type(timestamp) +
                six.text_type(user.candidate.email_confirmed)
            )
        else:
            pass


account_activation_token = AccountActivationTokenGenerator()
