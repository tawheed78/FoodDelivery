from django.shortcuts import get_object_or_404, redirect, render

from account.views import check_role_vendor
from menu.forms import CategoryForm, FoodItemForm
from menu.models import Category, FoodItem

from .forms import VendorForm

from account.forms import UserProfileForm

from account.models import UserProfile
from .models import Vendor

from django.contrib import messages

from django.contrib.auth.decorators import login_required, user_passes_test
from django.template.defaultfilters import slugify

def get_vendor(request):
    vendor = Vendor.objects.get(user=request.user)
    return vendor

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

@login_required(login_url = 'login')
@user_passes_test(check_role_vendor)
def menu_builder(request):
    vendor = get_vendor(request)
    categories = Category.objects.filter(vendor=vendor).order_by('created_at')
    context = {
        'categories':categories,
    }
    return render(request, 'vendor/menu_builder.html',context)



@login_required(login_url = 'login')
@user_passes_test(check_role_vendor)
def fooditems_by_category(request, pk=None):
    vendor =  get_vendor(request)
    category = get_object_or_404(Category, pk=pk)
    fooditems = FoodItem.objects.filter(vendor=vendor,category=category)
    context = {
        'fooditems' : fooditems,
        'category' : category,
    }
    return render(request, 'vendor/fooditems_by_category.html',context)

@login_required(login_url = 'login')
@user_passes_test(check_role_vendor)
def add_category(request):
    if request.method=='POST':           #we have passed request as post in addcate form so if the req method here is also post then we can retrieve data
        form = CategoryForm(request.POST)     #request.post implies that we get all the data that has been entered in the form.
        if form.is_valid():
            category_name= form.cleaned_data['category_name']   #from the cleaned data we can accesss the cat name
            category = form.save(commit=False) #form is ready to save but not yet saved
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name)
            form.save()                      #if the data is valid then we will save the form
            messages.success(request, "Category added succesfully")
            return redirect('menu_builder')
        else:
            print(form.errors)
    else:
        form = CategoryForm()               #if req is not post then we will simply load the form
    context = {
        'form':form
    }
    return render(request, 'vendor/add_category.html',context)

@login_required(login_url = 'login')
@user_passes_test(check_role_vendor)
def edit_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    if request.method=='POST':           
        form = CategoryForm(request.POST, instance=category)     
        if form.is_valid():
            category_name= form.cleaned_data['category_name']   
            category = form.save(commit=False) 
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name)
            form.save()                    
            messages.success(request, "Category updated succesfully")
            return redirect('menu_builder')
        else:
            print(form.errors)
    else:
        form = CategoryForm(instance=category)               
    context = {
        'form':form,
        'category':category,
    }
    
    return render(request, 'vendor/edit_category.html',context)


@login_required(login_url = 'login')
@user_passes_test(check_role_vendor)
def delete_category(request,pk=None):
    category = get_object_or_404(Category,pk=pk)
    category.delete()
    messages.success(request,'Category has been deleted')
    return redirect('menu_builder')


@login_required(login_url = 'login')
@user_passes_test(check_role_vendor)
def add_food(request):
    if request.method=='POST':           
        form =FoodItemForm(request.POST,request.FILES)   
        if form.is_valid():
            foodtitle = form.cleaned_data['food_title']   
            food = form.save(commit=False)
            food.vendor = get_vendor(request)
            food.slug = slugify(foodtitle)
            form.save()                      
            messages.success(request, "Food Item added succesfully")
            return redirect('fooditems_by_category',food.category.id)
        else:
            print(form.errors)
    else:
        form = FoodItemForm()
        #
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
    context = {
        'form':form,
    }
    return render(request, 'vendor/add_food.html',context)



@login_required(login_url = 'login')
@user_passes_test(check_role_vendor)
def edit_food(request, pk=None):
    food = get_object_or_404(FoodItem, pk=pk)
    if request.method=='POST':           
        form = FoodItemForm(request.POST,request.FILES, instance=food)     
        if form.is_valid():
            foodtitle= form.cleaned_data['food_title']   
            food = form.save(commit=False) 
            food.vendor = get_vendor(request)
            food.slug = slugify(foodtitle)
            form.save()                    
            messages.success(request, "Food updated succesfully")
            return redirect('fooditems_by_category',food.category.id)
        else:
            print(form.errors)
    else:
        form = FoodItemForm(instance=food)   
        #
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))            
    context = {
        'form':form,
        'food':food,
    } 
    return render(request, 'vendor/edit_food.html',context)



@login_required(login_url = 'login')
@user_passes_test(check_role_vendor)
def delete_food(request,pk=None):
    food = get_object_or_404(FoodItem,pk=pk)
    food.delete()
    messages.success(request,'Food Item has been deleted')
    return redirect('fooditems_by_category',food.category.id)

