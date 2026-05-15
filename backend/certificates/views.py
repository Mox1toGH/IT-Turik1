from django.http import HttpResponse
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import Certificate, CertificateTemplate
from .serializers import CertificateSerializer, CertificateTemplateSerializer
from .services import generate_certificate_pdf

from backend.openapi import _400, _401, _403, _404


class CertificatePagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 100


class CertificateTemplatePagination(PageNumberPagination):
    page_size = 8
    page_size_query_param = 'page_size'
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        if request.query_params.get('nopage') == 'true':
            return None
        return super().paginate_queryset(queryset, request, view)


@extend_schema_view(
    list=extend_schema(
        operation_id='listCertificateTemplates',
        parameters=[
            OpenApiParameter('nopage', OpenApiTypes.STR, required=False, description='Pass "true" to disable pagination'),
        ],
        responses={
            200: CertificateTemplateSerializer(many=True),
            401: _401,
        },
    ),
    retrieve=extend_schema(
        operation_id='getCertificateTemplate',
        responses={
            200: CertificateTemplateSerializer,
            401: _401,
            404: _404,
        },
    ),
    create=extend_schema(
        operation_id='createCertificateTemplate',
        responses={
            201: CertificateTemplateSerializer,
            400: _400,
            401: _401,
            403: _403,
        },
    ),
    update=extend_schema(
        operation_id='replaceCertificateTemplate',
        responses={200: CertificateTemplateSerializer, 400: _400, 401: _401, 403: _403, 404: _404},
    ),
    partial_update=extend_schema(
        operation_id='updateCertificateTemplate',
        responses={
            200: CertificateTemplateSerializer,
            400: _400,
            401: _401,
            403: _403,
            404: _404,
        },
    ),
    destroy=extend_schema(
        operation_id='deleteCertificateTemplate',
        responses={
            204: OpenApiResponse(description='Template deleted successfully.'),
            401: _401,
            403: _403,
            404: _404,
        },
    ),
)
@method_decorator(csrf_exempt, name='dispatch')
class CertificateTemplateViewSet(viewsets.ModelViewSet):
    queryset = CertificateTemplate.objects.all().order_by('-created_at')
    serializer_class = CertificateTemplateSerializer
    parser_classes = (MultiPartParser, FormParser)
    pagination_class = CertificateTemplatePagination

    def get_permissions(self):
        return [IsAuthenticated()]

    def _ensure_admin(self):
        if not self.request.user.is_staff:
            raise PermissionDenied('Only admins can manage certificate templates.')

    def create(self, request, *args, **kwargs):
        self._ensure_admin()
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self._ensure_admin()
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        self._ensure_admin()
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self._ensure_admin()
        return super().destroy(request, *args, **kwargs)


@extend_schema_view(
    list=extend_schema(
        operation_id='listCertificates',
        parameters=[
            OpenApiParameter('search', OpenApiTypes.STR, required=False, description='Search by username, full name, certificate number or unique code (admin only)'),
        ],
        responses={
            200: CertificateSerializer(many=True),
            401: _401,
        },
    ),
    retrieve=extend_schema(
        operation_id='getCertificate',
        responses={
            200: CertificateSerializer,
            401: _401,
            404: _404,
        },
    ),
    create=extend_schema(
        operation_id='createCertificate',
        responses={
            201: CertificateSerializer,
            400: _400,
            401: _401,
            403: _403,
        },
    ),
    partial_update=extend_schema(
        operation_id='updateCertificate',
        responses={
            200: CertificateSerializer,
            400: _400,
            401: _401,
            403: _403,
            404: _404,
        },
    ),
    destroy=extend_schema(
        operation_id='deleteCertificate',
        responses={
            204: OpenApiResponse(description='Certificate deleted successfully.'),
            401: _401,
            403: _403,
            404: _404,
        },
    ),
)
@method_decorator(csrf_exempt, name='dispatch')
class CertificateViewSet(viewsets.ModelViewSet):
    queryset = Certificate.objects.all().select_related('template', 'user', 'team', 'tournament').order_by('-created_at')
    serializer_class = CertificateSerializer
    lookup_field = 'unique_code'
    pagination_class = CertificatePagination

    def get_permissions(self):
        if self.action in {'verify', 'view'}:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if not user.is_authenticated:
            if self.action == 'view':
                return queryset
            return queryset.none()

        if user.is_staff:
            search_query = self.request.query_params.get('search')
            if search_query:
                queryset = queryset.filter(
                    Q(user__username__icontains=search_query) |
                    Q(user__full_name__icontains=search_query) |
                    Q(certificate_number__icontains=search_query) |
                    Q(unique_code__icontains=search_query)
                )
            return queryset

        return queryset.filter(user_id=user.id)

    def _ensure_admin_for_write(self):
        if self.action in {'create', 'update', 'partial_update', 'destroy'} and not self.request.user.is_staff:
            raise PermissionDenied('Only admins can manage certificates.')

    def create(self, request, *args, **kwargs):
        self._ensure_admin_for_write()
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self._ensure_admin_for_write()
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        self._ensure_admin_for_write()
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self._ensure_admin_for_write()
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        operation_id='viewCertificatePdf',
        responses={
            200: OpenApiResponse(description='PDF file of the certificate.'),
            401: _401,
            500: OpenApiResponse(description='PDF generation failed.'),
        },
    )
    @method_decorator(xframe_options_exempt)
    @action(detail=True, methods=['get'])
    def view(self, request, unique_code=None):
        certificate = self.get_object()
        try:
            pdf_bytes = generate_certificate_pdf(certificate, request=request)
            response = HttpResponse(pdf_bytes, content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="cert_{certificate.unique_code}.pdf"'
            return response
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        operation_id='verifyCertificate',
        parameters=[
            OpenApiParameter('code', OpenApiTypes.STR, location=OpenApiParameter.PATH, description='Unique code or certificate number'),
        ],
        responses={
            200: CertificateSerializer,
            404: _404,
        },
    )
    @action(detail=False, methods=['get'], url_path='verify/(?P<code>[^/.]+)')
    def verify(self, request, code=None):
        certificate = Certificate.objects.filter(
            Q(unique_code=code) | Q(certificate_number=code)
        ).first()

        if not certificate:
            return Response({"is_valid": False, "message": "Certificate not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(certificate)
        return Response({
            "is_valid": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)