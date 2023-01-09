from django.urls import path
from account import views as AccountViews
from . import views

urlpatterns = [
    path('', AccountViews.custDashboard, name='customer'),
    path('profile/', views.cprofile, name='cprofile'),
]