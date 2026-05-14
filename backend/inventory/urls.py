from django.urls import path
from .views import (
    MyDigitalInventoryView,
    EquipDigitalInventoryItemView,
    UnequipDigitalInventoryItemView,
)

urlpatterns = [
    path('my/', MyDigitalInventoryView.as_view(), name='inventory-my'),
    path('equip/', EquipDigitalInventoryItemView.as_view(), name='inventory-equip'),
    path('unequip/', UnequipDigitalInventoryItemView.as_view(), name='inventory-unequip'),
]
