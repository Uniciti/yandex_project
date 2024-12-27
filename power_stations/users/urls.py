# users/urls.py
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/password/', views.password_change, name='password_change'),
    path('profile/<str:username>/', views.profile, name='profile'),
]