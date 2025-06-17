from django.conf import settings # Added import
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import AttentionCenter, Service, Doctor, Appointment # Removed Holiday, DoctorAvailability as they are used in slot_logic
from django.utils import timezone
from datetime import datetime, timedelta, time # Removed date as it's part of datetime, removed collections
from django.db import transaction
from .slot_logic import get_available_slots # Import the new slot logic
from django.http import HttpResponseBadRequest # For handling bad POST data

@login_required
def list_centers_view(request):
    centers = AttentionCenter.objects.all()
    return render(request, 'scheduling/list_centers.html', {'centers': centers})

@login_required
def list_services_at_center_view(request, center_id):
    center = get_object_or_404(AttentionCenter, pk=center_id)
    services = Service.objects.filter(center=center)
    return render(request, 'scheduling/list_services.html', {'center': center, 'services': services})

@login_required
def view_available_slots_view(request, center_id, service_id):
    center = get_object_or_404(AttentionCenter, pk=center_id)
    service = get_object_or_404(Service, pk=service_id, center=center)

    start_date = timezone.now().date()
    if service.service_type in ['LAB_EXAM', 'CERTIFICATE']:
        service_cutoff_time = service.specific_end_time or time(10,0)
        if timezone.now().time() < service_cutoff_time :
             start_date = timezone.now().date()
        else:
             start_date = timezone.now().date() + timedelta(days=1)
    else:
        start_date = timezone.now().date() + timedelta(days=1)

    end_date = start_date + timedelta(days=7)

    available_slots_by_date = get_available_slots(center_id, service_id, start_date, end_date)

    if request.method == 'POST':
        selected_slot_start_str = request.POST.get('selected_slot_start')
        # Construct the key for the doctor ID based on the selected slot start string
        doctor_id_form_key = f"doctor_for_slot_{selected_slot_start_str}"
        selected_doctor_id_str = request.POST.get(doctor_id_form_key)

        if not selected_slot_start_str:
            messages.error(request, 'Please select a time slot.')
            return redirect(request.path_info)

        try:
            # slot_start_dt = datetime.fromisoformat(selected_slot_start_str) # fromisoformat does not handle 'Z' if present from date:"c"
            # A more robust way to parse ISO format with potential 'Z' or timezone offset:
            if selected_slot_start_str.endswith('Z'):
                slot_start_dt = datetime.strptime(selected_slot_start_str, "%Y-%m-%dT%H:%M:%SZ")
            else: # Handle cases with +HH:MM or -HH:MM if necessary, or assume no offset if not Z
                 slot_start_dt = datetime.fromisoformat(selected_slot_start_str.replace('Z', ''))


            if settings.USE_TZ:
                slot_start_dt = timezone.make_aware(slot_start_dt, timezone.get_default_timezone())
            else: # If not using TZ, ensure it's naive
                slot_start_dt = timezone.make_naive(slot_start_dt, timezone.get_default_timezone()) if timezone.is_aware(slot_start_dt) else slot_start_dt


        except ValueError:
            messages.error(request, 'Invalid slot format.')
            return redirect(request.path_info)

        chosen_slot_info = None
        slot_date = slot_start_dt.date()
        if slot_date in available_slots_by_date:
            for slot_info in available_slots_by_date[slot_date]:
                # Make slot_info['start'] naive if settings.USE_TZ is false for comparison
                # Or ensure slot_start_dt is consistently aware/naive with slot_info['start']
                comp_slot_start = slot_info['start']
                if not settings.USE_TZ and timezone.is_aware(comp_slot_start):
                    comp_slot_start = timezone.make_naive(comp_slot_start, timezone.get_default_timezone())

                if comp_slot_start == slot_start_dt:
                    if service.requires_doctor_assignment:
                        # Check if doctor ID from form matches. selected_doctor_id_str could be "" or "None" as a string.
                        if selected_doctor_id_str and selected_doctor_id_str != "" and selected_doctor_id_str != "None" and slot_info['doctor'] and str(slot_info['doctor'].id) == selected_doctor_id_str:
                            chosen_slot_info = slot_info
                            break
                        # Case where service requires doctor, but slot has no doctor or ID from form is missing/None
                        elif not slot_info['doctor'] or not selected_doctor_id_str or selected_doctor_id_str == "" or selected_doctor_id_str == "None":
                            # If the slot expects a doctor, but no valid doctor_id was submitted for it, this slot is not a match.
                            if slot_info['doctor']: # This specific slot in the list has a doctor.
                                continue # Doctor ID mismatch or not provided from form, so skip.
                            else: # This slot in the list has no doctor, but service requires one. This case should ideally not occur if slots are generated correctly.
                                chosen_slot_info = slot_info # Or raise error/log warning
                                break
                        else: # Fallback or error case
                            continue
                    else: # Service does not require a doctor
                        chosen_slot_info = slot_info
                        break

        if not chosen_slot_info:
            messages.error(request, 'Selected slot is no longer available or invalid. Please try again.')
            return redirect(request.path_info)

        slot_end_dt = chosen_slot_info['end']
        doctor_instance = chosen_slot_info['doctor']

        try:
            with transaction.atomic():
                existing_appt_for_slot = Appointment.objects.filter(
                    service=service,
                    start_time=slot_start_dt,
                    status='SCHEDULED'
                )
                if doctor_instance:
                    existing_appt_for_slot = existing_appt_for_slot.filter(doctor=doctor_instance)
                else:
                    existing_appt_for_slot = existing_appt_for_slot.filter(doctor__isnull=True)

                if existing_appt_for_slot.exists():
                    messages.error(request, 'Sorry, this slot was booked while you were choosing. Please select another slot.')
                    return redirect(request.path_info)

                Appointment.objects.create(
                    patient=request.user,
                    service=service,
                    doctor=doctor_instance,
                    center=center, # This is service.center, but passed for clarity
                    start_time=slot_start_dt,
                    end_time=slot_end_dt,
                    status='SCHEDULED'
                )
                messages.success(request, f'Appointment booked successfully for {service.name} on {slot_start_dt.strftime("%A, %B %d, %Y at %I:%M %p")}.')
                return redirect(reverse('profile'))

        except Exception as e:
            messages.error(request, f'Could not book appointment: {e}')
            return redirect(request.path_info)

    return render(request, 'scheduling/view_available_slots.html', {
        'center': center,
        'service': service,
        'available_slots_by_date': available_slots_by_date,
    })
