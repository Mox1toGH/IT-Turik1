from rest_framework import serializers
from .models import Certificate, CertificateTemplate
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes


class CertificateTemplateSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = CertificateTemplate
        fields = ['id', 'name', 'image', 'is_default', 'image_url', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class CertificateSerializer(serializers.ModelSerializer):
    certificate_url = serializers.SerializerMethodField()
    template_name = serializers.ReadOnlyField(source='template.name')
    full_name = serializers.SerializerMethodField(read_only=True)
    team_name = serializers.SerializerMethodField(read_only=True)
    tournament_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Certificate
        fields = [
            'id', 'unique_code', 'user', 'full_name', 'team', 'team_name',
            'tournament', 'tournament_name', 'placement', 'certificate_number',
            'template', 'template_name', 'certificate_url', 'created_at'
        ]
        read_only_fields = ['id', 'unique_code', 'created_at', 'certificate_url', 'full_name', 'team_name', 'tournament_name']
        extra_kwargs = {
            'certificate_number': {'required': False, 'allow_blank': True},
        }

    @extend_schema_field(OpenApiTypes.URI)
    def get_certificate_url(self, obj):
        request = self.context.get('request')
        if request:
            # We will use the custom action 'view' on the viewset
            return request.build_absolute_uri(f"/api/certificates/{obj.unique_code}/view/")
        return None

    @extend_schema_field(OpenApiTypes.STR)
    def get_full_name(self, obj):
        return obj.full_name

    @extend_schema_field(OpenApiTypes.STR)
    def get_team_name(self, obj):
        return obj.team_name

    @extend_schema_field(OpenApiTypes.STR)
    def get_tournament_name(self, obj):
        return obj.tournament_name

    def _resolve_default_template(self):
        return CertificateTemplate.objects.filter(is_default=True).first()

    def create(self, validated_data):
        # If "Default template" was selected (template=null), pin the current
        # default template to keep certificate background immutable over time.
        if validated_data.get('template') is None:
            validated_data['template'] = self._resolve_default_template()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Preserve deterministic template selection for updates as well.
        if 'template' in validated_data and validated_data.get('template') is None:
            validated_data['template'] = self._resolve_default_template()
        return super().update(instance, validated_data)
