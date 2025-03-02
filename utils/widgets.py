from django import forms
from django.conf import settings

class CloudflareTurnstileWidget(forms.Widget):
    template_name = 'widgets/turnstile.html'

    def __init__(self, attrs=None):
        if attrs is None:
            attrs = {}
        attrs['site_key'] = getattr(settings, 'CLOUDFLARE_TURNSTILE_SITE_KEY', '')
        super().__init__(attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['attrs']['site_key'] = self.attrs['site_key']
        return context