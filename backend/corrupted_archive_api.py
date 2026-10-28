from ninja import Router, Schema

router = Router(tags=['archive'], auth=None)
CORRUPTED_ARCHIVE_PASSWORD = 'TRIANGULUM VIGILAT'

class CorruptedArchivePasswordRequest(Schema):
    password: str

class CorruptedArchivePasswordResponse(Schema):
    valid: bool

@router.post(
    '/verify-corrupted-password',
    response=CorruptedArchivePasswordResponse,
    operation_id='verifyCorruptedArchivePassword',
)
def verify_corrupted_archive_password(request, payload: CorruptedArchivePasswordRequest):
    return {'valid': payload.password == CORRUPTED_ARCHIVE_PASSWORD}
