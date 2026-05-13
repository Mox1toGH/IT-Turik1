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
- checks stock and points balance
- creates order in `pending`
- deducts points
- decreases stock
- creates points transaction linked to the order

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

### 6. Points Link Back to Order

`PointsTransaction` now has optional `order_id`.
Purchase and refund transactions created by shop always include this reference.
