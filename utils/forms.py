from django import forms
from .widgets import CloudflareTurnstileWidget

class TurnstileMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['captcha'] = forms.CharField(widget=CloudflareTurnstileWidget(), required=True)

    def clean_captcha(self):
        import requests
        from django.conf import settings

        captcha_response = self.cleaned_data.get('captcha')
        secret_key = settings.CLOUDFLARE_TURNSTILE_SECRET_KEY
        verify_url = 'https://challenges.cloudflare.com/turnstile/v0/siteverify'

        response = requests.post(verify_url, data={
            'secret': secret_key,
            'response': captcha_response,
        })
        result = response.json()

        if not result.get('success'):
            raise forms.ValidationError('Invalid CAPTCHA. Please try again.')

        return captcha_response