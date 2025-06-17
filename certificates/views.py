from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.template.loader import render_to_string
from django.conf import settings # Though not explicitly used, good for future reference
from .models import PatientCertificate
import qrcode
import base64
from io import BytesIO

# WeasyPrint import might fail if system dependencies are missing
try:
    from weasyprint import HTML, CSS
    WEASYPRINT_ERROR = None
except OSError as e: # OSError is often raised for missing shared libraries
    HTML = None
    CSS = None # CSS object might not be needed if all CSS is in <style> tags or linked in HTML
    WEASYPRINT_ERROR = e
    print(f'WEASYPRINT LOAD ERROR: {e}') # Log to console
except ImportError as e: # Could also be an ImportError if WeasyPrint is not installed at all
    HTML = None
    CSS = None
    WEASYPRINT_ERROR = f"ImportError: {e}"
    print(f'WEASYPRINT IMPORT ERROR: {e}')


def generate_certificate_pdf_view(request, certificate_id):
    if HTML is None:
        error_message = f'Error: WeasyPrint is not properly installed or configured. System library missing or Python package not found. ({WEASYPRINT_ERROR})'
        # It might be good to have a simple HTML error page for this too.
        return HttpResponse(error_message, status=500, content_type="text/plain")

    certificate = get_object_or_404(PatientCertificate.objects.select_related('patient', 'certificate_type', 'appointment'), pk=certificate_id)

    # Generate QR code
    qr_img_base64 = None
    # qr_code_url_display should be the full verification URL stored in qr_code_data
    qr_code_url_display = certificate.qr_code_data

    if certificate.qr_code_data:
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(certificate.qr_code_data) # Use the URL from the model
        qr.make(fit=True)
        img = qr.make_image(fill_color='black', back_color='white')

        buffered = BytesIO()
        img.save(buffered, format='PNG')
        qr_img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

    context = {
        'certificate': certificate,
        'qr_code_img_base64': qr_img_base64,
        'qr_code_url_display': qr_code_url_display,
    }
    html_string = render_to_string('certificates/certificate_template.html', context)

    # base_url helps WeasyPrint find related files like CSS if not inlined.
    # request.build_absolute_uri('/') provides scheme, host, port.
    html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
    pdf_file = html.write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    # f'attachment; filename=...' to download, f'inline; filename=...' to display in browser
    response['Content-Disposition'] = f'inline; filename="certificate_{certificate.certificate_identifier}.pdf"'
    return response

def verify_certificate_qr_view(request, certificate_identifier):
    # certificate_identifier is now a UUID field.
    try:
        certificate = PatientCertificate.objects.select_related('patient', 'certificate_type').get(certificate_identifier=certificate_identifier)
    except PatientCertificate.DoesNotExist:
        raise Http404('Certificate not found or invalid identifier.')
    except ValueError: # If certificate_identifier from URL is not a valid UUID
        raise Http404('Invalid certificate identifier format.')

    return render(request, 'certificates/verify_certificate.html', {'certificate': certificate})
