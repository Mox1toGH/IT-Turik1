import re
import secrets
import string

from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import serializers

from .models import RoleActivationCode, User


RESTRICTED_ROLES = {'jury', 'organizer', 'admin'}
MAX_ACTIVE_CODES_PER_ROLE = 10


def validate_strong_password(password, user=None, field_name='password'):
    errors = []
    if not re.search(r'[A-Z]', password):
        errors.append('Password must include at least one uppercase letter.')
    if not re.search(r'[a-z]', password):
        errors.append('Password must include at least one lowercase letter.')
    if not re.search(r'\d', password):
        errors.append('Password must include at least one digit.')
    if not re.search(r'[^A-Za-z0-9]', password):
        errors.append('Password must include at least one special character.')
    if errors:
        raise serializers.ValidationError({field_name: errors})

    validate_password(password, user=user)


def generate_unique_role_code(length=12):
    alphabet = string.ascii_uppercase + string.digits
    for _ in range(20):
        code = ''.join(secrets.choice(alphabet) for _ in range(length))
        if not RoleActivationCode.objects.filter(code=code).exists():
            return code
    raise serializers.ValidationError({'message': ['Unable to generate a unique activation code. Please retry.']})


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    redeem_code = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'role', 'redeem_code', 'full_name', 'phone', 'city')

    def validate_phone(self, value):
        if value and not re.match(r'^\+?1?\d{9,15}$', value):
            raise serializers.ValidationError('Invalid phone number format.')
        return value

    def validate(self, attrs):
        role = attrs.get('role') or 'team'
        redeem_code = (attrs.get('redeem_code') or '').strip()

        if role in RESTRICTED_ROLES:
            if not redeem_code:
                raise serializers.ValidationError(
                    {'redeem_code': 'A valid activation code is required for this role.'}
                )
            role_code = RoleActivationCode.objects.filter(code=redeem_code).first()
            if role_code is None:
                raise serializers.ValidationError({'redeem_code': 'Activation code is invalid.'})
            if role_code.is_used:
                raise serializers.ValidationError({'redeem_code': 'Activation code has already been used.'})
            if role_code.role != role:
                raise serializers.ValidationError(
                    {'redeem_code': f'This code is not valid for the selected role "{role}".'}
                )
            attrs['_role_code_id'] = role_code.id
        else:
            attrs['role'] = 'team'
            attrs.pop('redeem_code', None)

        password = attrs.get('password')
        if password:
            user_for_validation = User(
                username=attrs.get('username', ''),
                email=attrs.get('email', ''),
                full_name=attrs.get('full_name', ''),
            )
            validate_strong_password(password, user=user_for_validation)
        return attrs

    def create(self, validated_data):
        role_code_id = validated_data.pop('_role_code_id', None)
        password = validated_data.pop('password')
        validated_data.pop('redeem_code', None)
        with transaction.atomic():
            role_code = None
            if role_code_id is not None:
                role_code = RoleActivationCode.objects.select_for_update().get(id=role_code_id)
                if role_code.is_used:
                    raise serializers.ValidationError({'redeem_code': 'Activation code has already been used.'})
                if role_code.role != validated_data.get('role'):
                    raise serializers.ValidationError({'redeem_code': 'Activation code role mismatch.'})

            user = User.objects.create_user(
                is_active=False,
                needs_onboarding=False,
                **validated_data,
            )

            user.set_password(password)
            if user.role == 'admin':
                user.is_staff = True
                user.is_superuser = True
                user.save(update_fields=['password', 'is_staff', 'is_superuser'])
            else:
                user.save(update_fields=['password'])

            if role_code is not None:
                role_code.is_used = True
                role_code.used_by = user
                role_code.used_at = timezone.now()
                role_code.save(update_fields=['is_used', 'used_by', 'used_at'])

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            activation_link = f"http://localhost:5173/activate/{uid}/{token}"
            send_mail(
                subject='Account activation',
                message=f'Open this link to activate your account: {activation_link}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )
            return user


class UserSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(source='date_joined', read_only=True)
    teams = serializers.SerializerMethodField()
    avatar = serializers.ImageField(read_only=True)
    avatar_frame_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'role',
            'full_name',
            'phone',
            'city',
            'avatar',
            'avatar_frame_url',
            'created_at',
            'needs_onboarding',
            'teams',
        )
        read_only_fields = ('id', 'email', 'created_at', 'needs_onboarding', 'teams')

    def get_avatar_frame_url(self, obj):
        from inventory.models import UserInventory

        equipped_item = (
            UserInventory.objects.select_related('product', 'product__avatar_frame')
            .filter(user=obj, is_equipped=True)
            .first()
        )
        if equipped_item is None:
            return None

        url = equipped_item.product.effective_digital_asset_url
        if not url:
            return None

        request = self.context.get('request')
        if request and url.startswith('/'):
            return request.build_absolute_uri(url)
        return url

    def get_teams(self, obj):
        return [
            {
                'id': team.id,
                'name': team.name,
                'contact_telegram': team.contact_telegram,
                'contact_discord': team.contact_discord,
            }
            for team in obj.teams.all()
        ]


