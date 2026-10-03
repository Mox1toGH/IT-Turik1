from datetime import datetime

from ninja import Schema

class ProductImageResponse(Schema):
    id: int
    image: str


class CategoryResponse(Schema):
    id: int
    name: str


class ProductResponse(Schema):
    id: int
    name: str
    description: str
    price: int
    stock_quantity: int
    category: CategoryResponse
    product_type: str
    digital_asset_url: str
    is_active: bool
    images: list[ProductImageResponse]


class DigitalInventoryItemResponse(Schema):
    id: int
    product: ProductResponse
    is_equipped: bool
    acquired_at: datetime
    updated_at: datetime


class EquipDigitalItemRequest(Schema):
    inventory_id: int
