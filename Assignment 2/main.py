from fastapi import FastAPI , Query
from pydantic import BaseModel, Field
from typing import Optional
from typing import List  

app=FastAPI()
# @app.get("/")
# def home():
#     return {"message": "Hello World"}

# ----Pydantic model-------------------
class OrderRequest(BaseModel):
    customer_name:      str=Field(...,min_length=2, max_length=100)
    product_id:         int=Field(...,gt=0)
    quantity:           int=Field(...,gt=0, le=100)
    delivery_address:   str=Field(...,min_length=5, max_length=10)

class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity:   int = Field(..., gt=0, le=50)

class BulkOrder(BaseModel):
    company_name:  str              = Field(..., min_length=2)
    contact_email: str              = Field(..., min_length=5)
    items:         List[OrderItem]  = Field(..., min_items=1)



# Temporary data – acting as our database for now
products = [
    {'id': 1, 'name': 'Wireless Mouse',      'price': 499,  'category': 'Electronics', 'in_stock': True},
    {'id': 2, 'name': 'Notebook',            'price': 99,   'category': 'Stationery',  'in_stock': True},
    {'id': 3, 'name': 'USB Hub',             'price': 799,  'category': 'Electronics', 'in_stock': False},
    {'id': 4, 'name': 'Pen Set',             'price': 49,   'category': 'Stationery',  'in_stock': True},
    {"id": 5, "name": "Laptop Stand",        "price": 1299, "category": "Electronics", "in_stock": True}, 
    {"id": 6, "name": "Mechanical Keyboard", "price": 2499, "category": "Electronics", "in_stock": True}, {"id": 7, "name": "Webcam",              "price": 1899, "category": "Electronics", "in_stock": False}
]
orders = []
order_counter = 1
# Add this list near orders = []:
feedback = []

# ----Helper Function------------------
def find_product(product_id: int):
    for p in products:
        if p['id']==product_id:
            return p
    return None

def calculate_total(product: dict, quantity: int) -> int:
    return product['price'] * quantity

def filter_products_logic(category=None, min_price=None,max_price=None, in_stock=None):
    result = products
    if category is not None:
        result=[p for p in result if p['category'].lower()==category.lower()]
    if min_price is not None:
        result=[p for p in result if p['price']>=min_price]
    if max_price is not None:
        result=[p for p in result if p['price']<=max_price]
    if in_stock is not None:
        result=[p for p in result if p['in_stock']==in_stock]
    return result



# Endpoint 0 – Home
@app.get('/')
def home():
    return {'message': 'Welcome to our E-commerce API'}


# Endpoint 1 – Return all products
@app.get('/products')
def get_all_products():
    return {'products': products, 'total': len(products)}

# add products filter before accessinng specific product
@app.get('/products/filter')
def filter(category : str = Query(None,description='Stationery or Electronics'),
           min_price: int =Query(None,description='Minimum price of the product'),
           max_price: int = Query(None,description='Maximum price of the product'),
           in_stock : bool= Query(None,description='True = In Stock, False = Out of Stock')
):
    result=products
    if category:
        result=[product for product in result if product['category'].lower()==category.lower()]
    if min_price is not None:
        result=[product for product in result if product['price']>=min_price]
    if max_price is not None:
        result=[product for product in result if product['price']<=max_price]
    if in_stock is not None:
        result=[product for product in result if product['in_stock']==in_stock]
    return {'filtered_products':result,'total_count':len(result)}

@app.get('/products/compare')
def compare_products(product_id_1: int=Query(...), product_id_2: int=Query(...)):
    p1=find_product(product_id_1)
    p2=find_product(product_id_2)
    if not p1: return {'error': f'Product{product_id_1} not found'}
    if not p2: return {'error': f'Product{product_id_2} not found'}
    cheaper = p1 if p1['price'] < p2['price'] else p2
    # expensive = p1 if p1['price'] > p2['price'] else p2
    return {'product_1':p1, 'product_2':p2, 'better_value': cheaper, 'price_diff':abs(p1['price']-p2['price'])}


#  End point 4 - instock 
@app.get('/products/instock')
def get_products_in_stock():
    result=[product for product in products if product['in_stock']==True]
    return {'in_stock_products':result,'total':len(result)}


#  End Point 7 - deals cheapest and expensive
@app.get('/products/deals')
def get_deals():
    cheapest = min(products, key=lambda p: p["price"]) 
    expensive = max(products, key=lambda p: p["price"]) 
    return { "best_deal": cheapest, "premium_pick": expensive, }


