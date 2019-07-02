from django.conf.urls import url
from . import views

urlpatterns=[
    url(r'^$',views.ProductListView.as_view(),name='home'),
    url(r'^(?P<slug>[\w-]+)/$',views.ProductDetailView.as_view(),name='detail'),
]