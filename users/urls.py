from django.urls import path
from . import views
from users import password_reset  # Import the password reset functions

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    # Add these two lines for forgot/reset password functionality
    path('forgot-password/', password_reset.forgot_password, name='forgot_password'),
    path('reset-password/<str:token>/', password_reset.reset_password, name='reset_password'),
]
