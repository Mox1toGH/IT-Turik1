/**
 * Compatibility shim — re-exports from Orval-generated inventory API
 * with the legacy hook aliases used by existing Vue components.
 */
export {
  useListMyDigitalInventory as useMyInventory,
  useEquipDigitalInventoryItem as useEquipInventoryItem,
  useUnequipDigitalInventoryItem as useUnequipInventoryItem,
} from '@/api/inventory/inventory'
