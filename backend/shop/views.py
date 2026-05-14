from django.db.models import Case, IntegerField, Value, When
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiResponse
from backend.openapi import _400, _401, _403, _404

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


@extend_schema(operation_id='listProducts', responses={
    200: ProductSerializer(many=True),
    400: _400,
    401: _401,
})
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


@extend_schema(operation_id='getProduct', responses={
    200: ProductSerializer,
    401: _401,
    404: _404,
})
class ProductDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.select_related('category').prefetch_related('images').filter(is_active=True)


class PurchaseView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(operation_id='purchaseProduct', responses={
        201: OrderSerializer,
        400: _400,
        401: _401,
    })
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


@extend_schema(operation_id='listMyOrders', responses={
    200: OrderSerializer(many=True),
    401: _401,
})
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

    @extend_schema(operation_id='cancelMyOrder', responses={
        200: OrderSerializer,
        400: _400,
        401: _401,
        403: _403,
        404: _404,
    })
    def post(self, request, order_id):
        order = get_object_or_404(Order.objects.select_related('user'), pk=order_id)
        if order.user_id != request.user.id:
            raise PermissionDenied('You can cancel only your own orders.')

        cancelled = cancel_order(order=order, cancelled_by=request.user)
        return Response(OrderSerializer(cancelled, context={'request': request}).data, status=status.HTTP_200_OK)


@extend_schema(methods=['GET'], operation_id='listAdminCategories', responses={
    200: CategorySerializer(many=True),
    401: _401,
    403: _403,
})
@extend_schema(methods=['POST'], operation_id='createAdminCategory', responses={
    201: CategorySerializer,
    400: _400,
    401: _401,
    403: _403,
})
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


@extend_schema(methods=['GET'], operation_id='getAdminCategory', responses={
    200: CategorySerializer,
    401: _401,
    403: _403,
    404: _404,
})
@extend_schema(methods=['PUT'], operation_id='replaceAdminCategory', responses={
    200: CategorySerializer,
    400: _400,
    401: _401,
    403: _403,
    404: _404,
})
@extend_schema(methods=['PATCH'], operation_id='updateAdminCategory', responses={
    200: CategorySerializer,
    400: _400,
    401: _401,
    403: _403,
    404: _404,
})
@extend_schema(methods=['DELETE'], operation_id='deleteAdminCategory', responses={
    204: OpenApiResponse(description='Category deleted successfully.'),
    401: _401,
    403: _403,
    404: _404,
})
class AdminCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def get_object(self):
        if not is_platform_admin(self.request.user):
            raise PermissionDenied('Only admins can manage categories.')
        return super().get_object()


@extend_schema(methods=['GET'], operation_id='listAdminProducts', responses={
    200: ProductSerializer(many=True),
    401: _401,
    403: _403,
})
@extend_schema(methods=['POST'], operation_id='createAdminProduct', responses={
    201: ProductSerializer,
    400: _400,
    401: _401,
    403: _403,
})
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


@extend_schema(methods=['GET'], operation_id='getAdminProduct', responses={
    200: ProductSerializer,
    401: _401,
    403: _403,
    404: _404,
})
@extend_schema(methods=['PUT'], operation_id='replaceAdminProduct', responses={
    200: ProductSerializer,
    400: _400,
    401: _401,
    403: _403,
    404: _404,
})
@extend_schema(methods=['PATCH'], operation_id='updateAdminProduct', responses={
    200: ProductSerializer,
    400: _400,
    401: _401,
    403: _403,
    404: _404,
})
@extend_schema(methods=['DELETE'], operation_id='deleteAdminProduct', responses={
    204: OpenApiResponse(description='Product deleted successfully.'),
    401: _401,
    403: _403,
    404: _404,
})
class AdminProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer

    def get_queryset(self):
        if not is_platform_admin(self.request.user):
            raise PermissionDenied('Only admins can manage products.')
        return Product.objects.select_related('category').prefetch_related('images')


@extend_schema(operation_id='listAdminOrders', responses={
    200: OrderSerializer(many=True),
    401: _401,
    403: _403,
})
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

    @extend_schema(operation_id='updateAdminOrderStatus', request=AdminOrderStatusUpdateSerializer, responses={
        200: OrderSerializer,
        400: _400,
        401: _401,
        403: _403,
        404: _404,
    })
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

    @extend_schema(operation_id='cancelAdminOrder', responses={
        200: OrderSerializer,
        400: _400,
        401: _401,
        403: _403,
        404: _404,
    })
    def post(self, request, order_id):
        if not is_platform_admin(request.user):
            raise PermissionDenied('Only admins can cancel orders.')

        order = get_object_or_404(Order, pk=order_id)
        cancelled = cancel_order(order=order, cancelled_by=request.user)
        return Response(OrderSerializer(cancelled, context={'request': request}).data, status=status.HTTP_200_OK)


@extend_schema(operation_id='listAvatarFrames', responses={
    200: AvatarFrameSerializer(many=True),
    401: _401,
})
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


@extend_schema(methods=['GET'], operation_id='listAdminAvatarFrames', responses={
    200: AvatarFrameSerializer(many=True),
    401: _401,
    403: _403,
})
@extend_schema(methods=['POST'], operation_id='createAdminAvatarFrame', responses={
    201: AvatarFrameSerializer,
    400: _400,
    401: _401,
    403: _403,
})
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


@extend_schema(methods=['GET'], operation_id='getAdminAvatarFrame', responses={
    200: AvatarFrameSerializer,
    401: _401,
    403: _403,
    404: _404,
})
@extend_schema(methods=['PUT'], operation_id='replaceAdminAvatarFrame', responses={
    200: AvatarFrameSerializer,
    400: _400,
    401: _401,
    403: _403,
    404: _404,
})
@extend_schema(methods=['PATCH'], operation_id='updateAdminAvatarFrame', responses={
    200: AvatarFrameSerializer,
    400: _400,
    401: _401,
    403: _403,
    404: _404,
})
@extend_schema(methods=['DELETE'], operation_id='deleteAdminAvatarFrame', responses={
    204: OpenApiResponse(description='Avatar frame deleted successfully.'),
    401: _401,
    403: _403,
    404: _404,
})
class AdminAvatarFrameDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AvatarFrameSerializer

    def get_queryset(self):
        if not is_platform_admin(self.request.user):
            raise PermissionDenied('Only admins can manage avatar frames.')
        return AvatarFrame.objects.all()


