from django import forms
from .models import UserProfile,UserAddress


# Edit profile + addresses
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['real_name', 'main_phone', 'secondary_phone', 'image']
        widgets = {
            'real_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-red focus:border-brand-red'}),
            'main_phone': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-red focus:border-brand-red'}),
            'secondary_phone': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-red focus:border-brand-red'}),
        }
        
        
class AddressForm(forms.ModelForm):
    class Meta:
        model = UserAddress
        fields = ['address_line1', 'building_number', 'floor', 'apartment_number', 'city', 'address_notes']
        widgets = {
            'address_line1': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-red focus:border-brand-red'}),
            'building_number': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-red focus:border-brand-red'}),
            'floor': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-red focus:border-brand-red'}),
            'apartment_number': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-red focus:border-brand-red'}),
            'city': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-red focus:border-brand-red'}),
            'address_notes': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-red focus:border-brand-red'}),
        }