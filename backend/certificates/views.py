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

from .models import Certificate, CertificateTemplate
from .serializers import CertificateSerializer, CertificateTemplateSerializer
from .services import generate_certificate_pdf


@method_decorator(csrf_exempt, name='dispatch')
class CertificateTemplateViewSet(viewsets.ModelViewSet):
    queryset = CertificateTemplate.objects.all().order_by('-created_at')
    serializer_class = CertificateTemplateSerializer
    parser_classes = (MultiPartParser, FormParser)


@method_decorator(csrf_exempt, name='dispatch')
class CertificateViewSet(viewsets.ModelViewSet):
    queryset = Certificate.objects.all().select_related('template', 'user', 'team', 'tournament').order_by('-created_at')
    serializer_class = CertificateSerializer
    lookup_field = 'unique_code'

    def get_permissions(self):
        if self.action == 'verify':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if not user.is_authenticated:
            return queryset.none()

        if user.is_staff:
            return queryset

        return queryset.filter(user_id=user.id)

    @method_decorator(xframe_options_exempt)
    @action(detail=True, methods=['get'])
    def view(self, request, unique_code=None):
        """
        Custom action to render the dynamic PDF
        """
        certificate = self.get_object()
        try:
            pdf_bytes = generate_certificate_pdf(certificate)
            response = HttpResponse(pdf_bytes, content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="cert_{certificate.unique_code}.pdf"'
            return response
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='verify/(?P<code>[^/.]+)')
    def verify(self, request, code=None):
        """
        Custom action to verify a certificate by code or number
        """
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
