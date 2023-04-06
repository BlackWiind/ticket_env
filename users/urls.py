from django.urls import path
from . import views

urlpatterns = [
    path('register-customer/', views.register_custumer, name='register-customer'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
]