@app.get('/products/summary')
def product_summary():
    total_products = len(products)
    in_stock_count = len([p for p in products if p['in_stock']])
    out_of_stock_count = total_products - in_stock_count
    expenive=max(products, key=lambda p: p['price'])
    cheapest=min(products, key=lambda p: p['price'])
    categories=list(set([p['category'] for p in products]))
    return{
        "total_products": total_products,
        "in_stock_count": in_stock_count,
        "out_of_stock_count": out_of_stock_count,
        "expenive": {"name":expenive['name'], "price":expenive['price']},
        "cheapest": {"name":cheapest['name'], "price":cheapest['price']},
        "categories": categories
    }



# Endpoint 2 – Return one product by its ID
@app.get('/products/{product_id}')
def get_product(product_id: int):
    for product in products:
        if product['id'] == product_id:
            return {'product': product}

    return {'error': 'Product not found'}


# day 3 new end point
@app.get('/products/{product_id}/price')
def get_product_price(product_id: int):
    for product in products:
        if product['id'] == product_id:
            return{'name': product['name'], 'price': product['price']}
    return {'error': 'Product not found'}


# End point 3 -  Add a Category Filter Endpoint
@app.get('/products/category/{category}')
def get_products_by_category(category: str):
    result = [product for product in products if product['category'].lower() == category.lower()]
    if not result:
        return {'error': 'Product not found'}
    return {'products': result, 'total': len(result)}



#  ENd Point 5 - store summary
@app.get('/store/summary')
def get_summary():
    total_products=len(products)
    in_stock_count=len([p for p in products if p['in_stock']==True])
    # out_stock_count=len(p for p in products if p['in_stock']==False)
    out_stock_count=total_products-in_stock_count

    categories=list(set([p["category"] for p in products]))

    return {'Store name:':"My E-commerce Store", 'total_products':total_products, 'in_stock_count':in_stock_count,'out_stock_count':out_stock_count,'categories':categories}



#  End-Point 6 = search
@app.get("/products/search/{keyword}") 
def search_products(keyword: str): 
    results = [p for p in products if keyword.lower() in p["name"].lower()] 
    if not results: 
        return {"message": "No products matched your search"} 
    return {"keyword": keyword, "results": results, "total_matches": len(results)}

# New GET by order ID:
@app.get("/orders/{order_id}")
def get_order(order_id: int):
    for order in orders:
        if order.get("id") == order_id:
            return {"order": order}
    return {"error": "Order not found"}


# PATCH to confirm:
@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id: int):
    for order in orders:
        if order["id"] == order_id:
            order["status"] = "confirmed"
            return order
        
    return {"error": "Order not found"}


class Order(BaseModel):
    product_id: int
    quantity: int
    
@app.post('/orders')
def create_order(order: Order):

    order_id = len(orders) + 1

    new_order = {
        "id": order_id,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "status": "pending"
    }

    orders.append(new_order)

    return new_order
# def place_order(order_data: OrderRequest):
#     global order_counter
#     product= next((p for p in products if p['id']==order_data.product_id), None)
#     if product is None:
#         return {'error': 'Product not found'}
#     if not product['in_stock']:
#         return {'error': f"{product['name']} iss out of stock"}
#     total_price = product['price'] * order_data.quantity
#     order = {
#         'order_id': order_counter,
#         'customer_name': order_data.customer_name,
#         'product': product['name'],
#         'quantity': order_data.quantity,
#         'delivery_address': order_data.delivery_address,
#         'total_price': total_price
#     }
#     orders.append(order)
#     order_counter += 1
#     return {'message': 'Order placed successfully', 'order':order}


# Add this Pydantic model (below OrderRequest):
class CustomerFeedback(BaseModel):
    customer_name: str            = Field(..., min_length=2, max_length=100)
    product_id:   int            = Field(..., gt=0)
    rating:       int            = Field(..., ge=1, le=5)
    comment:      Optional[str]  = Field(None, max_length=300)


# Add this endpoint at the bottom:
@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):
    feedback.append(data.dict())
    return {
        "message":        "Feedback submitted successfully",
        "feedback":       data.dict(),
        "total_feedback": len(feedback),
    }


@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):
    confirmed, failed, grand_total = [], [], 0
    for item in order.items:
        product = next((p for p in products if p["id"] == item.product_id), None)
        if not product:
            failed.append({"product_id": item.product_id, "reason": "Product not found"})
        elif not product["in_stock"]:
            failed.append({"product_id": item.product_id, "reason": f"{product['name']} is out of stock"})
        else:
            subtotal = product["price"] * item.quantity
            grand_total += subtotal
            confirmed.append({"product": product["name"], "qty": item.quantity, "subtotal": subtotal})
    return {"company": order.company_name, "confirmed": confirmed,
            "failed": failed, "grand_total": grand_total}