from django import forms
from django.conf import settings

class CloudflareTurnstileWidget(forms.Widget):
    template_name = 'widgets/turnstile.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['site_key'] = settings.CLOUDFLARE_TURNSTILE_SITE_KEY
        return context