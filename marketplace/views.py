from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from account.models import UserProfile

from orders.forms import OrderForm
from .models import Cart
from menu.models import Category, FoodItem

from vendor.models import Vendor, OpeningHour
from django.db.models import Prefetch
from marketplace.context_processors import get_cart_counter, get_cart_amounts
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from datetime import date, datetime

def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_count = vendors.count()
    context = {
        'vendors' : vendors,
        'vendor_count' : vendor_count,
    }
    return render(request, 'marketplace/listings.html',context)


def vendor_detail(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug = vendor_slug)
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'fooditems',
            queryset=FoodItem.objects.filter(is_available=True)
        )
    )
    opening_hours = OpeningHour.objects.filter(vendor=vendor).order_by('day','-from_hour')

    today_date = date.today()
    today = today_date.isoweekday()

    current_opening_hours = OpeningHour.objects.filter(vendor=vendor, day=today)

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items=None
    context = {
        'vendor':vendor,
        'categories':categories,
        'cart_items':cart_items,
        'opening_hours':opening_hours,
        'current_opening_hours':current_opening_hours,
        
    }
    return render(request, 'marketplace/vendor_detail.html',context)


def add_to_cart(request, food_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            #checking if food exists
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                #check if food is already added
                try:
                    chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    #increase cart
                    chkCart.quantity += 1
                    chkCart.save()
                    return JsonResponse({'status':'Success','message':'quantity added','cart_counter':get_cart_counter(request), 'qty': chkCart.quantity,'cart_amount':get_cart_amounts(request)})
                except:
                    chkCart=Cart.objects.create(user=request.user, fooditem=fooditem, quantity=1)
                    return JsonResponse({'status':'Success','message':'food item added to cart','cart_counter':get_cart_counter(request),'qty': chkCart.quantity, 'cart_amount':get_cart_amounts(request)})
            except:
                return JsonResponse({'status':'Success','message':'Food does not exist'})
        else:
            return JsonResponse({'status':'Success','message':'Invalid request'})
    else:
        return JsonResponse({'status':'login_required','message':'Please login before proceeding.'})



def decrease_cart(request, food_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            #checking if food exists
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                #check if food is already added
                try:
                    chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    if chkCart.quantity > 1:
                        #decrease cart
                        chkCart.quantity -= 1
                        chkCart.save()
                    else:
                        chkCart.delete()
                        chkCart.quantity=0
                    return JsonResponse({'status':'Success','cart_counter':get_cart_counter(request), 'qty': chkCart.quantity,'cart_amount':get_cart_amounts(request)})
                except:
                    return JsonResponse({'status':'Failed','message':'You dont have this item in cart'})
            except:
                return JsonResponse({'status':'Failed','message':'Food does not exist'})
        else:
            return JsonResponse({'status':'Failed','message':'Invalid request'})
    else:
        return JsonResponse({'status':'login_required','message':'Please login before proceeding.'})


@login_required(login_url = 'login')
def cart(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    context = {
        'cart_items':cart_items,
    }
    return render(request, 'marketplace/cart.html',context)



def delete_cart(request,cart_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                # check if cart item exists
                cart_item = Cart.objects.get(user=request.user, id=cart_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse({'status':'Success','message':'Cart Item deleted','cart_counter':get_cart_counter(request),'cart_amount':get_cart_amounts(request)})
            except:
                return JsonResponse({'status':'Failed','message':'Food does not exist'})
        else:
            return JsonResponse({'status':'Failed','message':'Invalid request'})


def search(request):
    if not 'address' in request.GET:
        return redirect('marketplace')
    else:
        # address = request.GET['address']
        # latitude = request.GET['lat']
        # longitude = request.GET['lng']
        # radius = request.GET['radius']
        keyword = request.GET['keyword']

        #get v_id for fooditem user needs
        fetch_vendor_by_fooditems = FoodItem.objects.filter(food_title__icontains=keyword, is_available=True).values_list('vendor',flat=True)

        vendors = Vendor.objects.filter(Q(id__in=fetch_vendor_by_fooditems) | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active = True))

        # vendors = Vendor.objects.filter(vendor_name__icontains=keyword, is_approved=True, user__is_active = True)shifted up
        vendor_count = vendors.count()
        context={
            'vendors':vendors,
            'vendor_count':vendor_count,
        }
        return render(request, 'marketplace/listings.html',context)

@login_required(login_url='login')
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace')
    
    user_profile = UserProfile.objects.get(user=request.user)
    default_values = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'phone': request.user.phonenumber,
        'email': request.user.email,
        'address': user_profile.address,
        'country': user_profile.country,
        'state': user_profile.state,
        'city': user_profile.city,
        'pin_code': user_profile.pin_code,
    } 
    form = OrderForm(initial=default_values)
    context = {
        'form':form,
        'cart_items':cart_items,
    }
    return render(request, 'marketplace/checkout.html',context)