from django.urls import path
from .views import generate_certificate_pdf_view, verify_certificate_qr_view

urlpatterns = [
    path('generate/<int:certificate_id>/pdf/', generate_certificate_pdf_view, name='generate_certificate_pdf'),
    # Ensure certificate_identifier in the path is treated as UUID
    path('verify/<uuid:certificate_identifier>/', verify_certificate_qr_view, name='verify_certificate_qr'),
]
