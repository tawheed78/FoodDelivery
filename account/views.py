from django.shortcuts import render, redirect
from django.http import HttpResponse

from account.utils import detectUser
from .forms import UserForm
from vendor.forms import VendorForm
from .models import User, UserProfile
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied

#Restricting vendor from accessing cust page
def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied

#Restricting cust from accessing vendor page
def check_role_cust(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied

def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in")
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            # Create the user using the form
            # password = form.cleaned_data['password']
            # user = form.save(commit=False)
            # user.set_password(password)
            # user.role = User.CUSTOMER
            # user.save()

            # Create the user using create_user method
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.role = User.CUSTOMER
            user.save()
            messages.error(request, 'Your account is created succesfully')
            return redirect('registerUser')
        else:
            print('invalid form')
            print(form.errors)
    else:
        form = UserForm()
    context = {
        'form': form,
    }
    return render(request, 'account/registerUser.html',context)


def registerVendor(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in")
        return redirect('dashboard')
    if request.method == 'POST':
       #store the data and create user
       form = UserForm(request.POST)
       v_form = VendorForm(request.POST, request.FILES)       #req.post is to collect data and to collect some sort of filees use request.files
       if form.is_valid() and v_form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.role = User.VENDOR
            user.save()
            vendor = v_form.save(commit=False)
            vendor.user = user
            user_profile = UserProfile.objects.get(user=user)       #get the user profile from the user.How it go created? well we have create a signals.py which will create the userprofile for the user on user.save trigger
            vendor.user_profile =user_profile
            vendor.save()
            messages.success(request, "Your account has been registered succesfully")
            return redirect('registerVendor')           
       else:
            print('invalid form')
            print(form.errors)
    else: 
        form = UserForm()
        v_form = VendorForm()                                  #combining both the vendor and user form
    context = {
        'form': form,
        'v_form' : v_form,                                 #using context to have multiple values.
    }

 
    return render(request, 'account/registerVendor.html',context)


def login(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in")
        return redirect('myAccount')
    elif request.method == 'POST':
        email = request.POST['email']                        #fetching from post
        password = request.POST['password']
        # in django we have in built authentication
        user = auth.authenticate(email = email, password = password)
        if user is not None:
            auth.login(request, user)          #auth will allow the user to login
            messages.success(request, 'Login Succesful')
            return redirect('myAccount')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')

    return render(request, 'account/login.html')

def logout(request):
    auth.logout(request)
    messages.info(request, "You have logged out")
    return redirect('login')

@login_required(login_url = 'login')                   #decorator so that only when u are logged in you can go to myAccount view
def myAccount(request):
    user = request.user
    redirectUrl = detectUser(user)
    return redirect(redirectUrl)

@login_required(login_url = 'login')
@user_passes_test(check_role_cust)
def custDashboard(request):
    return render(request, 'account/custDashboard.html')

@login_required(login_url = 'login')
@user_passes_test(check_role_vendor)
def vendorDashboard(request):
    return render(request, 'account/vendorDashboard.html')