class TeamUserListSerializer(serializers.ModelSerializer):
    avatar_frame_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'full_name', 'role', 'avatar', 'avatar_frame_url')

    def get_avatar_frame_url(self, obj):
        from inventory.models import UserInventory

        equipped_item = (
            UserInventory.objects.select_related('product', 'product__avatar_frame')
            .filter(user=obj, is_equipped=True)
            .first()
        )
        if equipped_item is None:
            return None
        return equipped_item.product.effective_digital_asset_url or None


class UserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    redeem_code = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ('username', 'role', 'full_name', 'phone', 'city', 'password', 'redeem_code')

    def validate_username(self, value):
        if self.instance and self.instance.username == value:
            return value
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('A user with this username already exists.')
        return value

    def validate_phone(self, value):
        if value and not re.match(r'^\+?1?\d{9,15}$', value):
            raise serializers.ValidationError('Invalid phone number format.')
        return value

    def validate(self, attrs):
        if self.instance and self.instance.needs_onboarding and 'role' not in self.initial_data:
            raise serializers.ValidationError({'role': 'Please select a role to complete Google registration.'})

        if self.instance:
            target_role = attrs.get('role', self.instance.role)
            is_role_change = target_role != self.instance.role
            redeem_code = (attrs.get('redeem_code') or '').strip()

            if target_role in RESTRICTED_ROLES and is_role_change:
                if not redeem_code:
                    raise serializers.ValidationError(
                        {'redeem_code': 'A valid activation code is required for this role.'}
                    )
                role_code = RoleActivationCode.objects.filter(code=redeem_code).first()
                if role_code is None:
                    raise serializers.ValidationError({'redeem_code': 'Activation code is invalid.'})
                if role_code.is_used:
                    raise serializers.ValidationError({'redeem_code': 'Activation code has already been used.'})
                if role_code.role != target_role:
                    raise serializers.ValidationError(
                        {'redeem_code': f'This code is not valid for the selected role "{target_role}".'}
                    )
                attrs['_role_code_id'] = role_code.id

        if (
            self.instance
            and self.instance.needs_onboarding
            and not self.instance.has_usable_password()
            and 'password' not in self.initial_data
        ):
            raise serializers.ValidationError(
                {'password': 'Please set a password to complete Google registration.'}
            )
        password = attrs.get('password')
        if password and self.instance:
            user_for_validation = User(
                username=attrs.get('username', self.instance.username),
                email=self.instance.email,
                full_name=attrs.get('full_name', self.instance.full_name),
            )
            validate_strong_password(password, user=user_for_validation)
        return attrs

    def update(self, instance, validated_data):
        role_code_id = validated_data.pop('_role_code_id', None)
        validated_data.pop('redeem_code', None)
        password = validated_data.pop('password', None)

        with transaction.atomic():
            role_code = None
            if role_code_id is not None:
                role_code = RoleActivationCode.objects.select_for_update().get(id=role_code_id)
                target_role = validated_data.get('role', instance.role)
                if role_code.is_used:
                    raise serializers.ValidationError({'redeem_code': 'Activation code has already been used.'})
                if role_code.role != target_role:
                    raise serializers.ValidationError({'redeem_code': 'Activation code role mismatch.'})

            for attr, value in validated_data.items():
                setattr(instance, attr, value)

            if password:
                instance.set_password(password)

            if instance.role == 'admin':
                instance.is_staff = True
                instance.is_superuser = True

            update_fields = list(validated_data.keys())
            if password:
                update_fields.append('password')
            if instance.role == 'admin':
                update_fields.extend(['is_staff', 'is_superuser'])
            if instance.needs_onboarding:
                instance.needs_onboarding = False
                update_fields.append('needs_onboarding')

            update_fields = list(dict.fromkeys(update_fields))
            if update_fields:
                instance.save(update_fields=update_fields)

            if role_code is not None:
                role_code.is_used = True
                role_code.used_by = instance
                role_code.used_at = timezone.now()
                role_code.save(update_fields=['is_used', 'used_by', 'used_at'])

        return instance


class UserAvatarUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('avatar',)


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError('No account found with this email address.')
        return value

    def save(self):
        email = self.validated_data['email']
        user = User.objects.get(email=email)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_link = f"http://localhost:5173/reset-password/{uid}/{token}"

        send_mail(
            subject='Password reset',
            message=f'Open this link to reset your password: {reset_link}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

        return user


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = self.context.get('user')
        if user is None:
            raise serializers.ValidationError({'message': ['Invalid password reset request.']})

        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')
        if new_password != confirm_password:
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match.'})

        validate_strong_password(new_password, user=user, field_name='new_password')
        return attrs

    def save(self):
        user = self.context['user']
        user.set_password(self.validated_data['new_password'])
        user.save(update_fields=['password'])
        return user


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = self.context.get('user')
        if user is None:
            raise serializers.ValidationError({'message': ['Invalid request context.']})

        current_password = attrs.get('current_password')
        if not user.check_password(current_password):
            raise serializers.ValidationError({'current_password': 'Current password is incorrect.'})

        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')
        if new_password != confirm_password:
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match.'})

        validate_strong_password(new_password, user=user, field_name='new_password')
        return attrs

    def save(self):
        user = self.context['user']
        user.set_password(self.validated_data['new_password'])
        user.save(update_fields=['password'])
        return user


class RoleActivationCodeSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    used_by_username = serializers.CharField(source='used_by.username', read_only=True)

    class Meta:
        model = RoleActivationCode
        fields = (
            'id',
            'code',
            'role',
            'is_used',
            'created_at',
            'used_at',
            'created_by_username',
            'used_by_username',
        )


class RoleActivationCodeGenerateSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=[(role, role) for role in RESTRICTED_ROLES])
    quantity = serializers.IntegerField(min_value=1, max_value=10, default=1)

    def validate(self, attrs):
        role = attrs['role']
        quantity = attrs['quantity']
        active_count = RoleActivationCode.objects.filter(role=role, is_used=False).count()
        remaining_slots = MAX_ACTIVE_CODES_PER_ROLE - active_count
        if remaining_slots <= 0:
            raise serializers.ValidationError({'role': f'Active code limit reached for "{role}" (10/10).'})
        if quantity > remaining_slots:
            raise serializers.ValidationError(
                {'quantity': f'Only {remaining_slots} additional active codes can be generated for "{role}".'}
            )
        return attrs

    def save(self):
        role = self.validated_data['role']
        quantity = self.validated_data['quantity']
        created_by = self.context['request'].user

        created_codes = []
        for _ in range(quantity):
            created_codes.append(
                RoleActivationCode.objects.create(
                    code=generate_unique_role_code(),
                    role=role,
                    created_by=created_by,
                )
            )
        return created_codes
