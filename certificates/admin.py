from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import CertificateType, CertificateRequirement, PatientCertificate

class CertificateRequirementInline(admin.TabularInline):
    model = CertificateRequirement
    extra = 1 # Number of empty forms to display

@admin.register(CertificateType)
class CertificateTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'issuance_service', 'validity_days')
    inlines = [CertificateRequirementInline]
    search_fields = ('name',) # Added search_fields as per script's new content for PatientCertificateAdmin

@admin.register(PatientCertificate)
class PatientCertificateAdmin(admin.ModelAdmin):
    list_display = ('patient', 'certificate_type', 'issue_date', 'expiry_date', 'certificate_identifier', 'generate_pdf_link')
    list_filter = ('certificate_type', 'issue_date', 'patient')
    search_fields = ('patient__username', 'certificate_identifier', 'certificate_type__name')
    raw_id_fields = ('patient', 'appointment')
    # Making issue_date and certificate_identifier readonly. Expiry_date is auto-calculated.
    readonly_fields = ('issue_date', 'expiry_date', 'certificate_identifier', 'qr_code_data')

    def generate_pdf_link(self, obj):
        if obj.pk:
            # Ensure qr_code_data is set before generating link, will be set by save_model
            if not obj.qr_code_data:
                 # This is a fallback, save_model should ideally set it.
                 # For robustness, one might call obj.save() here if qr_code_data is critical
                 # but admin actions shouldn't typically auto-save without explicit user action on the form.
                 # The link will work once qr_code_data is populated by saving the model instance.
                 return "Save certificate first to set QR data for PDF link."

            url = reverse('generate_certificate_pdf', args=[obj.pk])
            return format_html('<a href="{}" target="_blank">View/Generate PDF</a>', url)
        return 'Save certificate to generate PDF'
    generate_pdf_link.short_description = 'Certificate PDF'

    def save_model(self, request, obj, form, change):
        # qr_code_data is now URLField, so it should store a URL.
        # The verification URL is based on certificate_identifier which is a UUID.
        if not obj.qr_code_data and obj.certificate_identifier:
            # Construct the verification URL.
            # request.build_absolute_uri() is good for full URLs.
            # However, for QR codes, sometimes shorter, more manageable URLs are preferred if a URL shortener is used,
            # or if the domain is implicitly known by the scanning app or process.
            # For this context, a full URL is robust.
            verification_path = reverse('verify_certificate_qr', args=[obj.certificate_identifier])
            full_verification_url = request.build_absolute_uri(verification_path)

            # Remove default ports for cleaner QR code data if desired.
            # This might be too aggressive if site runs on non-standard port behind a reverse proxy
            # that expects the port in the Host header. For now, let's keep it simple.
            # full_verification_url = full_verification_url.replace(':8000', '').replace(':80', '')
            obj.qr_code_data = full_verification_url

        super().save_model(request, obj, form, change)

# Basic admin for CertificateRequirement if needed directly (though usually managed via inline)
# admin.site.register(CertificateRequirement)
