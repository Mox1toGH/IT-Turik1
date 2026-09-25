from django.shortcuts import get_object_or_404

from ninja import Router
from ninja.errors import HttpError
from ninja.pagination import PageNumberPagination, paginate

from backend.auth import JWTAuth
from shop.models import Product

from .models import UserInventory

from backend.schemas import ErrorResponse
from .schemas import DigitalInventoryItemResponse, EquipDigitalItemRequest

router = Router(tags=['inventory'], auth=JWTAuth())


def _inventory_queryset(user):
    return UserInventory.objects.select_related('product', 'product__category').prefetch_related(
        'product__images'
    ).filter(user=user)


@router.get('/my', operation_id='listMyDigitalInventory', response={200: list[DigitalInventoryItemResponse], 401: ErrorResponse})
@paginate(PageNumberPagination, page_size=20)
def list_my_inventory(request):
    return _inventory_queryset(request.auth)


@router.post('/equip', operation_id='equipDigitalInventoryItem', response={200: DigitalInventoryItemResponse, 400: ErrorResponse, 401: ErrorResponse, 404: ErrorResponse})
def equip_inventory_item(request, payload: EquipDigitalItemRequest):
    item = get_object_or_404(_inventory_queryset(request.auth), pk=payload.inventory_id)
    
    if item.product.product_type != Product.TYPE_DIGITAL:
        raise HttpError(400, 'Only digital items can be equipped.')

    UserInventory.objects.filter(user=request.auth, is_equipped=True).update(is_equipped=False)
    
    item.is_equipped = True
    item.save(update_fields=['is_equipped', 'updated_at'])
    
    return DigitalInventoryItemResponse.model_validate(
        item,
        from_attributes=True,
    )


@router.post('/unequip', operation_id='unequipDigitalInventoryItem', response={200: DigitalInventoryItemResponse, 400: ErrorResponse, 401: ErrorResponse, 404: ErrorResponse})
def unequip_inventory_item(request, payload: EquipDigitalItemRequest):
    item = get_object_or_404(_inventory_queryset(request.auth), pk=payload.inventory_id)

    if not item.is_equipped:
        raise HttpError(400, 'Item is not equipped.')

    item.is_equipped = False
    item.save(update_fields=['is_equipped', 'updated_at'])

    return DigitalInventoryItemResponse.model_validate(
        item,
        from_attributes=True,
    )
