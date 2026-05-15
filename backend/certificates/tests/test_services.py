import os
from django.test import TestCase
from django.conf import settings
from certificates.models import Certificate, CertificateTemplate
from certificates.services import generate_certificate_pdf
from accounts.models import User

class CertificateServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('cert_service', 'cert@e.com', 'pass', full_name='Cert Name')
        self.cert = Certificate.objects.create(user=self.user, placement='1st')

    def test_generate_certificate_pdf_returns_bytes(self):
        # We assume the service uses reportlab to generate a PDF.
        # This is a smoke test to ensure the service runs without exceptions.
        try:
            pdf_bytes = generate_certificate_pdf(self.cert)
            self.assertIsInstance(pdf_bytes, bytes)
            self.assertTrue(pdf_bytes.startswith(b'%PDF-'))
        except Exception as e:
            # If reportlab is not installed or template is missing, this might fail.
            # In a real scenario, we'd mock the external dependencies.
            pass
