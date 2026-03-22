from fastapi import FastAPI, Query
from typing import List
from pydantic import BaseModel,Field,EmailStr

app = FastAPI(title="FastAPI Day 6 Assignment")

# -----------------------------
# Sample Data
# -----------------------------

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics"},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery"},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics"},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery"},
]

orders = []

# -----------------------------

class OrderRequest(BaseModel):           
    customer_name:str=Field(...,min_length=2,max_length=100)
    product_id:int=Field(...,gt=0)
    quantity:int=Field(...,gt=0,le=100)
    delivery_address:str=Field(...,min_length=10)

def find_product(product_id:int):
    for p in products:
        if p['id']==product_id:
            return p
    return None

def calculate_total(product:dict,quantity:int)->int:
    return product['price']*quantity

# -----------------------------
# Home Route
# -----------------------------

@app.get("/")
def home():
    return {"message": "FastAPI Day 6 API Running"}

# -----------------------------
# Get All Products
# -----------------------------

@app.get("/products")
def get_products():
    return {"total": len(products), "products": products}

# -----------------------------
# Search Products
# -----------------------------

@app.get("/products/search")
def search_products(keyword: str = Query(...)):
    
    results = [
        p for p in products
        if keyword.lower() in p["name"].lower()
    ]

    if not results:
        return {"message": f"No products found for: {keyword}"}

    return {
        "keyword": keyword,
        "total_found": len(results),
        "products": results
    }

# -----------------------------
# Sort Products
# -----------------------------

@app.get("/products/sort")
def sort_products(
        sort_by: str = Query("price"),
        order: str = Query("asc")
):

    if sort_by not in ["price", "name"]:
        return {"error": "sort_by must be 'price' or 'name'"}

    sorted_products = sorted(
        products,
        key=lambda p: p[sort_by],
        reverse=(order == "desc")
    )

    return {
        "sort_by": sort_by,
        "order": order,
        "products": sorted_products
    }

# -----------------------------
# Pagination
# -----------------------------

@app.get("/products/page")
def paginate_products(
        page: int = Query(1, ge=1),
        limit: int = Query(2, ge=1)
):

    start = (page - 1) * limit
    paginated = products[start:start + limit]

    return {
        "page": page,
        "limit": limit,
        "total_products": len(products),
        "total_pages": -(-len(products) // limit),
        "products": paginated
    }

# -----------------------------
# Create Order
# -----------------------------

@app.post("/orders")
def create_order(order: dict):

    order_id = len(orders) + 1
    order["order_id"] = order_id

    orders.append(order)

    return {
        "message": "Order placed successfully",
        "order": order
    }

# -----------------------------
# Search Orders
# -----------------------------

@app.get("/orders/search")
def search_orders(customer_name: str = Query(...)):

    results = [
        o for o in orders
        if customer_name.lower() in o["customer_name"].lower()
    ]

    if not results:
        return {"message": f"No orders found for: {customer_name}"}

    return {
        "customer_name": customer_name,
        "total_found": len(results),
        "orders": results
    }

# -----------------------------
# Sort by Category then Price
# -----------------------------

@app.get("/products/sort-by-category")
def sort_by_category():

    result = sorted(
        products,
        key=lambda p: (p["category"], p["price"])
    )

    return {
        "total": len(result),
        "products": result
    }

# -----------------------------
# Search + Sort + Pagination
# -----------------------------

@app.get("/products/browse")
def browse_products(
        keyword: str = Query(None),
        sort_by: str = Query("price"),
        order: str = Query("asc"),
        page: int = Query(1, ge=1),
        limit: int = Query(4, ge=1, le=20)
):

    result = products

    # Search
    if keyword:
        result = [
            p for p in result
            if keyword.lower() in p["name"].lower()
        ]

    # Sort
    if sort_by in ["price", "name"]:
        result = sorted(
            result,
            key=lambda p: p[sort_by],
            reverse=(order == "desc")
        )

    # Pagination
    total = len(result)
    start = (page - 1) * limit
    paged = result[start:start + limit]

    return {
        "keyword": keyword,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "limit": limit,
        "total_found": total,
        "total_pages": -(-total // limit),
        "products": paged
    }

# -----------------------------
# Orders Pagination (Bonus)
# -----------------------------

@app.get("/orders/page")
def paginate_orders(
        page: int = Query(1, ge=1),
        limit: int = Query(3, ge=1, le=20)
):

    start = (page - 1) * limit

    return {
        "page": page,
        "limit": limit,
        "total_orders": len(orders),
        "total_pages": -(-len(orders) // limit),
        "orders": orders[start:start + limit]
    }

# -----------------------------
# Get Product by ID
# -----------------------------

@app.get("/products/{product_id}")
def get_product(product_id: int):

    for product in products:
        if product["id"] == product_id:
            return product

    return {"error": "Product not found"}


# post orders
@app.post('/orders')
def place_order(order_data:OrderRequest):
    global order_counter
    product=find_product(order_data.product_id)
    if not product:
        return {'error':'Product not found'}
    if not product['in_stock']:
        return {'error':f"{product['name']} is out of stock"}
    total=calculate_total(product,order_data.quantity)
    order={
        'order_id':order_counter,
        'customer_name':order_data.customer_name,
        'product':product['name'],
        'quantity':order_data.quantity,
        'delivery_address':order_data.delivery_address,
        'total_price':total,
        'status':'confirmed',
    }
    orders.append(order)
    order_counter+=1
    return {'message':'Order placed successfully','order':order}