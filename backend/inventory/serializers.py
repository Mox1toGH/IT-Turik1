from rest_framework import serializers
from shop.serializers import ProductSerializer
from .models import UserInventory


class DigitalInventoryItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = UserInventory
        fields = ('id', 'product', 'is_equipped', 'acquired_at', 'updated_at')
        read_only_fields = fields


class EquipDigitalItemSerializer(serializers.Serializer):
    inventory_id = serializers.IntegerField(min_value=1)
