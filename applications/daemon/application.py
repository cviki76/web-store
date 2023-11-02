from flask import Flask;

from models import database, Product, Category, ProductCategory, ProductOrder, Order
from configuration import Configuration;
from redis import Redis
import json

from sqlalchemy import and_


application = Flask(__name__)
application.config.from_object(Configuration)


def checkIfOrderComplete(idOrder):

    productOrders = ProductOrder.query.filter(ProductOrder.orderId == idOrder).all()
    sumReceived = 0
    sumRequested = 0

    for productOrder in productOrders:
        sumReceived += productOrder.received
        sumRequested += productOrder.requested

    if (sumRequested == sumReceived):
        return 1
    else:
        return 0

if (__name__ == "__main__"):
    database.init_app(application)

    with Redis(host=Configuration.REDIS_HOST) as redis:
        while(True):
            productRedisJSON = json.loads(redis.blpop(Configuration.REDIS_LIST)[1].decode())
            with application.app_context() as context:
                product = Product.query.filter(Product.name == productRedisJSON.get("name")).first()
                categoriesNames = json.loads(productRedisJSON.get("categories"))
                if not product:
                        productAdd = Product(name=productRedisJSON.get("name"), price=productRedisJSON.get("price"),
                                         quantity=productRedisJSON.get("quantity"))
                        database.session.add(productAdd)
                        database.session.commit()
                        for categoryName in categoriesNames:
                            category = Category.query.filter(Category.name == categoryName).first()
                            if category:
                                productCategory = ProductCategory(productId = productAdd.id,categoryId = category.id)
                                database.session.add(productCategory)
                                database.session.commit()
                            else:
                                categoryAdd = Category(name = categoryName)
                                database.session.add(categoryAdd)
                                database.session.commit()
                                productCategory = ProductCategory(productId=productAdd.id, categoryId=categoryAdd.id)
                                database.session.add(productCategory)
                                database.session.commit()
                else:
                    categoriesNamesNew = []
                    for category in product.categories:
                        categoriesNamesNew.append(category.name)

                    flag = True

                    for categoryName in categoriesNames:
                        if categoryName not in categoriesNamesNew:
                            flag = False

                    if flag:
                        currentQuantity = product.quantity
                        currentPrice = product.price

                        deiliveryPrice = productRedisJSON.get("price")
                        deliveryQuantity = productRedisJSON.get("quantity")

                        newPrice = (currentQuantity * currentPrice + deliveryQuantity * deiliveryPrice) / (
                                    currentQuantity + deliveryQuantity)

                        product.price = newPrice
                        database.session.commit()

                        ordersToComplete = Order.query.join(ProductOrder).join(Product).filter(
                            and_(
                                Order.status == "PENDING",
                                Product.id == product.id,
                                ProductOrder.requested - ProductOrder.received > 0
                                )
                        ).order_by(Order.timestamp)

                        for order in ordersToComplete:
                            productOrder = ProductOrder.query.filter(
                                ProductOrder.productId == product.id,
                                ProductOrder.orderId == order.id
                            ).first()

                            requested = productOrder.requested
                            received = productOrder.received

                            if (requested - received < deliveryQuantity):
                                deliveryQuantity -= (requested - received)
                                received = requested
                            else:
                                received = received + deliveryQuantity
                                deliveryQuantity = 0

                            productOrder.received = received
                            database.session.commit()


                            if (checkIfOrderComplete(order.id) == 1):
                                order.status = "COMPLETE"
                                database.session.commit()

                            if deliveryQuantity == 0:
                                break;

                        product.quantity += deliveryQuantity
                        database.session.commit()
