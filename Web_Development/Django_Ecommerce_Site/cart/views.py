from django.shortcuts import render,redirect
from .models import Cart
from orders.models import Order
from products.models import Product
from accounts.forms import LoginForm,GuestForm
from addresses.forms import AddressForm
from addresses.models import Address
from accounts.models import GuestEmail
from billing.models import BillingProfile
# Create your views here.

def cart_home(request):
    cart_obj,new_obj=Cart.objects.new_or_get(request)
    return render(request,'cart/home.html',{"cart":cart_obj})

def cart_update(request):
    product_id=request.POST.get('product_id')
    if product_id is not None:
        try:
            product_obj=Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            print('Product Error!')
            return redirect('cart:home')
        # except:
        #     print('Unknown Error!!')
        #     return redirect('cart:home')
        cart_obj,new_obj=Cart.objects.new_or_get(request)
        if product_obj in cart_obj.products.all():
            cart_obj.products.remove(product_obj)
        else:
            cart_obj.products.add(product_obj)
    else:
        print('hacked')
    return redirect('cart:home')

def checkout_home(request):
    cart_obj,cart_created=Cart.objects.new_or_get(request)
    order_obj=None
    address_qs=None
    if cart_created or cart_obj.products.count()==0:
        return redirect('cart:home')

    login_form=LoginForm()
    guest_form=GuestForm()
    address_form=AddressForm()
    
    shipping_address_id=request.session.get('shipping_address_id',None)
    billing_address_id=request.session.get('billing_address_id',None)

    billing_profile,billing_profile_created=BillingProfile.objects.new_or_get(request)

    if billing_profile is not None:
        if request.user.is_authenticated():
            address_qs=Address.objects.filter(billing_profile=billing_profile)
        order_obj,order_obj_created=Order.objects.new_or_get(billing_profile,cart_obj)
        if shipping_address_id:
            order_obj.shipping_address=Address.objects.get(id=shipping_address_id)  
            del request.session['shipping_address_id']
        if billing_address_id:
            order_obj.billing_address=Address.objects.get(id=billing_address_id) 
            del request.session['billing_address_id']
        if billing_address_id or shipping_address_id:
            order_obj.save()

    

    if request.method == "POST":
        is_done=order_obj.check_done()
        if is_done:
            order_obj.mark_paid()
            del request.session['cart_id']
            return redirect('/products')
            
    context={
        'object':order_obj,
        'billing_profile':billing_profile,
        'login_form':login_form,
        'guest_form':guest_form,
        'address_form':address_form,
        'address_qs':address_qs,
    }
    return render(request,'cart/checkout.html',context)