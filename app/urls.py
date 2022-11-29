from unicodedata import name
from django.urls import path
from app import views

urlpatterns = [
    path('', views.home, name="home"),
    path('register', views.register, name='register'),
    path('login', views.Login, name='login'),
    path('logout', views.Logout, name='logout'),
    path('activate/<uidb64>/<token>', views.activate, name='activate')
]