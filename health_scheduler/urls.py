from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('scheduling/', include('scheduling.urls')),
    path('certificates/', include('certificates.urls')), # Added certificates URLs
    path('', auth_views.LoginView.as_view(template_name='registration/login.html'), name='root'), # Keep root as login for now
]
