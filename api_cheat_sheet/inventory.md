# Inventory API Cheat Sheet

---

### 1. Endpoints

| Action | Method | Path | Access |
| :--- | :--- | :--- | :--- |
| **My inventory** | GET | `/api/inventory/my/` | Auth |
| **Equip item** | POST | `/api/inventory/equip/` | Auth |
| **Unequip item** | POST | `/api/inventory/unequip/` | Auth |

---

### 2. My Inventory

**GET `/api/inventory/my/`**

Returns all digital products owned by the authenticated user.

**Response example**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 15,
      "product": {
        "id": 10,
        "name": "Neon Frame",
        "description": "Premium neon avatar frame",
        "price": 500,
        "product_type": "digital",
        "digital_asset_url": "/media/avatar-frames/neon.svg"
      },
      "is_equipped": true,
      "acquired_at": "2026-05-13T20:00:00Z",
      "updated_at": "2026-05-13T21:00:00Z"
    }
  ]
}
```

---

### 3. Equipping Items

**POST `/api/inventory/equip/`**

Equips a digital item. Only one item can be equipped at a time. Equipping a new item automatically unequips any previously equipped item.

**Request body**
```json
{
  "inventory_id": 15
}
```

**Notes**
- Only digital items can be equipped.
- Returns the updated inventory item object.

**POST `/api/inventory/unequip/`**

Unequips the specified item.

**Request body**
```json
{
  "inventory_id": 15
}
```
