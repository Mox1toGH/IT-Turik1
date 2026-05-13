# Shop API Cheat Sheet

---

### 1. Endpoints

| Action | Method | Path | Access |
| :--- | :--- | :--- | :--- |
| List products | GET | `/api/shop/products/` | Auth |
| Product detail | GET | `/api/shop/products/{id}/` | Auth |
| Purchase product | POST | `/api/shop/purchase/` | Auth |
| My order history | GET | `/api/shop/orders/my/` | Auth |
| Cancel my order | POST | `/api/shop/orders/my/{order_id}/cancel/` | Auth |
| Admin category list/create | GET / POST | `/api/shop/admin/categories/` | Admin |
| Admin category detail/update/delete | GET / PUT / PATCH / DELETE | `/api/shop/admin/categories/{id}/` | Admin |
| Admin product list/create | GET / POST | `/api/shop/admin/products/` | Admin |
| Admin product detail/update/delete | GET / PUT / PATCH / DELETE | `/api/shop/admin/products/{id}/` | Admin |
| Admin orders list | GET | `/api/shop/admin/orders/` | Admin |
| Admin change order status | PATCH | `/api/shop/admin/orders/{order_id}/status/` | Admin |
| Admin cancel order | POST | `/api/shop/admin/orders/{order_id}/cancel/` | Admin |
| Admin avatar frames list/create | GET / POST | `/api/shop/admin/avatar-frames/` | Admin |
| Admin avatar frame detail/edit/delete | GET / PATCH / DELETE | `/api/shop/admin/avatar-frames/{id}/` | Admin |
| **Avatar frames list (active)** | GET | `/api/shop/avatar-frames/` | Auth |

---

### 2. Products List

**GET `/api/shop/products/`**

**Query params**
- `page`, `page_size` (max `100`)
- `search` (by name)
- `category` (category id)
- `product_type` (`physical` or `digital`)
- `ordering` (`name`, `-name`, `price`, `-price`)

Notes:
- only active products are listed.
- products with stock `0` are returned with `is_available: false` and sorted to the end.

---

### 3. Purchase

**POST `/api/shop/purchase/`**

```json
{
  "product_id": 12,
  "quantity": 2
}
```

Server atomically:
- locks product and user points balance (`select_for_update`)
- checks ownership (for digital) or stock (for physical) and points balance
- for **physical** products:
    - creates order in `pending`
    - decreases stock
- for **digital** products:
    - adds item to user inventory
- deducts points
- creates points transaction (linked to order if physical)

---

### 4. Cancel Order

Allowed statuses for cancellation:
- `pending`
- `confirmed`

On cancellation (atomic):
- order status -> `cancelled`
- stock is returned
- points are refunded
- refund points transaction is created and linked to the order

---

### 5. Admin Orders

**GET `/api/shop/admin/orders/`** supports:
- `page`, `page_size`
- `status`
- `user` (user id)

Each order includes `user_profile_url` (`/api/accounts/users/{id}/`).

`PATCH /status/` can set any non-cancel status.
Use `/cancel/` endpoint for cancellation so refund+stock rollback logic is executed.

---

### 6. Admin Avatar Frames

**GET / POST `/api/shop/admin/avatar-frames/`**
- `GET`: returns all frames (active and inactive).
- `POST`: creates a new frame. Requires `name` and `svg_file`.

**GET / PATCH / DELETE `/api/shop/admin/avatar-frames/{id}/`**
- Standard CRUD for avatar frames.

---

### 7. Creating Products with Avatar Frames

When creating a digital product (`product_type="digital"`), you can now provide an `avatar_frame_file` directly in the **multipart/form-data** request.

**POST `/api/shop/admin/products/`**
- If `avatar_frame_file` is provided:
    - System checks if an `AvatarFrame` with the same `name` as the product exists.
    - If not, it creates a new `AvatarFrame` and links it to the product.
    - If it exists, it links the existing one (and updates its SVG if it's an `update` request).
- This allows creating a product and its frame in a single step.

---

### 8. Points Link Back to Order

`PointsTransaction` now has optional `order_id`.
Purchase and refund transactions created by shop always include this reference.

---


### 9. Avatar Frames (Public)

**GET `/api/shop/avatar-frames/`**
- Returns a list of active avatar frames.
- Supports `search` query param.
- Used to preview available frames before purchase.


