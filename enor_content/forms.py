from django import forms
from . models import Contact_us,Newsletter



class ContactForm(forms.ModelForm):
    class Meta:
        model =Contact_us
        exclude = ['submitted_at']
        widgets = {
            'name':forms.TextInput(attrs={"placeholder":"enter your name","class":"form-textarea w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-red focus:border-brand-red"}),
            'email':forms.TextInput(attrs={"placeholder":"your@email.com"}),
            'subject':forms.TextInput(attrs={"placeholder":"How can we help?"}),
            'message':forms.TextInput(attrs={"placeholder":"Tell us more...","class":"form-textarea w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-red focus:border-brand-red","rows":5}),
        }
        
class NesletterForm(forms.ModelForm):
    class Meta:
        model =Newsletter
        fields = ['email']
        widgets = {
            'email':forms.TextInput(attrs={"placeholder":"your@email.com"}),
        }