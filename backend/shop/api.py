from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Case, IntegerField, Value, When
from django.shortcuts import get_object_or_404

from ninja import File, Form, Router
from ninja.errors import HttpError
from ninja.files import UploadedFile
from ninja.pagination import PageNumberPagination, paginate

from backend.auth import JWTAuth
from backend.permissions import is_platform_admin
from notifications.services import NotificationService

from .models import AvatarFrame, Category, Order, Product, ProductImage

from backend.schemas import ErrorResponse
from .schemas import AvatarFrameRequest, AvatarFrameResponse, CategoryRequest, CategoryResponse, OrderResponse, OrderStatusRequest, ProductRequest, ProductResponse, PurchaseDigitalResponse, PurchaseOrderResponse, PurchaseRequest
from .services import cancel_order, create_order_purchase

router = Router(tags=['shop'], auth=JWTAuth())


def _require_admin(request):
    if not is_platform_admin(request.auth):
        raise HttpError(403, 'Admin access required.')


def _products(active_only=False):
    queryset = Product.objects.select_related('category', 'avatar_frame').prefetch_related('images')
    return queryset.filter(is_active=True) if active_only else queryset


def _product_filters(queryset, search: str | None, category: int | None, product_type: str | None, ordering: str = 'name'):
    if search:
        queryset = queryset.filter(name__icontains=search)
    if category:
        queryset = queryset.filter(category_id=category)
    if product_type:
        queryset = queryset.filter(product_type=product_type)
    if ordering not in {'name', '-name', 'price', '-price'}:
        raise HttpError(400, 'Unsupported ordering. Use name, -name, price, or -price.')
    return queryset.annotate(available_sort=Case(When(stock_quantity__gt=0, then=Value(0)), default=Value(1), output_field=IntegerField())).order_by('available_sort', ordering, 'id')


def _save_product(product, payload, uploaded_images=None, avatar_frame_file=None):
    data = payload.model_dump()
    category = get_object_or_404(Category, pk=data.pop('category_id'))
    avatar_frame_id = data.pop('avatar_frame_id')
    avatar_frame = get_object_or_404(AvatarFrame.objects.filter(is_active=True), pk=avatar_frame_id) if avatar_frame_id else None
    for field, value in data.items():
        setattr(product, field, value)
    product.category = category
    product.avatar_frame = avatar_frame

    if avatar_frame_file and product.product_type == Product.TYPE_DIGITAL:
        frame, created = AvatarFrame.objects.get_or_create(
            name=product.name,
            defaults={'svg_file': avatar_frame_file},
        )
        if not created:
            frame.svg_file = avatar_frame_file
            frame.save(update_fields=['svg_file', 'updated_at'])
        product.avatar_frame = frame

    product.full_clean()
    product.save()

    for image in uploaded_images or []:
        ProductImage.objects.create(product=product, image=image)

    return product


@router.get('/products', operation_id='listProducts', response={200: list[ProductResponse], 400: ErrorResponse, 401: ErrorResponse})
@paginate(PageNumberPagination, page_size=20)
def list_products(request, search: str | None = None, category: int | None = None, product_type: str | None = None, ordering: str = 'name'):
    return _product_filters(_products(active_only=True), search, category, product_type, ordering)


@router.get('/products/{product_id}', operation_id='getProduct', response={200: ProductResponse, 401: ErrorResponse, 404: ErrorResponse})
def get_product(request, product_id: int):
    product = get_object_or_404(_products(active_only=True), pk=product_id),
    
    return ProductResponse.model_validate(
        product,
        from_attributes=True,
    )


@router.post('/purchase', operation_id='purchaseProduct', response={201: PurchaseOrderResponse | PurchaseDigitalResponse, 400: ErrorResponse, 401: ErrorResponse})
def purchase_product(request, payload: PurchaseRequest):
    try:
        order = create_order_purchase(user=request.auth, product_id=payload.product_id, quantity=payload.quantity)
    except Product.DoesNotExist:
        raise HttpError(400, 'Active product not found.')
    except ValidationError as exc:
        raise HttpError(400, exc.message_dict) from None
    
    if order is None:
        return 201, PurchaseDigitalResponse(
            message='Digital product purchased successfully and added to your inventory.'
        )

    return 201, PurchaseOrderResponse.model_validate(
        order,
        from_attributes=True,
    )

@router.get('/orders/my', operation_id='listMyOrders', response={200: list[OrderResponse], 401: ErrorResponse})
@paginate(PageNumberPagination, page_size=20)
def list_my_orders(request):
    return Order.objects.select_related('user', 'product', 'product__category', 'product__avatar_frame').prefetch_related('product__images').filter(user=request.auth)


