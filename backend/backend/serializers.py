from rest_framework import serializers

class BaseValidationErrorResponseSerializer(serializers.Serializer):
    code = serializers.CharField(default='validation_error')
    message = serializers.CharField(default='Validation failed.')


def build_validation_error_serializer(serializer_class):
    serializer_instance = serializer_class()

    fields = {
        field_name: serializers.ListField(
            child=serializers.CharField()
        )
        for field_name in serializer_instance.fields
    }

    details_serializer = type(
        f'{serializer_class.__name__}ValidationDetailsSerializer',
        (serializers.Serializer,),
        fields,
    )

    return type(
        f'{serializer_class.__name__}ValidationErrorSerializer',
        (BaseValidationErrorResponseSerializer,),
        {
            'details': details_serializer(),
        },
    )