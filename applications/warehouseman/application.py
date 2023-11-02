import json
import io
import csv

from flask import Flask, request, jsonify, Response
from flask_jwt_extended import JWTManager
from redis import Redis

from configuration import Configuration
from models import database, Category, ProductCategory, Product, Order, ProductOrder
from sqlalchemy import and_, or_, func, DATETIME
import decorator
application = Flask(__name__)
application.config.from_object(Configuration)

jwt = JWTManager(application)


@application.route("/update", methods=["POST"])
@decorator.roleCheck(role = "warehouseman")
def update():
    if "file" not in request.files:
        return Response(json.dumps({"message": "Field file is missing."}), status=400)

    file = request.files['file'].stream.read()

    stream = io.StringIO(file.decode("UTF8"))
    reader = csv.reader(stream)

    products = []

    for count, row in enumerate(reader):
        if len(row) != 4:
            return Response(json.dumps({"message": f"Incorrect number of values on line {count}."}), status=400)

        name = str(row[1])

        try:
            quantity = int(row[2])
            if quantity < 0:
                raise ValueError()
        except ValueError:
            return Response(json.dumps({"message": f"Incorrect quantity on line {count}."}), status=400)

        try:
            price = float(row[3])
            if price < 0:
                raise ValueError()
        except ValueError:
            return Response(json.dumps({"message": f"Incorrect price on line {count}."}), status=400)

        categories = row[0].split('|')

        products.append(json.dumps({"categories":json.dumps(categories),"name":name, "quantity":quantity,"price":price}))

    for product in products:
        with Redis (host = Configuration.REDIS_HOST) as redis:
            redis.rpush(Configuration.REDIS_LIST, product)

    return Response(status = 200)

@application.route("/",methods = ["GET"])
def index():
    return "Hello world"
if (__name__ == "__main__"):
    database.init_app(application)
    application.run(debug = True,host = "0.0.0.0",port = 5003)