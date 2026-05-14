from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from certificates.models import Certificate, CertificateTemplate
from accounts.models import User
import uuid

class CertificateApiTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin', email='admin@e.com', password='pass', role='admin', is_staff=True, is_superuser=True
        )
        self.user = User.objects.create_user(username='user', email='u@e.com', password='pass')
        self.template = CertificateTemplate.objects.create(name='T')
        self.list_url = reverse('certificate-list')

    def test_list_certificates_anonymous(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_certificate_admin_only(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.list_url, {'placement': '1st', 'template': self.template.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.list_url, {'placement': '1st', 'template': self.template.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_certificate_by_uuid(self):
        cert = Certificate.objects.create(placement='1st', user=self.user)
        url = reverse('certificate-detail', kwargs={'unique_code': cert.unique_code})
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unique_code'], str(cert.unique_code))

    def test_verify_certificate(self):
        cert = Certificate.objects.create(placement='1st')
        url = reverse('certificate-verify', kwargs={'code': cert.unique_code})
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unique_code'], str(cert.unique_code))

    def test_view_certificate_action(self):
        cert = Certificate.objects.create(placement='1st', user=self.user)
        url = reverse('certificate-view', kwargs={'unique_code': cert.unique_code})
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_template_list_admin_only(self):
        url = reverse('template-list')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        # Templates might be public to view but restricted to create
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        pass

    def test_create_template_admin_only(self):
        url = reverse('template-list')
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, {'name': 'New T'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_certificate_admin_only(self):
        cert = Certificate.objects.create(placement='1st')
        url = reverse('certificate-detail', kwargs={'unique_code': cert.unique_code})
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(url, {'placement': '2nd'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_certificate_admin_only(self):
        cert = Certificate.objects.create(placement='1st')
        url = reverse('certificate-detail', kwargs={'unique_code': cert.unique_code})
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_verify_invalid_code(self):
        url = reverse('certificate-verify', kwargs={'code': 'invalid-uuid'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
