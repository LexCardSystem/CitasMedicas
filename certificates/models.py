from django.db import models
from django.conf import settings # For Patient model
from scheduling.models import Service, Appointment # Assuming scheduling app exists
import uuid

class CertificateType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    validity_days = models.PositiveIntegerField(null=True, blank=True, help_text='Optional: Number of days the certificate is valid for.')
    # Link this certificate type to a specific service that needs to be booked for its issuance.
    # E.g., 'Medical Certificate for Driving' CertificateType links to a 'Driving Medical Exam' Service.
    issuance_service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True,
                                         help_text='The service that must be booked to obtain this certificate.')

    def __str__(self):
        return self.name

class CertificateRequirement(models.Model):
    certificate_type = models.ForeignKey(CertificateType, on_delete=models.CASCADE, related_name='requirements')
    requirement_description = models.CharField(max_length=500)
    is_mandatory = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.requirement_description} (for {self.certificate_type.name})'

class PatientCertificate(models.Model):
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='certificates')
    certificate_type = models.ForeignKey(CertificateType, on_delete=models.PROTECT) # Don't delete type if certs exist
    # The appointment during which this certificate was processed/issued
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name='issued_certificates')
    issue_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    # For 'codigo unico seguro'.
    certificate_identifier = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, help_text='Unique identifier for the certificate (UUID)')
    # Data to be encoded in QR. This will store the full verification URL.
    qr_code_data = models.URLField(max_length=500, blank=True, help_text='Full verification URL to be embedded in the QR code.')
    notes = models.TextField(blank=True, help_text='Internal notes by issuing staff or doctor.')
    # The actual generated certificate file (PDF) could be a FileField here, added in a later step if needed.
    # pdf_file = models.FileField(upload_to='certificates_pdf/', null=True, blank=True)


    def save(self, *args, **kwargs):
        if self.issue_date and self.certificate_type and self.certificate_type.validity_days and not self.expiry_date:
            from datetime import timedelta
            self.expiry_date = self.issue_date + timedelta(days=self.certificate_type.validity_days)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.certificate_type.name} for {self.patient.username} (Issued: {self.issue_date})'
