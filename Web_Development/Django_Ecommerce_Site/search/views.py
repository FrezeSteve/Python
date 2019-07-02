from django.shortcuts import render
from django.db.models import Q
from django.views.generic import ListView,DetailView
from products.models import Product
# Create your views here.
class SearchProductListView(ListView):
    # def get_context_data(self,*args,**kwargs):
    #     context=super(SearchProductListView,self).get_context_data(*args,**kwargs)
    #     print(context)
    #     return context

    def get_queryset(self,*args,**kwargs):
        request=self.request
        method_dict=request.GET
        query=method_dict.get('q',None)
        if query is not None:
            return Product.objects.searches(query)
        return Product.objects.features()