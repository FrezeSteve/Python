from django.shortcuts import render,redirect
from .forms import AddressForm
from .models import Address
from django.utils.http import is_safe_url
from billing.models import BillingProfile
# Create your views here.

def checkout_address_reuse_view(request):
    print('Working')
    if request.user.is_authenticated():
        next_=request.GET.get('next')
        next_post=request.POST.get('next')
        redirect_path=next_ or next_post or None
        if request.method=='POST': 
            print(request.POST)
            shipping_address=request.POST.get('shipping_address',None)
            address_type=request.POST.get('address_type','shipping')
            billing_profile,billing_profile_created=BillingProfile.objects.new_or_get(request)
            print(shipping_address," :in the address view")
            if shipping_address is not None:
                qs=Address.objects.filter(billing_profile=billing_profile,id=shipping_address)
                print(qs,' :in the address view')
                if qs.exists():
                    request.session[address_type + '_address_id']=shipping_address
                if is_safe_url(redirect_path,request.get_host()):
                    return redirect(redirect_path)
    return redirect('cart:checkout')

def checkout_address_create_view(request):
    form=AddressForm(request.POST or None)
    next_=request.GET.get('next')
    next_post=request.POST.get('next')
    redirect_path=next_ or next_post or None
    if form.is_valid():
        print(request.POST)
        billing_profile,billing_profile_created=BillingProfile.objects.new_or_get(request)
        if billing_profile is not None:
            address_type=request.POST.get('address_type','shipping')
            instance=form.save(commit=False)
            instance.billing_profile=billing_profile
            instance.address_type=request.POST.get('address_type','shipping')
            instance.save()

            request.session[address_type + '_address_id']=instance.id
            print(address_type + '_address_id')

        if is_safe_url(redirect_path,request.get_host()):
            return redirect(redirect_path)
        else:
            return redirect('cart:checkout')

    return redirect('cart:checkout')