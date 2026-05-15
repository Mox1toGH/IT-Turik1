from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserPointsBalanceSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    balance = serializers.IntegerField()
    updated_at = serializers.DateTimeField()


class PointsTransactionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    order_id = serializers.IntegerField(allow_null=True, required=False)
    amount = serializers.IntegerField()
    reason = serializers.CharField()
    created_at = serializers.DateTimeField()


class AdminPointsBalanceModifySerializer(serializers.Serializer):
    OPERATION_ADD = 'add'
    OPERATION_SUBTRACT = 'subtract'
    OPERATION_SET = 'set'
    OPERATION_RESET = 'reset'

    OPERATION_CHOICES = (
        (OPERATION_ADD, 'Add'),
        (OPERATION_SUBTRACT, 'Subtract'),
        (OPERATION_SET, 'Set'),
        (OPERATION_RESET, 'Reset'),
    )

    operation = serializers.ChoiceField(choices=OPERATION_CHOICES)
    amount = serializers.IntegerField(required=False)
    reason = serializers.CharField(max_length=255)

    def validate(self, attrs):
        operation = attrs.get('operation')
        amount = attrs.get('amount')

        if operation in {self.OPERATION_ADD, self.OPERATION_SUBTRACT, self.OPERATION_SET} and amount is None:
            raise serializers.ValidationError({'amount': 'This field is required for this operation.'})

        if operation == self.OPERATION_RESET and amount is not None:
            raise serializers.ValidationError({'amount': 'Do not provide amount for reset operation.'})

        if operation in {self.OPERATION_ADD, self.OPERATION_SUBTRACT} and amount is not None and amount < 0:
            raise serializers.ValidationError({'amount': 'Use a non-negative number for add/subtract operations.'})

        return attrs


class UserLookupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')
