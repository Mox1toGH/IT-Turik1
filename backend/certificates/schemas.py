from datetime import datetime
from typing import Optional

from backend.media import absolute_media_url
from ninja import Schema

class CertificateTemplateResponse(Schema):
    id: int
    name: str
    image: Optional[str] = None
    image_url: Optional[str] = None
    is_default: bool
    created_at: datetime

    @staticmethod
    def resolve_image(obj, context):
        return absolute_media_url(obj.image, context)

    @staticmethod
    def resolve_image_url(obj, context):
        return absolute_media_url(obj.image, context)


class CertificateTemplateRequest(Schema):
    name: str
    is_default: bool = False


class CertificateResponse(Schema):
    id: int
    unique_code: str
    user: int | None
    full_name: str
    team: int | None
    team_name: str
    tournament: int | None
    tournament_name: str
    placement: str
    certificate_number: str
    template: int | None
    template_name: str
    certificate_url: str
    created_at: datetime

    @staticmethod
    def resolve_user(obj):
        return obj.user_id

    @staticmethod
    def resolve_team(obj):
        return obj.team_id

    @staticmethod
    def resolve_tournament(obj):
        return obj.tournament_id

    @staticmethod
    def resolve_template(obj):
        return obj.template_id

    @staticmethod
    def resolve_template_name(obj):
        return obj.template.name if obj.template else ''

    @staticmethod
    def resolve_certificate_url(obj, context):
        request = (context or {}).get('request')
        path = f'/api/certificates/{obj.unique_code}/view'
        return request.build_absolute_uri(path) if request else path


class CertificateRequest(Schema):
    user: int | None = None
    team: int | None = None
    tournament: int | None = None
    placement: str
    certificate_number: str = ''
    template: int | None = None


class CertificateVerifyResponse(Schema):
    is_valid: bool
    data: CertificateResponse | None = None
    message: str | None = None
