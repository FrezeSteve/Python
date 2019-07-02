from django.shortcuts import render,Http404,get_object_or_404
from django.views.generic import ListView,DetailView
from .models import Product

from cart.models import Cart

# Create your views here.
class ProductListView(ListView):
    def get_queryset(self,*args,**kwargs):
        request=self.request
        return Product.objects.all()


class ProductDetailView(DetailView):
    #queryset=Product.objects.all()

    def get_context_data(self,*args,**kwargs):
        context=super(ProductDetailView,self).get_context_data(*args,**kwargs)
        cart_obj,new_obj=Cart.objects.new_or_get(self.request)
        context['cart']=cart_obj
        return context

    def get_object(self,*args,**kwargs):
        request=self.request
        slug=self.kwargs.get('slug')
        #pk=self.kwargs.get('pk')
        try:
            instance=get_object_or_404(Product,slug=slug,active=True)
        except Product.DoesNotExist:
            raise Http404('Not Found...')
        except Product.MultipleObjectsReturned:
            qs=Product.objects.filter(slug=slug,active=True)
            instance=qs.first()
        except:
            raise Http404('UnKnown Error!!!')
        if instance is None:
            raise Http404('Product doesnt exist')
        return instance