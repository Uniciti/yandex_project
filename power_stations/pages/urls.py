# pages/urls.py
from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'), 
    path('help/', views.HelpView.as_view(), name='help'),
]