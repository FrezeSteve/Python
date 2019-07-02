from django.conf.urls import url
from . import views

urlpatterns=[
    url(r'^create/$',views.checkout_address_create_view,name='checkout_address_create'),
    url(r'^reuse/$',views.checkout_address_reuse_view,name='checkout_address_reuse'),
]