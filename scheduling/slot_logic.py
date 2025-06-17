from django.utils import timezone
from datetime import datetime, timedelta, time, date
from .models import Appointment, Holiday, DoctorAvailability, Service, AttentionCenter
import collections

def get_available_slots(center_id, service_id, start_date, end_date):
    center = AttentionCenter.objects.get(pk=center_id)
    service = Service.objects.get(pk=service_id)

    holidays = set(Holiday.objects.filter(date__range=(start_date, end_date)).values_list('date', flat=True))
    existing_appointments = Appointment.objects.filter(
        service=service, # Could also filter by center
        start_time__date__range=(start_date, end_date),
        status='SCHEDULED'
    )

    # Group existing appointments by date and doctor for quick lookup
    booked_slots_by_date_doc = collections.defaultdict(list)
    for appt in existing_appointments:
        doc_id = appt.doctor.id if appt.doctor else None
        booked_slots_by_date_doc[(appt.start_time.date(), doc_id)].append((appt.start_time, appt.end_time))

    available_slots_by_date = collections.defaultdict(list)
    slot_duration = timedelta(minutes=service.duration_minutes)

    current_date = start_date
    while current_date <= end_date:
        # Skip Sundays (day_of_week == 6) and Saturdays (day_of_week == 5) as per Mon-Fri requirement
        # Python's weekday(): Monday is 0 and Sunday is 6
        if current_date.weekday() >= 5 or current_date in holidays:
            current_date += timedelta(days=1)
            continue

        # Determine the service's operating window for the day
        # Start with center's general hours, then narrow by service specific times
        daily_windows = []
        if center.morning_start_time and center.morning_end_time:
            daily_windows.append((center.morning_start_time, center.morning_end_time))
        if center.afternoon_start_time and center.afternoon_end_time:
            daily_windows.append((center.afternoon_start_time, center.afternoon_end_time))

        # Narrow by service-specific times if they exist
        effective_service_start_time = service.specific_start_time or min(w[0] for w in daily_windows) if daily_windows else None
        effective_service_end_time = service.specific_end_time or max(w[1] for w in daily_windows) if daily_windows else None

        if not effective_service_start_time or not effective_service_end_time:
            current_date += timedelta(days=1)
            continue # No valid operating window for the service/center

        # For services NOT requiring a doctor
        if not service.requires_doctor_assignment:
            for window_start, window_end in daily_windows:
                current_slot_start_dt = datetime.combine(current_date, max(window_start, effective_service_start_time))
                day_end_dt = datetime.combine(current_date, min(window_end, effective_service_end_time))

                while current_slot_start_dt + slot_duration <= day_end_dt:
                    current_slot_end_dt = current_slot_start_dt + slot_duration
                    # Check for overlaps with existing appointments (for this service, no doctor)
                    is_booked = False
                    for booked_start, booked_end in booked_slots_by_date_doc.get((current_date, None), []):
                        if max(current_slot_start_dt, booked_start) < min(current_slot_end_dt, booked_end):
                            is_booked = True
                            break
                    if not is_booked:
                        available_slots_by_date[current_date].append({
                            'start': current_slot_start_dt,
                            'end': current_slot_end_dt,
                            'doctor': None
                        })
                    current_slot_start_dt += slot_duration

        # For services REQUIRING a doctor
        else:
            # Find doctors associated with this service's center and available on this day_of_week
            center_doctors = Doctor.objects.filter(centers=center)
            for doctor in center_doctors:
                doctor_availabilities = DoctorAvailability.objects.filter(
                    doctor=doctor,
                    center=center,
                    day_of_week=current_date.weekday()
                )
                for davail in doctor_availabilities:
                    # Effective start for this doctor on this day for this service
                    # Max of doctor's availability, center's window, service's specific window
                    eff_davail_start_time = max(davail.start_time, effective_service_start_time)
                    # Min of doctor's availability, center's window, service's specific window
                    eff_davail_end_time = min(davail.end_time, effective_service_end_time)

                    current_slot_start_dt = datetime.combine(current_date, eff_davail_start_time)
                    day_end_dt = datetime.combine(current_date, eff_davail_end_time)

                    while current_slot_start_dt + slot_duration <= day_end_dt:
                        current_slot_end_dt = current_slot_start_dt + slot_duration
                        # Check for overlaps with this doctor's existing appointments
                        is_booked = False
                        for booked_start, booked_end in booked_slots_by_date_doc.get((current_date, doctor.id), []):
                             if max(current_slot_start_dt, booked_start) < min(current_slot_end_dt, booked_end):
                                is_booked = True
                                break
                        if not is_booked:
                            available_slots_by_date[current_date].append({
                                'start': current_slot_start_dt,
                                'end': current_slot_end_dt,
                                'doctor': doctor # Store the doctor object
                            })
                        current_slot_start_dt += slot_duration
            # Sort slots by time after collecting from all doctors for the day
            if current_date in available_slots_by_date:
                 available_slots_by_date[current_date].sort(key=lambda x: (x['start'], x['doctor'].id if x['doctor'] else 0))


        current_date += timedelta(days=1)
    return available_slots_by_date
