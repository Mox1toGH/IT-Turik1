from django.test import TestCase
from accounts.models import User, RoleActivationCode

class AccountModelTests(TestCase):
    def test_user_str(self):
        user = User.objects.create_user(username='testuser', email='test@example.com')
        self.assertEqual(str(user), 'testuser')

    def test_role_activation_code_str(self):
        code = RoleActivationCode.objects.create(code='CODE123', role='jury')
        self.assertEqual(str(code), 'jury:CODE123:False')

    def test_user_is_admin_property(self):
        user = User.objects.create_user(username='admin', email='a@e.com', role='admin')
        self.assertTrue(user.role == 'admin')

    def test_user_default_role(self):
        user = User.objects.create_user(username='default', email='d@e.com')
        self.assertEqual(user.role, 'team')

    def test_user_full_name_blank_by_default(self):
        user = User.objects.create_user(username='name', email='n@e.com')
        self.assertEqual(user.full_name, '')

    def test_role_activation_code_default_unused(self):
        code = RoleActivationCode.objects.create(code='UNUSED', role='team')
        self.assertFalse(code.is_used)

    def test_user_needs_onboarding_default_false(self):
        user = User.objects.create_user(username='onboard', email='o@e.com')
        self.assertFalse(user.needs_onboarding)

    def test_user_active_by_default(self):
        user = User.objects.create_user(username='active', email='act@e.com')
        self.assertTrue(user.is_active)

    def test_user_email_unique(self):
        User.objects.create_user(username='u1', email='same@e.com')
        with self.assertRaises(Exception):
            User.objects.create_user(username='u2', email='same@e.com')

    def test_user_username_unique(self):
        User.objects.create_user(username='same', email='u1@e.com')
        with self.assertRaises(Exception):
            User.objects.create_user(username='same', email='u2@e.com')

    def test_role_activation_code_unique(self):
        RoleActivationCode.objects.create(code='SAME', role='jury')
        with self.assertRaises(Exception):
            RoleActivationCode.objects.create(code='SAME', role='team')

    def test_user_set_unusable_password(self):
        user = User.objects.create_user(username='unusable', email='un@e.com')
        user.set_unusable_password()
        self.assertFalse(user.has_usable_password())

    def test_user_needs_onboarding_can_be_true(self):
        user = User.objects.create_user(username='onboarding', email='on@e.com', needs_onboarding=True)
        self.assertTrue(user.needs_onboarding)

    def test_role_activation_code_is_used_tracking(self):
        user = User.objects.create_user(username='usedby', email='ub@e.com')
        code = RoleActivationCode.objects.create(code='UCODE', role='jury', is_used=True, used_by=user)
        self.assertTrue(code.is_used)
        self.assertEqual(code.used_by, user)

    def test_user_phone_max_length(self):
        user = User.objects.create_user(username='phone', email='p@e.com', phone='1'*20)
        self.assertEqual(user.phone, '1'*20)

    def test_user_city_max_length(self):
        user = User.objects.create_user(username='city', email='c@e.com', city='C'*100)
        self.assertEqual(user.city, 'C'*100)

    def test_role_choices(self):
        user = User.objects.create_user(username='jury_role', email='j@e.com', role='jury')
        self.assertEqual(user.role, 'jury')
