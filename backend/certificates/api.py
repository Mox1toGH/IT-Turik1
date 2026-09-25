from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from ninja import Router, File
from ninja.files import UploadedFile
from ninja.errors import HttpError
from ninja.pagination import paginate, PageNumberPagination

from backend.auth import JWTAuth, OptionalJWTAuth  # твій auth-backend для Ninja
from .models import Certificate, CertificateTemplate

from backend.schemas import ErrorResponse
from .schemas import CertificateResponse, CertificateRequest, CertificateTemplateResponse, CertificateVerifyResponse
from .services import generate_certificate_pdf

router = Router(tags=['certificates'])

def _require_staff(request):
    if not request.auth.is_staff:
        raise HttpError(403, 'Only admins can perform this action.')


# =============================================================================
# CertificateTemplateViewSet — equivalent
#
#   GET    /certificate-templates/          -> list_templates
#   GET    /certificate-templates/{id}/     -> get_template
#   POST   /certificate-templates/          -> create_template     (admin only)
#   PATCH  /certificate-templates/{id}/     -> update_template     (admin only)
#   DELETE /certificate-templates/{id}/     -> delete_template     (admin only)
# =============================================================================

@router.get('/certificate-templates', operation_id='listCertificateTemplates', response={200: list[CertificateTemplateResponse], 401: ErrorResponse}, auth=JWTAuth())
@paginate(PageNumberPagination, page_size=8)
def list_templates(request, nopage: str = ''):
    return CertificateTemplate.objects.all().order_by('-created_at')

@router.get('/certificate-templates/{template_id}', operation_id='getCertificateTemplate', response={200: CertificateTemplateResponse, 401: ErrorResponse, 404: ErrorResponse}, auth=JWTAuth())
def get_template(request, template_id: int):
    template = get_object_or_404(CertificateTemplate, pk=template_id)
    
    return CertificateTemplateResponse.model_validate(
        template,
        from_attributes=True,
        context={"request": request},
    )


@router.post('/certificate-templates', operation_id='createCertificateTemplate', response={201: CertificateTemplateResponse, 401: ErrorResponse, 400: ErrorResponse, 403: ErrorResponse}, auth=JWTAuth())
def create_template(request, name: str, is_default: bool = False, image: UploadedFile = File(...)):
    _require_staff(request)

    if not name.strip():
        raise HttpError(400, 'name is required.')

    template = CertificateTemplate.objects.create(name=name, is_default=is_default, image=image)
    return 201, CertificateTemplateResponse.model_validate(
        template,
        from_attributes=True,
        context={"request": request},
    )


@router.put('/certificate-templates/{template_id}', operation_id='replaceCertificateTemplate', response={200: CertificateTemplateResponse, 401: ErrorResponse, 400: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse}, auth=JWTAuth())
@router.patch('/certificate-templates/{template_id}', operation_id='updateCertificateTemplate', response={200: CertificateTemplateResponse, 401: ErrorResponse, 400: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse}, auth=JWTAuth())
def update_template(
    request, template_id: int,
    name: str = None, is_default: bool = None, image: UploadedFile = File(None),
):
    _require_staff(request)
    template = get_object_or_404(CertificateTemplate, pk=template_id)

    if name is not None:
        template.name = name
    if is_default is not None:
        template.is_default = is_default
    if image is not None:
        template.image = image
    template.save()

    return CertificateTemplateResponse.model_validate(
        template,
        from_attributes=True,
        context={"request": request},
    )


@router.delete('/certificate-templates/{template_id}', operation_id='deleteCertificateTemplate', response={204: None, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse}, auth=JWTAuth())
def delete_template(request, template_id: int):
    _require_staff(request)
    template = get_object_or_404(CertificateTemplate, pk=template_id)
    template.delete()
    return 204, None


# =============================================================================
# CertificateViewSet — equivalent
#
#   GET    /                        -> list_certificates
#   GET    /{unique_code}/           -> get_certificate
#   POST   /                         -> create_certificate  (admin only)
#   PATCH  /{unique_code}/           -> update_certificate  (admin only)
#   DELETE /{unique_code}/           -> delete_certificate  (admin only)
#   GET    /{unique_code}/view/      -> view_certificate_pdf (public)
#   GET    /verify/{code}/           -> verify_certificate   (public)
# =============================================================================

