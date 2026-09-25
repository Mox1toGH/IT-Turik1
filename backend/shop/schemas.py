from datetime import datetime
from typing import Literal

from ninja import Field, Schema

from backend.media import absolute_media_url

class CategoryResponse(Schema):
    id: int
    name: str


class CategoryRequest(Schema):
    name: str = Field(..., max_length=120)


class ProductImageResponse(Schema):
    id: int
    image: str
    created_at: datetime

    @staticmethod
    def resolve_image(obj, context):
        return absolute_media_url(obj.image, context)


class AvatarFrameResponse(Schema):
    id: int
    name: str
    svg_file: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def resolve_svg_file(obj, context):
        return absolute_media_url(obj.svg_file, context)


class AvatarFrameRequest(Schema):
    name: str
    svg_file: str
    is_active: bool = True


class ProductResponse(Schema):
    id: int
    name: str
    description: str
    price: int
    stock_quantity: int
    category: CategoryResponse
    product_type: str
    avatar_frame: AvatarFrameResponse | None = None
    digital_asset_url: str
    images: list[ProductImageResponse]
    is_active: bool
    is_available: bool
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def resolve_digital_asset_url(obj, context):
        return absolute_media_url(obj.effective_digital_asset_url, context) or ''

    @staticmethod
    def resolve_is_available(obj):
        return obj.is_active if obj.product_type == 'digital' else obj.is_active and obj.stock_quantity > 0


class ProductRequest(Schema):
    name: str
    description: str = ''
    price: int = Field(..., ge=0)
    stock_quantity: int = Field(0, ge=0)
    category_id: int
    product_type: Literal['physical', 'digital'] = 'physical'
    avatar_frame_id: int | None = None
    digital_asset_url: str = ''
    is_active: bool = True


class PurchaseRequest(Schema):
    product_id: int = Field(..., ge=1)
    quantity: int = Field(..., ge=1)


class UserShortResponse(Schema):
    id: int
    username: str
    email: str
    full_name: str


class OrderResponse(Schema):
    id: int
    user: UserShortResponse
    user_profile_url: str
    product: ProductResponse
    quantity: int
    total_cost: int
    status: str
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def resolve_user_profile_url(obj, context):
        request = (context or {}).get('request')
        path = f'/api/accounts/users/{obj.user_id}/'
        return request.build_absolute_uri(path) if request else path


class PurchaseOrderResponse(OrderResponse):
    result_type: Literal['order'] = 'order'


class PurchaseDigitalResponse(Schema):
    result_type: Literal['digital'] = 'digital'
    message: str


class OrderStatusRequest(Schema):
    status: Literal['pending', 'confirmed', 'shipped', 'completed']
