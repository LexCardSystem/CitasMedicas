from django.urls import path
from .views import list_centers_view, list_services_at_center_view, view_available_slots_view # Removed book_appointment_view

urlpatterns = [
    path('centers/', list_centers_view, name='list_centers'),
    path('centers/<int:center_id>/services/', list_services_at_center_view, name='list_services_at_center'),
    path('centers/<int:center_id>/services/<int:service_id>/slots/', view_available_slots_view, name='view_available_slots'), # POST here for booking
    # The path for 'book_appointment' is removed as it's handled by view_available_slots_view
]
