from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Category, Order, Product, ProductImage

User = get_user_model()


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'image', 'created_at')
        read_only_fields = ('id', 'created_at')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )
    images = ProductImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
        allow_empty=False,
    )
    is_available = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'description',
            'price',
            'stock_quantity',
            'category',
            'category_id',
            'product_type',
            'images',
            'uploaded_images',
            'is_active',
            'is_available',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'is_available')

    def get_is_available(self, obj):
        return bool(obj.is_active and obj.stock_quantity > 0)

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        product = super().create(validated_data)
        for image in uploaded_images:
            ProductImage.objects.create(product=product, image=image)
        return product

    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', None)
        instance = super().update(instance, validated_data)
        if uploaded_images:
            for image in uploaded_images:
                ProductImage.objects.create(product=instance, image=image)
        return instance


class PurchaseSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1)


class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'full_name')


class OrderSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    user = UserShortSerializer(read_only=True)
    user_profile_url = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            'id',
            'user',
            'user_profile_url',
            'product',
            'quantity',
            'total_cost',
            'status',
            'created_at',
            'updated_at',
        )
        read_only_fields = fields

    def get_user_profile_url(self, obj):
        request = self.context.get('request')
        if request is None:
            return f'/api/accounts/users/{obj.user_id}/'
        return request.build_absolute_uri(f'/api/accounts/users/{obj.user_id}/')


class AdminOrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)

    def validate_status(self, value):
        if value == Order.STATUS_CANCELLED:
            raise serializers.ValidationError('Use the cancel endpoint to cancel orders.')
        return value
