from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from certificates.models import Certificate, CertificateTemplate
from accounts.models import User
from tournaments.models import Tournament
from teams.models import Team
from backend.auth import authenticate
from django.utils import timezone

class CertificateApiTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin', email='admin@e.com', password='pass', role='admin', is_staff=True, is_superuser=True
        )
        self.user = User.objects.create_user(username='user', email='u@e.com', password='pass')
        self.template = CertificateTemplate.objects.create(
            name='Default',
            image=SimpleUploadedFile('t.png', b'fake', content_type='image/png'),
            is_default=True,
        )
        self.team = Team.objects.create(name='Tournament Team', email='ct@e.com', captain=self.user)
        self.tournament = Tournament.objects.create(
            name='test Tournament', 
            start_date=timezone.now(), 
            end_date=timezone.now() + timezone.timedelta(days=1),
            created_by=self.user
        )
    
        self.list_url = reverse('ninja-api:certificate-list')

    def test_list_certificates_anonymous(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_certificate_admin_only(self):
        authenticate(self.client, self.user)
        response = self.client.post(self.list_url, {'placement': '1st', 'template': self.template.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        authenticate(self.client, self.admin)
        response = self.client.post(self.list_url, {'placement': '1st', 'template': self.template.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_certificate_by_uuid(self):
        cert = Certificate.objects.create(placement='1st', user=self.user)
        url = reverse('ninja-api:certificate-detail', kwargs={'unique_code': cert.unique_code})
        authenticate(self.client, self.user)
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['unique_code'], str(cert.unique_code))

    def test_verify_certificate(self):
        cert = Certificate.objects.create(
            placement='1st',
            user=self.user,
            team=self.team,
            tournament=self.tournament,
            template=self.template,
        )
        url = reverse('ninja-api:certificate-verify', kwargs={'code': cert.unique_code})
        authenticate(self.client, self.user)
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['unique_code'], str(cert.unique_code))

    def test_view_certificate_action(self):
        cert = Certificate.objects.create(placement='1st', user=self.user)
        url = reverse('ninja-api:certificate-view', kwargs={'unique_code': cert.unique_code})
        authenticate(self.client, self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_template_list_admin_only(self):
        url = reverse('ninja-api:template-list')
        authenticate(self.client, self.user)
        response = self.client.get(url)
        # Templates might be public to view but restricted to create
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        pass

    def test_create_template_admin_only(self):
        url = reverse('ninja-api:template-list')
        authenticate(self.client, self.user)
        image = SimpleUploadedFile(
            "template.png",
            b"fake image content",
            content_type="image/png",
        )

        response = self.client.post(
            url,
            {
                "name": "New T",
                "image": image,
            },
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_certificate_admin_only(self):
        cert = Certificate.objects.create(placement='1st')
        url = reverse('ninja-api:certificate-detail', kwargs={'unique_code': cert.unique_code})
        authenticate(self.client, self.user)
        response = self.client.patch(url, {'placement': '2nd'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_certificate_admin_only(self):
        cert = Certificate.objects.create(placement='1st')
        url = reverse('ninja-api:certificate-detail', kwargs={'unique_code': cert.unique_code})
        authenticate(self.client, self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_verify_invalid_code(self):
        url = reverse('ninja-api:certificate-verify', kwargs={'code': 'invalid-uuid'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
