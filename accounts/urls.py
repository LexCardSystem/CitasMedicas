from django.urls import path
from django.contrib.auth import views as auth_views
from .views import RegisterView, profile_view, appointment_history_view, appointment_detail_view # Added new views

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'), # next_page can be set in settings.py
    path('profile/', profile_view, name='profile'),
    path('history/', appointment_history_view, name='appointment_history'),
    path('history/<int:appointment_id>/', appointment_detail_view, name='appointment_detail'),
]
