from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from . models import UserProfile, UserAddress
from . forms import UserProfileForm
from django.forms import BaseInlineFormSet,inlineformset_factory
from django.contrib import messages
from django import forms
from django.contrib.auth.models import User
from . forms import AddressForm
# Create your views here.
@login_required
def profile_view(request):
    addresses = request.user.addresses.all()
    form = AddressForm()

    return render(request, 'profile.html', {
        'addresses': addresses,
        'form': form,
    })
    
    
# @login_required
# def profile_edit_view(request):
#     profile, created = UserProfile.objects.get_or_create(user=request.user)
    
#     AddressFormSet = inlineformset_factory(
#         User, UserAddress,
#         fields=('address_line1', 'building_number', 'floor', 'apartment_number', 'city', 'address_notes'),
#         extra=1,
#         can_delete=True,
#         widgets={
#             'address_line1': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded'}),
#             'building_number': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded'}),
#             'floor': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded'}),
#             'apartment_number': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded'}),
#             'city': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded'}),
#             'address_notes': forms.Textarea(attrs={'rows': 2, 'class': 'w-full px-3 py-2 border border-gray-300 rounded'}),
#         }
#     )

#     if request.method == 'POST':
#         form = UserProfileForm(request.POST, request.FILES, instance=profile)
#         formset = AddressFormSet(request.POST, instance=request.user)
#         if form.is_valid() and formset.is_valid():
#             form.save()
#             formset.save()
#             messages.success(request, "✅ Profile updated successfully!")
#             return redirect('profile')
#         else:
#             messages.error(request, "❌ Please correct the errors below.")
#     else:
#         form = UserProfileForm(instance=profile)
#         formset = AddressFormSet(instance=request.user)

#     return render(request, 'profile_edit.html', {
#         'form': form,
#         'formset': formset,
#     })

# Custom formset to skip validation for empty forms

@login_required
def profile_edit_view(request):
    profile = get_object_or_404(UserProfile,user=request.user)



    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()

            messages.success(request, "✅ Profile updated successfully!")
            return redirect('profile')
        else:
            messages.error(request, "❌ Please correct the errors below.")
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'profile_edit.html', {
        'form': form,
    })
    
@login_required
def address_add_view(request):
    address_count = UserAddress.objects.filter(user=request.user).count()
    if request.method == 'POST':
        if address_count >= 3:
            messages.error(request, "❌ You have reached the maximum number of addresses (5). Please delete an existing address before adding a new one.")
            return redirect('profile')
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, "✅ Address added successfully!")
            return redirect('profile')
        else:
            messages.error(request, "❌ Please correct the errors below.")
    else:
        form = AddressForm()

    return render(request, 'address_add.html', {
        'form': form,
    })
    
@login_required
def address_edit_view(request, address_id):
        address = get_object_or_404(UserAddress, id=address_id, user=request.user)

        if request.method == 'POST':
            form = AddressForm(request.POST, instance=address)
            if form.is_valid():
                form.save()
                messages.success(request, "✅ Address updated successfully!")
                return redirect('profile')
            else:
                messages.error(request, "❌ Please correct the errors below.")
        else:
            form = AddressForm(instance=address)

        return render(request, 'address_edit.html', {
            'form': form,
        })  
        
@login_required
def address_delete_view(request, address_id):
    address = get_object_or_404(UserAddress, id=address_id, user=request.user)
    address.delete()
    messages.success(request, "✅ Address deleted successfully!")
    return redirect('profile')
