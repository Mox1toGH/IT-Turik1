from django.test import TestCase
from certificates.models import Certificate, CertificateTemplate
from accounts.models import User
from teams.models import Team
from tournaments.models import Tournament
from django.utils import timezone
import uuid

class CertificateModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cert-u', email='cert@e.com', full_name='Cert User')
        self.team = Team.objects.create(name='Cert Team', email='ct@e.com', captain=self.user)
        self.tournament = Tournament.objects.create(
            name='Cert Tourney', 
            start_date=timezone.now(), 
            end_date=timezone.now() + timezone.timedelta(days=1),
            created_by=self.user
        )
        self.template = CertificateTemplate.objects.create(name='Standard')

    def test_certificate_template_str(self):
        self.assertEqual(str(self.template), 'Standard')

    def test_certificate_template_default_behavior(self):
        t1 = CertificateTemplate.objects.create(name='T1', is_default=True)
        self.assertTrue(t1.is_default)
        t2 = CertificateTemplate.objects.create(name='T2', is_default=True)
        t1.refresh_from_db()
        self.assertFalse(t1.is_default)
        self.assertTrue(t2.is_default)

    def test_certificate_creation_fills_snapshots(self):
        cert = Certificate.objects.create(
            user=self.user,
            team=self.team,
            tournament=self.tournament,
            placement='1st Place'
        )
        self.assertEqual(cert.participant_name_snapshot, 'Cert User')
        self.assertEqual(cert.team_name_snapshot, 'Cert Team')
        self.assertEqual(cert.tournament_name_snapshot, 'Cert Tourney')
        self.assertTrue(cert.certificate_number.startswith('CERT-'))

    def test_certificate_snapshot_immutability(self):
        cert = Certificate.objects.create(
            user=self.user,
            team=self.team,
            tournament=self.tournament,
            placement='1st'
        )
        # Change user full name
        self.user.full_name = 'New Name'
        self.user.save()
        # Snapshot should remain the same
        cert.save() 
        self.assertEqual(cert.participant_name_snapshot, 'Cert User')
        self.assertEqual(cert.full_name, 'Cert User')

    def test_certificate_str(self):
        cert = Certificate.objects.create(user=self.user, tournament=self.tournament, placement='1st')
        self.assertEqual(str(cert), 'Cert User - Cert Tourney')

    def test_certificate_unique_code(self):
        cert = Certificate.objects.create(user=self.user, placement='1st')
        self.assertIsInstance(uuid.UUID(cert.unique_code), uuid.UUID)

    def test_certificate_cascade_null(self):
        cert = Certificate.objects.create(user=self.user, team=self.team, placement='1st')
        self.user.delete()
        cert.refresh_from_db()
        self.assertIsNone(cert.user)
        self.assertEqual(cert.participant_name_snapshot, 'Cert User')

    def test_certificate_template_cascade_null(self):
        cert = Certificate.objects.create(template=self.template, placement='1st')
        self.template.delete()
        cert.refresh_from_db()
        self.assertIsNone(cert.template)

    def test_certificate_number_generation(self):
        cert = Certificate.objects.create(placement='1st')
        self.assertIn('CERT-', cert.certificate_number)

    def test_certificate_resolve_participant_name_with_username(self):
        user2 = User.objects.create_user(username='only-user', email='o@e.com')
        cert = Certificate.objects.create(user=user2, placement='1st')
        self.assertEqual(cert.participant_name_snapshot, 'only-user')
