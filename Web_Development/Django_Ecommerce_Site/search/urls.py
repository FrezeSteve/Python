from django.conf.urls import url
from . import views

urlpatterns=[
    url(r'^$',views.SearchProductListView.as_view(),name='default'),
]