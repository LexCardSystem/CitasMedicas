from django.shortcuts import render, redirect, get_object_or_404 # Added get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.utils import timezone # Added for appointment history

from .forms import PatientCreationForm
from .models import Patient
from scheduling.models import Appointment # For accessing appointments
from labresults.models import PatientLabResult # For accessing lab results


class RegisterView(generic.CreateView):
    form_class = PatientCreationForm
    success_url = reverse_lazy('login') # Redirect to login page after successful registration
    template_name = 'accounts/register.html'

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')

# We will use Django's built-in LoginView and LogoutView


@login_required
def appointment_history_view(request):
    upcoming_appointments = Appointment.objects.filter(
        patient=request.user,
        start_time__gte=timezone.now() # Use timezone.now()
    ).order_by('start_time').select_related('service', 'center', 'doctor', 'doctor__user')

    past_appointments = Appointment.objects.filter(
        patient=request.user,
        start_time__lt=timezone.now()
    ).order_by('-start_time').select_related('service', 'center', 'doctor', 'doctor__user')

    return render(request, 'accounts/appointment_history.html', {
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments,
    })

@login_required
def appointment_detail_view(request, appointment_id):
    appointment = get_object_or_404(
        Appointment.objects.select_related('service', 'center', 'doctor', 'doctor__user'),
        pk=appointment_id,
        patient=request.user
    )
    # Fetch related lab results for this appointment
    lab_results_for_appointment = PatientLabResult.objects.filter(
        appointment=appointment
    ).prefetch_related(
        'values',
        'values__numeric_range_item_tested',
        'values__list_value_selected',
        'test_definition'
    )

    return render(request, 'accounts/appointment_detail.html', {
        'appointment': appointment,
        'lab_results_for_appointment': lab_results_for_appointment,
    })