@router.post('/orders/my/{order_id}/cancel', operation_id='cancelMyOrder', response={200: OrderResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def cancel_my_order(request, order_id: int):
    order = get_object_or_404(Order.objects.select_related('user'), pk=order_id)

    if order.user_id != request.auth.id:
        raise HttpError(403, 'You can cancel only your own orders.')
    try:
        return cancel_order(order=order, cancelled_by=request.auth)
    except ValidationError as exc:
        raise HttpError(400, exc.message_dict) from None


@router.get('/admin/categories', operation_id='listAdminCategories', response={200: list[CategoryResponse], 401: ErrorResponse, 403: ErrorResponse})
@paginate(PageNumberPagination, page_size=20)
def list_admin_categories(request):
    _require_admin(request)

    return Category.objects.all()


@router.post('/admin/categories', operation_id='createAdminCategory', response={201: CategoryResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse})
def create_admin_category(request, payload: CategoryRequest):
    _require_admin(request)

    try:
        category = Category.objects.create(name=payload.name)
    except IntegrityError:
        raise HttpError(400, 'A category with this name already exists.') from None

    return 201, CategoryResponse.model_validate(
        category,
        from_attributes=True,
    )


@router.get('/admin/categories/{category_id}', operation_id='getAdminCategory', response={200: CategoryResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def get_admin_category(request, category_id: int):
    _require_admin(request)

    return CategoryResponse.model_validate(
        get_object_or_404(Category, pk=category_id),
        from_attributes=True,
    )


@router.put('/admin/categories/{category_id}', operation_id='replaceAdminCategory', response={200: CategoryResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
@router.patch('/admin/categories/{category_id}', operation_id='updateAdminCategory', response={200: CategoryResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def update_admin_category(request, category_id: int, payload: CategoryRequest):
    _require_admin(request)

    category = get_object_or_404(Category, pk=category_id)
    category.name = payload.name
    try:
        category.save()
    except IntegrityError:
        raise HttpError(400, 'A category with this name already exists.') from None
    
    return CategoryResponse.model_validate(
        category,
        from_attributes=True,
    )


@router.delete('/admin/categories/{category_id}', operation_id='deleteAdminCategory', response={204: None, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def delete_admin_category(request, category_id: int):
    _require_admin(request)
    get_object_or_404(Category, pk=category_id).delete()
    
    return 204, None


@router.get('/admin/products', operation_id='listAdminProducts', response={200: list[ProductResponse], 401: ErrorResponse, 403: ErrorResponse})
@paginate(PageNumberPagination, page_size=20)
def list_admin_products(request, search: str | None = None, category: int | None = None, product_type: str | None = None):
    _require_admin(request)

    return _product_filters(_products(), search, category, product_type)


@router.post('/admin/products', operation_id='createAdminProduct', response={201: ProductResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse})
def create_admin_product(
    request,
    payload: Form[ProductRequest],
    uploaded_images: list[UploadedFile] = File(None),
    avatar_frame_file: UploadedFile | None = File(None),
):
    _require_admin(request)

    try:
        return 201, ProductResponse.model_validate(
            _save_product(Product(), payload, uploaded_images, avatar_frame_file),
            from_attributes=True,
        )
    except ValidationError as exc:
        raise HttpError(400, exc.message_dict) from None


@router.get('/admin/products/{product_id}', operation_id='getAdminProduct', response={200: ProductResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def get_admin_product(request, product_id: int):
    _require_admin(request)

    return ProductResponse.model_validate(
        get_object_or_404(_products(), pk=product_id),
        from_attributes=True,
    )


@router.put('/admin/products/{product_id}', operation_id='replaceAdminProduct', response={200: ProductResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
@router.patch('/admin/products/{product_id}', operation_id='updateAdminProduct', response={200: ProductResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def update_admin_product(
    request,
    product_id: int,
    payload: Form[ProductRequest],
    uploaded_images: list[UploadedFile] = File(None),
    avatar_frame_file: UploadedFile | None = File(None),
):
    _require_admin(request)

    try:
        return ProductResponse.model_validate(
            _save_product(
                get_object_or_404(_products(), pk=product_id),
                payload,
                uploaded_images,
                avatar_frame_file,
            ),
            from_attributes=True,
        )
    except ValidationError as exc:
        raise HttpError(400, exc.message_dict) from None


@router.delete('/admin/products/{product_id}', operation_id='deleteAdminProduct', response={204: None, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def delete_admin_product(request, product_id: int):
    _require_admin(request)
    product = get_object_or_404(_products(), pk=product_id)

    if product.orders.exists() or product.owned_by_users.exists():
        product.is_active = False
        product.save(update_fields=['is_active', 'updated_at'])
    else:
        product.delete()

    return 204, None


@router.get('/admin/orders', operation_id='listAdminOrders', response={200: list[OrderResponse], 401: ErrorResponse, 403: ErrorResponse})
@paginate(PageNumberPagination, page_size=20)
def list_admin_orders(request, status: str | None = None, user: int | None = None):
    _require_admin(request)
    queryset = Order.objects.select_related('user', 'product', 'product__category', 'product__avatar_frame').prefetch_related('product__images')
    
    return queryset.filter(status=status) if status else queryset.filter(user_id=user) if user else queryset


@router.patch('/admin/orders/{order_id}/status', operation_id='updateAdminOrderStatus', response={200: OrderResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def update_admin_order_status(request, order_id: int, payload: OrderStatusRequest):
    _require_admin(request)

    order = get_object_or_404(Order.objects.select_related('user', 'product'), pk=order_id)
    order.status = payload.status
    order.save(update_fields=['status', 'updated_at'])
    
    NotificationService.notify(recipients=[order.user], event_type='shop_order_status_changed', context={'order_id': order.id, 'product_name': order.product.name, 'order_status': order.status})
    
    return OrderResponse.model_validate(
        order,
        from_attributes=True,
    )


@router.post('/admin/orders/{order_id}/cancel', operation_id='cancelAdminOrder', response={200: OrderResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def cancel_admin_order(request, order_id: int):
    _require_admin(request)
    order = get_object_or_404(Order.objects.select_related('user', 'product'), pk=order_id)
    
    try:
        cancelled = cancel_order(order=order, cancelled_by=request.auth)
    except ValidationError as exc:
        raise HttpError(400, exc.message_dict) from None
    NotificationService.notify(recipients=[cancelled.user], event_type='shop_order_status_changed', context={'order_id': cancelled.id, 'product_name': cancelled.product.name, 'order_status': cancelled.status})
    
    return OrderResponse.model_validate(
        cancelled,
        from_attributes=True,
    )


@router.get('/avatar-frames', operation_id='listAvatarFrames', response={200: list[AvatarFrameResponse], 401: ErrorResponse})
@paginate(PageNumberPagination, page_size=20)
def list_avatar_frames(request, search: str | None = None):
    queryset = AvatarFrame.objects.filter(is_active=True)

    return queryset.filter(name__icontains=search).order_by('name') if search else queryset.order_by('name')


@router.get('/admin/avatar-frames', operation_id='listAdminAvatarFrames', response={200: list[AvatarFrameResponse], 401: ErrorResponse, 403: ErrorResponse})
@paginate(PageNumberPagination, page_size=20)
def list_admin_avatar_frames(request, search: str | None = None):
    _require_admin(request)
    queryset = AvatarFrame.objects.all()
    
    return queryset.filter(name__icontains=search).order_by('name', 'id') if search else queryset.order_by('name', 'id')


@router.post('/admin/avatar-frames', operation_id='createAdminAvatarFrame', response={201: AvatarFrameResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse})
def create_admin_avatar_frame(request, payload: AvatarFrameRequest):
    _require_admin(request)

    return 201, AvatarFrameResponse.model_validate(
        AvatarFrame.objects.create(**payload.model_dump()),
        from_attributes=True,
    )


@router.get('/admin/avatar-frames/{frame_id}', operation_id='getAdminAvatarFrame', response={200: AvatarFrameResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def get_admin_avatar_frame(request, frame_id: int):
    _require_admin(request)

    return AvatarFrameResponse.model_validate(
        get_object_or_404(AvatarFrame, pk=frame_id),
        from_attributes=True,
    )


@router.put('/admin/avatar-frames/{frame_id}', operation_id='replaceAdminAvatarFrame', response={200: AvatarFrameResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
@router.patch('/admin/avatar-frames/{frame_id}', operation_id='updateAdminAvatarFrame', response={200: AvatarFrameResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def update_admin_avatar_frame(request, frame_id: int, payload: AvatarFrameRequest):
    _require_admin(request)
    frame = get_object_or_404(AvatarFrame, pk=frame_id)
    
    for field, value in payload.model_dump().items():
        setattr(frame, field, value)
    frame.save()
    
    return AvatarFrameResponse.model_validate(
        frame,
        from_attributes=True,
    )


@router.delete('/admin/avatar-frames/{frame_id}', operation_id='deleteAdminAvatarFrame', response={204: None, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def delete_admin_avatar_frame(request, frame_id: int):
    _require_admin(request)
    get_object_or_404(AvatarFrame, pk=frame_id).delete()
    
    return 204, None
