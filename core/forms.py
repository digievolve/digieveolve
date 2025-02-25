# core/forms.py
from django import forms

class ContactForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    subject = forms.ChoiceField(choices=[
        ('', 'Select a subject'),
        ('training', 'Training Programs'),
        ('consulting', 'Digital Transformation'),
        ('automation', 'Automation Solutions'),
        ('career', 'Career Development'),
        ('other', 'Other'),
    ])
    message = forms.CharField(widget=forms.Textarea)