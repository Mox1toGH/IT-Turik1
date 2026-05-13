from django.urls import path

from .views import (
    AdminCategoryDetailView,
    AdminCategoryListCreateView,
    AdminOrderCancelView,
    AdminOrderListView,
    AdminOrderStatusUpdateView,
    AdminProductDetailView,
    AdminProductListCreateView,
    AvatarFrameListView,
    EquipDigitalInventoryItemView,
    MyDigitalInventoryView,
    MyOrderCancelView,
    MyOrderHistoryView,
    ProductDetailView,
    ProductListView,
    PurchaseView,
    UnequipDigitalInventoryItemView,
)

urlpatterns = [
    path('products/', ProductListView.as_view(), name='shop-products-list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='shop-products-detail'),
    path('avatar-frames/', AvatarFrameListView.as_view(), name='shop-avatar-frames-list'),
    path('purchase/', PurchaseView.as_view(), name='shop-purchase'),
    path('orders/my/', MyOrderHistoryView.as_view(), name='shop-my-orders'),
    path('orders/my/<int:order_id>/cancel/', MyOrderCancelView.as_view(), name='shop-my-order-cancel'),
    path('inventory/my/', MyDigitalInventoryView.as_view(), name='shop-my-inventory'),
    path('inventory/equip/', EquipDigitalInventoryItemView.as_view(), name='shop-inventory-equip'),
    path('inventory/unequip/', UnequipDigitalInventoryItemView.as_view(), name='shop-inventory-unequip'),

    path('admin/categories/', AdminCategoryListCreateView.as_view(), name='shop-admin-categories-list-create'),
    path('admin/categories/<int:pk>/', AdminCategoryDetailView.as_view(), name='shop-admin-categories-detail'),
    path('admin/products/', AdminProductListCreateView.as_view(), name='shop-admin-products-list-create'),
    path('admin/products/<int:pk>/', AdminProductDetailView.as_view(), name='shop-admin-products-detail'),
    path('admin/orders/', AdminOrderListView.as_view(), name='shop-admin-orders-list'),
    path('admin/orders/<int:order_id>/status/', AdminOrderStatusUpdateView.as_view(), name='shop-admin-orders-status'),
    path('admin/orders/<int:order_id>/cancel/', AdminOrderCancelView.as_view(), name='shop-admin-orders-cancel'),
]
