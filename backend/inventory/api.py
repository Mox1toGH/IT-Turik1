import logging

from django.shortcuts import get_object_or_404

from ninja import Router
from ninja.pagination import PageNumberPagination, paginate

from backend.auth import JWTAuth
from shop.models import Product

from .models import UserInventory

from backend.schemas import ErrorResponse
from backend.errors import raise_api_error
from http import HTTPStatus
from .schemas import DigitalInventoryItemResponse, EquipDigitalItemRequest

logger = logging.getLogger(__name__)

router = Router(tags=['inventory'], auth=JWTAuth())

def _inventory_queryset(user):
    return UserInventory.objects.select_related('product', 'product__category').prefetch_related(
        'product__images'
    ).filter(user=user)


@router.get('/my', operation_id='listMyDigitalInventory', url_name="inventory-my", response={200: list[DigitalInventoryItemResponse], 401: ErrorResponse})
@paginate(PageNumberPagination, page_size=20)
def list_my_inventory(request):
    logger.debug('Listing inventory', extra={
        'user_id': request.auth.id
    })
    return _inventory_queryset(request.auth)


@router.post('/equip', operation_id='equipDigitalInventoryItem', url_name="inventory-equip", response={200: DigitalInventoryItemResponse, 400: ErrorResponse, 401: ErrorResponse, 404: ErrorResponse})
def equip_inventory_item(request, payload: EquipDigitalItemRequest):
    logger.info('Equip requested', extra={
        'user_id': request.auth.id,
        'inventory_id': payload.inventory_id
    })
    item = get_object_or_404(_inventory_queryset(request.auth), pk=payload.inventory_id)

    if item.product.product_type != Product.TYPE_DIGITAL:
        logger.warning(
            'Equip rejected, non-digital item',
            extra={
                'user_id': request.auth.id,
                'inventory_id': item.id,
                'product_id': item.product_id,
                'product_type': item.product.product_type
            }
        )
        raise_api_error(HTTPStatus.BAD_REQUEST, 'Only digital items can be equipped.')

    unequipped = UserInventory.objects.filter(user=request.auth, is_equipped=True).update(is_equipped=False)
    if unequipped:
        logger.debug('Unequipped previously equipped item(s)', extra={
            'items': unequipped,
            'user_id': request.auth.id
        })

    item.is_equipped = True
    item.save(update_fields=['is_equipped', 'updated_at'])
    logger.info(
        'Item equipped',
         extra={
            'user_id': request.auth.id,
            'inventory_id': item.id,
            'product_id': item.product_id
        }
    )

    return DigitalInventoryItemResponse.model_validate(
        item,
        from_attributes=True,
    )


@router.post('/unequip', operation_id='unequipDigitalInventoryItem', url_name="inventory-unequip", response={200: DigitalInventoryItemResponse, 400: ErrorResponse, 401: ErrorResponse, 404: ErrorResponse})
def unequip_inventory_item(request, payload: EquipDigitalItemRequest):
    logger.info('Unequip requested', extra={
        'user_id': request.auth.id,
        'inventory_id': payload.inventory_id,
    })
    item = get_object_or_404(_inventory_queryset(request.auth), pk=payload.inventory_id)

    if item.product.product_type != Product.TYPE_DIGITAL:
        logger.warning(
            'Unequip rejected, non-digital item',
            extra={
                'user_id': request.auth.id,
                'inventory_id': payload.inventory_id,
                'product_id': item.product_id,
                'product_type': item.product.product_type
            }
        )
        raise_api_error(HTTPStatus.BAD_REQUEST, 'Only digital items can be unequipped.')

    if not item.is_equipped:
        logger.warning(
            'Unequip rejected, item not equipped',
            extra={
                'user_id': request.auth.id,
                'inventory_id': payload.inventory_id,
            }
        )
        raise_api_error(HTTPStatus.BAD_REQUEST, 'Item is not equipped.')

    item.is_equipped = False
    item.save(update_fields=['is_equipped', 'updated_at'])
    logger.info(
        'Item unequipped',
        extra={
            'user_id': request.auth.id,
            'inventory_id': payload.inventory_id,
            'product_id': item.product_id
        }
    )

    return DigitalInventoryItemResponse.model_validate(
        item,
        from_attributes=True,
    )