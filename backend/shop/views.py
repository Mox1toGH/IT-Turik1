from django.db.models import Case, IntegerField, Value, When
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.permissions import is_platform_admin

from .models import AvatarFrame, Category, Order, Product
from .serializers import (
    AdminOrderStatusUpdateSerializer,
    AvatarFrameSerializer,
    CategorySerializer,
    OrderSerializer,
    ProductSerializer,
    PurchaseSerializer,
)
from .services import cancel_order, create_order_purchase

class ShopPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProductListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer
    pagination_class = ShopPagination

    def get_queryset(self):
        queryset = Product.objects.select_related('category').prefetch_related('images').filter(is_active=True)

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)

        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        product_type = self.request.query_params.get('product_type')
        if product_type:
            queryset = queryset.filter(product_type=product_type)

        ordering = self.request.query_params.get('ordering', 'name')
        allowed = {'name', '-name', 'price', '-price'}
        if ordering not in allowed:
            raise ValidationError({'ordering': 'Unsupported ordering. Use name, -name, price, or -price.'})

        queryset = queryset.annotate(
            available_sort=Case(
                When(stock_quantity__gt=0, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
        )
        return queryset.order_by('available_sort', ordering, 'id')


class ProductDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.select_related('category').prefetch_related('images').filter(is_active=True)


class PurchaseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PurchaseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payload = serializer.validated_data
        try:
            order = create_order_purchase(
                user=request.user,
                product_id=payload['product_id'],
                quantity=payload['quantity'],
            )
        except Product.DoesNotExist:
            raise ValidationError({'product_id': 'Active product not found.'})

        if order:
            data = OrderSerializer(order, context={'request': request}).data
        else:
            data = {'message': 'Digital product purchased successfully and added to your inventory.'}

        return Response(data, status=status.HTTP_201_CREATED)


class MyOrderHistoryView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    pagination_class = ShopPagination

    def get_queryset(self):
        return Order.objects.select_related('user', 'product', 'product__category').prefetch_related('product__images').filter(
            user=self.request.user
        )


class MyOrderCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(Order.objects.select_related('user'), pk=order_id)
        if order.user_id != request.user.id:
            raise PermissionDenied('You can cancel only your own orders.')

        cancelled = cancel_order(order=order, cancelled_by=request.user)
        return Response(OrderSerializer(cancelled, context={'request': request}).data, status=status.HTTP_200_OK)


class AdminCategoryListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    pagination_class = ShopPagination

    def get_queryset(self):
        if not is_platform_admin(self.request.user):
            raise PermissionDenied('Only admins can manage categories.')
        return super().get_queryset()

    def perform_create(self, serializer):
        if not is_platform_admin(self.request.user):
            raise PermissionDenied('Only admins can manage categories.')
        serializer.save()


class AdminCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def get_object(self):
        if not is_platform_admin(self.request.user):
            raise PermissionDenied('Only admins can manage categories.')
        return super().get_object()


class AdminProductListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer
    pagination_class = ShopPagination

    def get_queryset(self):
        if not is_platform_admin(self.request.user):
            raise PermissionDenied('Only admins can manage products.')
        queryset = Product.objects.select_related('category').prefetch_related('images')

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)

        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        product_type = self.request.query_params.get('product_type')
        if product_type:
            queryset = queryset.filter(product_type=product_type)

        return queryset.order_by('name', 'id')

    def perform_create(self, serializer):
        if not is_platform_admin(self.request.user):
            raise PermissionDenied('Only admins can manage products.')
        serializer.save()


class AdminProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer

    def get_queryset(self):
        if not is_platform_admin(self.request.user):
            raise PermissionDenied('Only admins can manage products.')
        return Product.objects.select_related('category').prefetch_related('images')


class AdminOrderListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    pagination_class = ShopPagination

    def get_queryset(self):
        if not is_platform_admin(self.request.user):
            raise PermissionDenied('Only admins can view all orders.')

        queryset = Order.objects.select_related('user', 'product', 'product__category').prefetch_related('product__images')

        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        user_id = self.request.query_params.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        return queryset


class AdminOrderStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, order_id):
        if not is_platform_admin(request.user):
            raise PermissionDenied('Only admins can change order status.')

        order = get_object_or_404(Order, pk=order_id)
        serializer = AdminOrderStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order.status = serializer.validated_data['status']
        order.save(update_fields=['status', 'updated_at'])
        return Response(OrderSerializer(order, context={'request': request}).data, status=status.HTTP_200_OK)


class AdminOrderCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        if not is_platform_admin(request.user):
            raise PermissionDenied('Only admins can cancel orders.')

        order = get_object_or_404(Order, pk=order_id)
        cancelled = cancel_order(order=order, cancelled_by=request.user)
        return Response(OrderSerializer(cancelled, context={'request': request}).data, status=status.HTTP_200_OK)


class AvatarFrameListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AvatarFrameSerializer
    pagination_class = ShopPagination

    def get_queryset(self):
        queryset = AvatarFrame.objects.filter(is_active=True)

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)

        return queryset.order_by('name')


class AdminAvatarFrameListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AvatarFrameSerializer
    pagination_class = ShopPagination

    def get_queryset(self):
        if not is_platform_admin(self.request.user):
            raise PermissionDenied('Only admins can manage avatar frames.')
        queryset = AvatarFrame.objects.all()

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)

        return queryset.order_by('name', 'id')

    def perform_create(self, serializer):
        if not is_platform_admin(self.request.user):
            raise PermissionDenied('Only admins can manage avatar frames.')
        serializer.save()


class AdminAvatarFrameDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AvatarFrameSerializer

    def get_queryset(self):
        if not is_platform_admin(self.request.user):
            raise PermissionDenied('Only admins can manage avatar frames.')
        return AvatarFrame.objects.all()


