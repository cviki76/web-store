import datetime

from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, get_jwt_identity
from configuration import Configuration
from models import database, Category, ProductCategory, Product, Order, ProductOrder
from sqlalchemy import and_, or_, func, DATETIME
import decorator
application = Flask(__name__)
application.config.from_object(Configuration)

jwt = JWTManager(application)

@application.route("/productStatistics",methods = ["GET"])
@decorator.roleCheck(role = "admin")
def productStatistics():
    jsonStatistics = []
    products = Product.query.all()

    for product in products:
        sold = 0
        waiting = 0
        productOrders = ProductOrder.query.filter(ProductOrder.productId == product.id).all()
        for productOrder in productOrders:
            sold += productOrder.requested
            waiting += productOrder.requested - productOrder.received

        if (sold > 0):
            jsonStat = {"name": product.name, "sold": sold, "waiting": waiting}
            jsonStatistics.append(jsonStat)

    return jsonify(statistics = jsonStatistics),200


@application.route("/categoryStatistics", methods=["GET"])
@decorator.roleCheck(role="admin")
def categoryStatistics():
    sortedCategories = []

    categoriesCount = {}
    categories = Category.query.all()
    for category in categories:
        categoriesCount[category.name] = 0
        for productForCategory in category.products:
            ordersForCategory = ProductOrder.query.filter(ProductOrder.productId == productForCategory.id)
            for orderForCategory in ordersForCategory:
                categoriesCount[category.name] += orderForCategory.requested

    categoriesSorted = sorted(categoriesCount.items(), key=lambda x: (-x[1], x[0]))

    categoriesSortedName = [c[0] for c in categoriesSorted]

    return jsonify(statistics = categoriesSortedName),200

@application.route("/",methods = ["GET"])
def index():
    return "Hello world"
if (__name__ == "__main__"):
    database.init_app(application)
    application.run(debug = True,host = "0.0.0.0",port = 5006)