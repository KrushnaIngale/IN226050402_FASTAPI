from fastapi import FastAPI , Query

app=FastAPI()
# @app.get("/")
# def home():
#     return {"message": "Hello World"}

# Temporary data – acting as our database for now
products = [
    {'id': 1, 'name': 'Wireless Mouse',      'price': 499,  'category': 'Electronics', 'in_stock': True},
    {'id': 2, 'name': 'Notebook',            'price': 99,   'category': 'Stationery',  'in_stock': True},
    {'id': 3, 'name': 'USB Hub',             'price': 799,  'category': 'Electronics', 'in_stock': False},
    {'id': 4, 'name': 'Pen Set',             'price': 49,   'category': 'Stationery',  'in_stock': True},
    {"id": 5, "name": "Laptop Stand",        "price": 1299, "category": "Electronics", "in_stock": True}, 
    {"id": 6, "name": "Mechanical Keyboard", "price": 2499, "category": "Electronics", "in_stock": True}, {"id": 7, "name": "Webcam",              "price": 1899, "category": "Electronics", "in_stock": False}
]

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
           max_price: int = Query(None,description='Maximum price of the product'),
           in_stock : bool= Query(None,description='True = In Stock, False = Out of Stock')
):
    result=products
    if category:
        result=[product for product in result if product['category'].lower()==category.lower()]
    if max_price is not None:
        result=[product for product in result if product['price']<=max_price]
    if in_stock is not None:
        result=[product for product in result if product['in_stock']==in_stock]
    return {'filtered_products':result,'total_count':len(result)}


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


# Endpoint 2 – Return one product by its ID
@app.get('/products/{product_id}')
def get_product(product_id: int):
    for product in products:
        if product['id'] == product_id:
            return {'product': product}

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

