from django.urls import path,include
from . import views
from account import views as AccountView


urlpatterns= [
    path('', AccountView.vendorDashboard, name = 'vendor'),
    path('profile/', views.vprofile, name='vprofile'),
]