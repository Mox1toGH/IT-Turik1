from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CertificateViewSet, CertificateTemplateViewSet

urlpatterns = [
    # Templates CRUD
    path('templates/', CertificateTemplateViewSet.as_view({'get': 'list', 'post': 'create'}), name='template-list'),
    path('templates/<int:pk>/', CertificateTemplateViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='template-detail'),
    
    # Certificates CRUD
    path('', CertificateViewSet.as_view({'get': 'list', 'post': 'create'}), name='certificate-list'),
    path('<uuid:unique_code>/', CertificateViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='certificate-detail'),
    
    # Custom Actions
    path('<uuid:unique_code>/view/', CertificateViewSet.as_view({'get': 'view'}), name='certificate-view'),
    path('verify/<str:code>/', CertificateViewSet.as_view({'get': 'verify'}), name='certificate-verify'),
]
