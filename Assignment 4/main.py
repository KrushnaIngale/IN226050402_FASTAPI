from fastapi import FastAPI, Query, Response, status, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI(title="My E-commerce Store API - Day 5 Cart System")

# ── Product Data ──────────────────────────────────────────────
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499,  "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook",       "price": 99,   "category": "Stationery",  "in_stock": True},
    {"id": 3, "name": "USB Hub",        "price": 799,  "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set",        "price": 49,   "category": "Stationery",  "in_stock": True},
]

# ── Cart & Orders storage ─────────────────────────────────────
cart   = []
orders = []

# ── Helper ────────────────────────────────────────────────────
def find_product(product_id: int):
    for p in products:
        if p["id"] == product_id:
            return p
    return None

def calculate_subtotal(product, quantity):
    return product["price"] * quantity


# ── Pydantic Models ───────────────────────────────────────────
class CheckoutRequest(BaseModel):
    customer_name:    str = Field(..., min_length=2, max_length=100)
    delivery_address: str = Field(..., min_length=10)


# ══════════════════════════════════════════════════════════════
# EXISTING PRODUCT ENDPOINTS
# ══════════════════════════════════════════════════════════════

@app.get('/')
def home():
    return {'message':'Welcome to our E-commerce API!'}

@app.get('/products')
def get_all_products():
    return {'products':products,'total':len(products)}

@app.get("/orders")
def get_all_orders():
    return {"orders": orders, "total_orders": len(orders)}


# ══════════════════════════════════════════════════════════════
# Q1 — POST /cart/add — Add item to cart
# ══════════════════════════════════════════════════════════════

@app.post("/cart/add")
def add_to_cart(
    product_id: int = Query(..., description="Product ID to add"),
    quantity:   int = Query(1, ge=1, le=50, description="Quantity"),
):
    # Find product
    product = find_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found")

    # Check if in stock
    if not product["in_stock"]:
        raise HTTPException(status_code=400, detail=f"{product['name']} is out of stock")

    # Check if already in cart → update quantity
    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"]  = calculate_subtotal(product, item["quantity"])
            return {"message": "Cart updated", "cart_item": item}

    # New item → add to cart
    cart_item = {
        "product_id":   product_id,
        "product_name": product["name"],
        "quantity":     quantity,
        "unit_price":   product["price"],
        "subtotal":     calculate_subtotal(product, quantity),
    }
    cart.append(cart_item)
    return {"message": "Added to cart", "cart_item": cart_item}


# ══════════════════════════════════════════════════════════════
# Q2 — GET /cart — View cart with grand total
# ══════════════════════════════════════════════════════════════

@app.get("/cart")
def view_cart():
    if not cart:
        return {"message": "Cart is empty"}
    grand_total = sum(item["subtotal"] for item in cart)
    return {
        "items":       cart,
        "item_count":  len(cart),
        "grand_total": grand_total,
    }


# ══════════════════════════════════════════════════════════════
# Q5 — DELETE /cart/{product_id} — Remove item from cart
# ══════════════════════════════════════════════════════════════

@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int, response: Response):
    for item in cart:
        if item["product_id"] == product_id:
            cart.remove(item)
            return {"message": f"{item['product_name']} removed from cart"}
    response.status_code = status.HTTP_404_NOT_FOUND
    return {"error": "Product not found in cart"}


# ══════════════════════════════════════════════════════════════
# Q5 — POST /cart/checkout — Checkout and place orders
# ══════════════════════════════════════════════════════════════

@app.post("/cart/checkout")
def checkout(data: CheckoutRequest):
    # Bonus — empty cart check
    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty — add items first")

    orders_placed = []
    grand_total   = 0

    for item in cart:
        order_id = len(orders) + 1
        order = {
            "order_id":        order_id,
            "customer_name":   data.customer_name,
            "delivery_address":data.delivery_address,
            "product":         item["product_name"],
            "quantity":        item["quantity"],
            "total_price":     item["subtotal"],
            "status":          "confirmed",
        }
        orders.append(order)
        orders_placed.append(order)
        grand_total += item["subtotal"]

    # Clear cart after checkout
    cart.clear()

    return {
        "message":      "Checkout successful",
        "orders_placed": orders_placed,
        "grand_total":  grand_total,
        "cart_status":  "Cart cleared",
    }
