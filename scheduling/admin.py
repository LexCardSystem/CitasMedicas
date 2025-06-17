from django.contrib import admin
from .models import AttentionCenter, Holiday, Service, Doctor, DoctorAvailability, Appointment

@admin.register(AttentionCenter) # Changed from admin.site.register(AttentionCenter)
class AttentionCenterAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'morning_start_time', 'morning_end_time', 'afternoon_start_time', 'afternoon_end_time')
    search_fields = ['name', 'address'] # Added search_fields

admin.site.register(Holiday) # Holiday can remain a basic registration for now

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialty_display', 'list_centers')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'specialty')
    raw_id_fields = ('user',)
    filter_horizontal = ('centers',)

    def specialty_display(self, obj):
        return obj.specialty if obj.specialty else 'N/A'
    specialty_display.short_description = 'Specialty'

    def list_centers(self, obj):
        return ", ".join([center.name for center in obj.centers.all()])
    list_centers.short_description = 'Works at Centers'


@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'center', 'get_day_of_week_display', 'start_time', 'end_time')
    list_filter = ('day_of_week', 'center', 'doctor')
    # search_fields for DoctorAvailabilityAdmin itself, used for filtering within its own list view.
    # The error was about search_fields in the *target* ModelAdmins (DoctorAdmin, AttentionCenterAdmin)
    # for the autocomplete_fields.
    search_fields = ('doctor__user__username', 'center__name')
    autocomplete_fields = ['doctor', 'center']


admin.site.register(Appointment)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'center', 'service_type', 'duration_minutes', 'requires_doctor_assignment', 'specific_start_time', 'specific_end_time')
    list_filter = ('center', 'service_type', 'requires_doctor_assignment')
    search_fields = ('name', 'description')
    autocomplete_fields = ['center'] # Added autocomplete for center in ServiceAdmin
    fieldsets = (
        (None, {
            'fields': ('name', 'center', 'service_type', 'description')
        }),
        ('Scheduling Parameters', {
            'fields': ('duration_minutes', 'requires_doctor_assignment', 'specific_start_time', 'specific_end_time')
        }),
    )
    actions = ['mark_as_consultation_template', 'mark_as_lab_template', 'mark_as_certificate_template']

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'specific_start_time' in form.base_fields:
            form.base_fields['specific_start_time'].help_text = 'Default: Operates during all center hours. For Lab Exams & Certificates: Set to early morning, e.g., 07:00.'
        if 'specific_end_time' in form.base_fields:
            form.base_fields['specific_end_time'].help_text = 'Default: Operates during all center hours. For Lab Exams & Certificates: Set to early morning end, e.g., 10:00.'
        if 'requires_doctor_assignment' in form.base_fields:
            form.base_fields['requires_doctor_assignment'].help_text = 'Check this for services like Consultations that need a specific doctor. Uncheck for general lab/certificate services.'

        if obj:
            if obj.service_type in ['LAB_EXAM', 'CERTIFICATE']:
                if 'specific_start_time' in form.base_fields:
                    form.base_fields['specific_start_time'].help_text = 'This service is a Lab Exam or Certificate. Recommended: early morning time (e.g., 07:00).'
                if 'specific_end_time' in form.base_fields:
                    form.base_fields['specific_end_time'].help_text = 'This service is a Lab Exam or Certificate. Recommended: early morning end time (e.g., 10:00).'
                if 'requires_doctor_assignment' in form.base_fields and obj.requires_doctor_assignment:
                     form.base_fields['requires_doctor_assignment'].help_text = 'Warning: Lab/Certificate services usually do not require a doctor. Consider unchecking.'
            elif obj.service_type == 'CONSULTATION':
                 if 'requires_doctor_assignment' in form.base_fields and not obj.requires_doctor_assignment:
                     form.base_fields['requires_doctor_assignment'].help_text = 'Warning: Consultation services usually require a doctor. Consider checking this.'
        return form

    def mark_as_consultation_template(self, request, queryset):
        queryset.update(requires_doctor_assignment=True, specific_start_time=None, specific_end_time=None)
        self.message_user(request, 'Selected services updated for Consultation template (requires doctor, no specific time override).')
    mark_as_consultation_template.short_description = 'Apply Consultation Template'

    def mark_as_lab_template(self, request, queryset):
        from datetime import time
        queryset.update(requires_doctor_assignment=False, specific_start_time=time(7,0), specific_end_time=time(10,0))
        self.message_user(request, 'Selected services updated for Lab Exam template (7-10 AM, no doctor).')
    mark_as_lab_template.short_description = 'Apply Lab Exam Template (7-10 AM)'

    def mark_as_certificate_template(self, request, queryset):
        from datetime import time
        queryset.update(requires_doctor_assignment=False, specific_start_time=time(7,0), specific_end_time=time(10,0)) # Similar to lab
        self.message_user(request, 'Selected services updated for Certificate template (7-10 AM, no doctor).')
    mark_as_certificate_template.short_description = 'Apply Certificate Template (7-10 AM)'
