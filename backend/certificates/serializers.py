from rest_framework import serializers
from .models import Certificate, CertificateTemplate


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

    def get_certificate_url(self, obj):
        request = self.context.get('request')
        if request:
            # We will use the custom action 'view' on the viewset
            return request.build_absolute_uri(f"/api/certificates/{obj.unique_code}/view/")
        return None

    def get_full_name(self, obj):
        return obj.full_name

    def get_team_name(self, obj):
        return obj.team_name

    def get_tournament_name(self, obj):
        return obj.tournament_name
