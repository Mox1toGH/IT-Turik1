from io import BytesIO
from pathlib import Path
import base64

from django.template.loader import render_to_string
from django.urls import reverse
from django.conf import settings
from weasyprint import HTML
import qrcode

from .models import CertificateTemplate


PAGE_WIDTH_PX = 1376
PAGE_HEIGHT_PX = 768


def _build_context(certificate, template_obj, verification_url=''):
    participant_name = certificate.full_name

    placement_text = certificate.placement or ''
    if placement_text and 'place' not in placement_text.lower() and placement_text.lower() != 'participant':
        placement_text = f'{placement_text} place'

    template_image_uri = ''
    if template_obj and template_obj.image:
        template_image_uri = Path(template_obj.image.path).resolve().as_uri()

    qr_code_data_uri = ''
    if verification_url:
        qr = qrcode.QRCode(box_size=4, border=1)
        qr.add_data(verification_url)
        qr.make(fit=True)
        qr_image = qr.make_image(fill_color='black', back_color='white')
        qr_buffer = BytesIO()
        qr_image.save(qr_buffer, format='PNG')
        qr_base64 = base64.b64encode(qr_buffer.getvalue()).decode('ascii')
        qr_code_data_uri = f'data:image/png;base64,{qr_base64}'

    return {
        'certificate': certificate,
        'participant_name': participant_name,
        'team_name': certificate.team_name,
        'tournament_name': certificate.tournament_name,
        'placement_text': placement_text,
        'template_image_uri': template_image_uri,
        'verification_url': verification_url,
        'qr_code_data_uri': qr_code_data_uri,
        'page_width_px': PAGE_WIDTH_PX,
        'page_height_px': PAGE_HEIGHT_PX,
    }


def _build_verification_url(certificate, request=None):
    frontend_base_url = getattr(settings, 'FRONTEND_URL', '').rstrip('/')
    if not frontend_base_url:
        frontend_base_url = getattr(settings, 'CORS_ALLOWED_ORIGINS', [''])[0].rstrip('/')
    if frontend_base_url:
        return f'{frontend_base_url}/certificates/verify/{certificate.unique_code}'

    if request:
        verify_path = reverse('certificate-verify', kwargs={'code': certificate.unique_code})
        return request.build_absolute_uri(verify_path)

    return ''


def generate_certificate_pdf(certificate, template_obj=None, request=None):
    """
    Generates a PDF from HTML template via WeasyPrint and returns raw PDF bytes.
    The PDF is not persisted and is rendered on demand.
    """
    if not template_obj:
        template_obj = certificate.template
    if not template_obj:
        template_obj = CertificateTemplate.objects.filter(is_default=True).first()

    verification_url = _build_verification_url(certificate, request=request)
    context = _build_context(certificate, template_obj, verification_url=verification_url)
    html_string = render_to_string('certificates/certificate.html', context)

    html = HTML(string=html_string, base_url=str(Path(__file__).resolve().parent.parent))
    pdf_bytes = html.write_pdf()

    buffer = BytesIO()
    buffer.write(pdf_bytes)
    return buffer.getvalue()
