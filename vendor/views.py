from django.shortcuts import get_object_or_404, redirect, render

from account.views import check_role_vendor

from .forms import VendorForm

from account.forms import UserProfileForm

from account.models import UserProfile
from .models import Vendor

from django.contrib import messages

from django.contrib.auth.decorators import login_required, user_passes_test

# Create your views here.
@login_required(login_url = 'login')
@user_passes_test(check_role_vendor)
def vprofile(request):
    #This is known as instance . we will pass this inside the forms thus getting the already entered data
    profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)

    # we did the necessary changes in the views and added the input fields for the form updation and affter that to update the data in the databse we will do the following steps
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST,request.FILES,instance=profile) #FILES for uploading images
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)
        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.success(request, 'Profile has been updated succesfully')
            return redirect('vprofile')
        else:
            print(profile_form.errors)
            print(vendor_form.errors)
    else:
        profile_form = UserProfileForm(instance=profile)
        vendor_form = VendorForm(instance=vendor)
    
    context = {
        'profile_form': profile_form,
        'vendor_form': vendor_form,
        'profile':profile,
        'vendor':vendor,
    }
    return render(request,'vendor/vprofile.html',context)
    #now this views taken from form will be given as input fields in the vprofile.html using static loader