import datetime
import json

from flask import Flask, request, jsonify, Response
from flask_jwt_extended import JWTManager, get_jwt_identity
from configuration import Configuration
from models import database, Category, ProductCategory, Product, Order, ProductOrder
from sqlalchemy import and_, or_, func, DATETIME
import decorator
application = Flask(__name__)
application.config.from_object(Configuration)

jwt = JWTManager(application)

@application.route("/search",methods = ["GET"])
@decorator.roleCheck(role = "buyer")
def search():
    productName = request.args.get("name")
    categoryName = request.args.get("category")

    count1 = func.count(Category.name)
    count2 = func.count(Product.name)

    categories = None
    products = None

    if (productName == None and categoryName == None):
        products = Product.query.join(ProductCategory).join(Category).all()
        categories = Category.query.join(ProductCategory).join(Product).all()
    elif(productName == None and categoryName is not None):
        products = Product.query.join(ProductCategory).join(Category).filter(Category.name.like(f"%{categoryName}%")).all()
        categories = Category.query.join(ProductCategory).join(Product).filter(Category.name.like(f"%{categoryName}%")).all()
    elif (productName is not None and categoryName == None):
        products = Product.query.join(ProductCategory).join(Category).filter(Product.name.like(f"%{productName}%")).all()
        categories = Category.query.join(ProductCategory).join(Product).filter(Product.name.like(f"%{productName}%")).all()
    elif (productName is not None and categoryName is not None):
        products = Product.query.join(ProductCategory).join(Category).filter(
        and_(
            Product.name.like(f"%{productName}%"),
            Category.name.like(f"%{categoryName}%")
            )
        ).all()
        categories = Category.query.join(ProductCategory).join(Product).filter(
        and_(
            Product.name.like(f"%{productName}%"),
            Category.name.like(f"%{categoryName}%")
            )
        ).all()


    jsonProducts = [{"categories":[category.name for category in product.categories],"id":product.id,"name" : product.name,"price":product.price,"quantity":product.quantity}  for product in products]
    return jsonify(categories=[category.name for category in categories], products=jsonProducts), 200

@application.route("/order",methods = ["POST"])
@decorator.roleCheck(role = "buyer")
def order():
    status  = "COMPLETE"
    price = 0
    requests = request.json.get("requests", "")

    requestsEmpty = len(requests) == 0

    if (requestsEmpty):
        return jsonify(message="Field requests is missing."), 400

    i = 0
    for req in requests:
        if 'id' not in req:
            return jsonify(message=f"Product id is missing for request number {i}."), 400
        if 'quantity' not in req:
            return jsonify(message=f"Product quantity is missing for request number {i}."), 400

        try:
            id = int(req["id"])
            if id <= 0:
                raise ValueError
        except ValueError:
            return Response(json.dumps({"message": f"Invalid product id for request number {i}."}), status=400)

        try:
            quantity = int(req['quantity'])
            if quantity <= 0:
                raise ValueError
        except ValueError:
            return Response(json.dumps({"message": f"Invalid product quantity for request number {i}."}), status=400)


        product = Product.query.filter(Product.id == id).first();

        if (not product):
            return jsonify(message=f"Invalid product for request number {i}."), 400

        if (product.quantity < quantity):
            status = "PENDING"

        price += product.price * product.quantity
        i+=1

    order = Order(price = price, status = status, timestamp=datetime.datetime.now().isoformat(),email = get_jwt_identity())
    database.session.add(order)
    database.session.commit()

    for req in requests:
        id = req["id"]
        quantity = req["quantity"]
        product = Product.query.filter(Product.id == id).first();
        if (product.quantity < quantity):
            rec = product.quantity
        else:
            rec = quantity

        productorder = ProductOrder(productId = id,orderId = order.id,requested = quantity,received = rec,price = product.price)
        database.session.add(productorder)
        database.session.commit()

        product.quantity -= rec
        database.session.commit()

    return jsonify(id = order.id),200

def getReceivedForProduct(idProduct,idOrder):
    productOrder = ProductOrder.query.filter(and_(
        ProductOrder.orderId == idOrder,
        ProductOrder.productId == idProduct
    )).first()

    return productOrder.received
def getRequestedForProduct(idProduct,idOrder):
    productOrder = ProductOrder.query.filter(and_(
        ProductOrder.orderId == idOrder,
        ProductOrder.productId == idProduct
    )).first()

    return productOrder.requested
def getRealPrice(idProduct,idOrder):
    productOrder = ProductOrder.query.filter(and_(
        ProductOrder.orderId == idOrder,
        ProductOrder.productId == idProduct
    )).first()

    return productOrder.price

@application.route("/status",methods = ["GET"])
@decorator.roleCheck(role = "buyer")
def status():
    ordersForUser = Order.query.filter(Order.email == get_jwt_identity()).all()
    ordersForPrint = []
    for order in ordersForUser:
        orderAttributes = {}
        orderProducts = []
        orderPrice = 0
        for product in order.products:
            categoresNames = [category.name for category in product.categories]
            productAttributes = {
                "categories" : categoresNames,
                "name":product.name,
                "price" : float(getRealPrice(product.id,order.id)),
                "received": getReceivedForProduct(product.id,order.id),
                "requested": getRequestedForProduct(product.id,order.id)
            }
            orderProducts.append(productAttributes)
            orderPrice += float(getRealPrice(product.id,order.id)) * getRequestedForProduct(product.id,order.id)
        orderAttributes["products"] = orderProducts
        orderAttributes["price"]= orderPrice
        orderAttributes["status"] = order.status
        orderAttributes["timestamp"] = order.timestamp
        ordersForPrint.append(orderAttributes)

    return jsonify(orders = ordersForPrint),200

@application.route("/",methods = ["GET"])
def index():
    return "Hello world"
if (__name__ == "__main__"):
    database.init_app(application)
    application.run(debug = True,host = "0.0.0.0",port = 5001)