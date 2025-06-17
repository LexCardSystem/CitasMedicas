from django.db import models
from django.conf import settings # To link to AUTH_USER_MODEL (Patient)
from django.utils import timezone
import uuid # For unique appointment codes

class AttentionCenter(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    # Default operating hours, assuming Mon-Fri. Specific exceptions or variations might need more complex setup.
    # For simplicity, let's assume these are the general hours.
    # More granular control (e.g. per day) can be added if needed.
    morning_start_time = models.TimeField(help_text='Morning session start time, e.g., 08:00')
    morning_end_time = models.TimeField(help_text='Morning session end time, e.g., 12:00')
    afternoon_start_time = models.TimeField(help_text='Afternoon session start time, e.g., 14:00')
    afternoon_end_time = models.TimeField(help_text='Afternoon session end time, e.g., 18:00')

    def __str__(self):
        return self.name

class Holiday(models.Model):
    date = models.DateField(unique=True)
    description = models.CharField(max_length=255, help_text='e.g., New Year\'s Day')

    def __str__(self):
        return f'{self.date} ({self.description})'

class Service(models.Model):
    SERVICE_TYPES = [
        ('CONSULTATION', 'Consultation'),
        ('VACCINATION', 'Vaccination'),
        ('LAB_EXAM', 'Lab Exam'),
        ('CERTIFICATE', 'Certificate'),
    ]
    name = models.CharField(max_length=255)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)
    description = models.TextField(blank=True)
    center = models.ForeignKey(AttentionCenter, on_delete=models.CASCADE, related_name='services')
    # Duration for the service slot in minutes
    duration_minutes = models.PositiveIntegerField(default=30, help_text='Default duration in minutes for an appointment of this service')
    # Specific time window for this service if it differs from general center hours
    # e.g., Lab exams only in the early morning
    specific_start_time = models.TimeField(null=True, blank=True, help_text='Optional: Specific start time for this service, e.g., 07:00 for lab exams')
    specific_end_time = models.TimeField(null=True, blank=True, help_text='Optional: Specific end time for this service, e.g., 10:00 for lab exams')
    # This indicates if a doctor must be assigned to an appointment of this service.
    requires_doctor_assignment = models.BooleanField(default=False, help_text='Is a doctor required for this service type? (e.g., Consultations)')


    def __str__(self):
        return f'{self.name} at {self.center.name}'

class Doctor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'is_staff': True}, help_text='Link to a user account marked as staff/doctor') # Assuming doctors are staff users
    specialty = models.CharField(max_length=100, blank=True)
    centers = models.ManyToManyField(AttentionCenter, related_name='doctors', help_text='Centers where this doctor works')
    # Individual availability is complex and will be handled by DoctorAvailability records

    def __str__(self):
        return f'Dr. {self.user.get_full_name() or self.user.username} ({self.specialty})'

class DoctorAvailability(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'),
        (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')
    ]
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='availabilities')
    center = models.ForeignKey(AttentionCenter, on_delete=models.CASCADE, related_name='doctor_availabilities')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK, help_text='Day of the week this specific availability applies to. E.g., Monday for 9-5.')
    start_time = models.TimeField(help_text='Start time for this availability block on the selected day and center.')
    end_time = models.TimeField(help_text='End time for this availability block on the selected day and center.')

    class Meta:
        unique_together = ('doctor', 'center', 'day_of_week', 'start_time') # Ensure no overlapping general slots per doctor/center/day
        verbose_name_plural = 'Doctor Availabilities'

    def __str__(self):
        return f'{self.doctor} at {self.center} on {self.get_day_of_week_display()}: {self.start_time}-{self.end_time}'


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('NO_SHOW', 'No Show'),
    ]
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appointments')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, null=True, blank=True, on_delete=models.SET_NULL, related_name='appointments', help_text='Required if service needs doctor assignment')
    center = models.ForeignKey(AttentionCenter, on_delete=models.CASCADE, related_name='appointments_at_center') # Denormalized for easier queries
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    # For now, a UUID for appointment_code. Security aspects can be enhanced later.
    appointment_code = models.CharField(max_length=36, unique=True, default=uuid.uuid4)
    notes = models.TextField(blank=True, help_text='Optional notes for the appointment')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Appointment for {self.patient.username} - {self.service.name} on {self.start_time.strftime("%Y-%m-%d %H:%M")}'

    def clean(self):
        from django.core.exceptions import ValidationError
        # Ensure center is consistent with service
        if self.service and self.center != self.service.center:
            raise ValidationError('Appointment center must match the service center.')
        # Ensure doctor is provided if service requires it
        if self.service and self.service.requires_doctor_assignment and not self.doctor:
            raise ValidationError(f'Doctor is required for service: {self.service.name}')
        # Ensure selected doctor (if any) works at the service's center
        if self.doctor and self.service and self.service.center not in self.doctor.centers.all():
            raise ValidationError(f'Dr. {self.doctor} does not work at {self.service.center}.')
        # Ensure appointment times are valid
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError('Appointment start time must be before end time.')
        # Add more complex validation for slot availability, overlaps, within center/service/doctor hours here or in form/view logic

    def save(self, *args, **kwargs):
        # Automatically set center from service if not set (though it's good practice to set it explicitly)
        if self.service and not self.center_id: # Use _id to avoid fetching the object
            self.center = self.service.center

        # Calculate end_time based on service duration if not explicitly provided
        if self.start_time and self.service and not self.end_time:
            from datetime import timedelta
            self.end_time = self.start_time + timedelta(minutes=self.service.duration_minutes)

        super().save(*args, **kwargs)