def _visible_certificates(request):
    """
    Replaces CertificateViewSet.get_queryset(). Called explicitly at the top
    of every action that needs it — no hidden override, no method resolution order.
    """
    queryset = Certificate.objects.select_related('template', 'user', 'team', 'tournament').order_by('-created_at')
    user = request.auth

    if user is None or not user.is_authenticated:
        return queryset.none()

    if user.is_staff:
        search = request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(user__username__icontains=search)
                | Q(user__full_name__icontains=search)
                | Q(certificate_number__icontains=search)
                | Q(unique_code__icontains=search)
            )
        return queryset

    return queryset.filter(user_id=user.id)


@router.get('', operation_id='listCertificates', response={200: list[CertificateResponse], 401: ErrorResponse}, auth=JWTAuth())
@paginate(PageNumberPagination, page_size=6)
def list_certificates(request, search: str = ''):
    return _visible_certificates(request)


@router.get('/{unique_code}', operation_id='getCertificate', response={200: CertificateResponse, 401: ErrorResponse, 404: ErrorResponse}, auth=JWTAuth())
def get_certificate(request, unique_code: str):
    certificate = get_object_or_404(_visible_certificates(request), unique_code=unique_code)
    
    return CertificateResponse.model_validate(
        certificate,
        from_attributes=True,
        context={'request': request},
    )


@router.post('', operation_id='createCertificate', response={201: CertificateResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse}, auth=JWTAuth())
def create_certificate(request, payload: CertificateRequest):
    _require_staff(request)

    certificate = Certificate.objects.create(
        user_id=payload.user,
        template_id=payload.template,
        team_id=payload.team,
        tournament_id=payload.tournament,
        placement=payload.placement,
        certificate_number=payload.certificate_number,
    )
    return 201, CertificateResponse.model_validate(
        certificate,
        from_attributes=True,
        context={'request': request},
    )


@router.patch('/{unique_code}', operation_id='updateCertificate', response={200: CertificateResponse, 401: ErrorResponse, 400: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse}, auth=JWTAuth())
def update_certificate(request, unique_code: str, payload: CertificateRequest):
    _require_staff(request)
    certificate = get_object_or_404(Certificate, unique_code=unique_code)

    certificate.user_id = payload.user
    certificate.template_id = payload.template
    certificate.team_id = payload.team
    certificate.tournament_id = payload.tournament
    certificate.placement = payload.placement
    certificate.certificate_number = payload.certificate_number
    certificate.save()

    return CertificateResponse.model_validate(
        certificate,
        from_attributes=True,
        context={'request': request},
    )


@router.delete('/{unique_code}', operation_id='deleteCertificate', response={204: None, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse}, auth=JWTAuth())
def delete_certificate(request, unique_code: str):
    _require_staff(request)
    
    certificate = get_object_or_404(Certificate, unique_code=unique_code)
    certificate.delete()
    
    return 204, None


@router.get(
    '/{unique_code}/view',
    operation_id='viewCertificatePdf',
    response={200: None, 404: ErrorResponse, 500: ErrorResponse},
    auth=OptionalJWTAuth(),  # public: no auth required, matches AllowAny for this action
)
def view_certificate_pdf(request, unique_code: str):
    certificate = get_object_or_404(Certificate, unique_code=unique_code)

    try:
        pdf_bytes = generate_certificate_pdf(certificate, request=request)
    except Exception as e:
        raise HttpError(500, f'PDF generation failed: {e}')

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="cert_{certificate.unique_code}.pdf"'
    response['X-Frame-Options'] = 'ALLOWALL'  # equivalent of xframe_options_exempt
    
    return response


@router.get('/verify/{code}', operation_id='verifyCertificate', response={200: CertificateVerifyResponse}, auth=None)
def verify_certificate(request, code: str):
    certificate = Certificate.objects.filter(Q(unique_code=code) | Q(certificate_number=code)).first()

    if certificate is None:
        return {'is_valid': False, 'message': 'Certificate not found.'}

    return CertificateVerifyResponse(
        is_valid=True,
        data=CertificateResponse.model_validate(
            certificate,
            from_attributes=True,
            context={'request': request},
        ),
    )
