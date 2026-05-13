from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from shop.models import Product
from .models import UserInventory
from .serializers import DigitalInventoryItemSerializer, EquipDigitalItemSerializer


class InventoryPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class MyDigitalInventoryView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DigitalInventoryItemSerializer
    pagination_class = InventoryPagination

    def get_queryset(self):
        return UserInventory.objects.select_related('product', 'product__category').prefetch_related(
            'product__images'
        ).filter(user=self.request.user)


class EquipDigitalInventoryItemView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = EquipDigitalItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        inventory_item = get_object_or_404(
            UserInventory.objects.select_related('product').filter(user=request.user),
            pk=serializer.validated_data['inventory_id'],
        )

        if inventory_item.product.product_type != Product.TYPE_DIGITAL:
            raise ValidationError({'inventory_id': 'Only digital items can be equipped.'})

        UserInventory.objects.filter(
            user=request.user,
            is_equipped=True,
        ).update(is_equipped=False)
        inventory_item.is_equipped = True
        inventory_item.save(update_fields=['is_equipped', 'updated_at'])

        return Response(
            DigitalInventoryItemSerializer(inventory_item, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )


class UnequipDigitalInventoryItemView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = EquipDigitalItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        inventory_item = get_object_or_404(
            UserInventory.objects.select_related('product').filter(user=request.user),
            pk=serializer.validated_data['inventory_id'],
        )

        if not inventory_item.is_equipped:
            raise ValidationError({'inventory_id': 'Item is not equipped.'})

        inventory_item.is_equipped = False
        inventory_item.save(update_fields=['is_equipped', 'updated_at'])

        return Response(
            DigitalInventoryItemSerializer(inventory_item, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )
