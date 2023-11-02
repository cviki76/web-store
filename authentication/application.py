from flask import Flask, request, jsonify, Response;
import decorator
from models import database, User, UserRole
from configuration import Configuration
from email.utils import parseaddr
import re
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt_identity, \
    get_jwt
from sqlalchemy import and_

application = Flask(__name__)
application.config.from_object(Configuration)

def checkEmail(email):
    pattern = "[^@]+@[^@]+\.[^2]{2,}"
    if (re.search(pattern,email)):
        return 1
    else:
        return 0

def checkPassword(password):
    pattern = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$"
    print(password)
    print(re.search(pattern, password))
    if (re.search(pattern,password)):
        return 1
    else:
        return 0
@application.route("/register",methods = ["POST"])
def register():
    email = request.json.get("email","")
    password = request.json.get("password", "")
    forename = request.json.get("forename","")
    surname = request.json.get("surname","")
    isCustomer = request.json.get("isCustomer",None)



    emailEmpty = len (email) == 0
    passwordEmpty = len(password) == 0
    forenameEmpty = len(forename) == 0
    surnameEmpty = len(surname) == 0

    if (forenameEmpty):
        return jsonify(message="Field forename is missing."), 400
    if (surnameEmpty):
        return jsonify(message="Field surname is missing."), 400
    if (emailEmpty):
        return jsonify(message="Field email is missing."), 400
    if (passwordEmpty):
        return jsonify(message="Field password is missing."),400
    if isCustomer is None:
        return jsonify(message="Field isCustomer is missing."),400


    result = parseaddr(email)

    if (len(result[1]) == 0 or not(checkEmail(email))):
        return jsonify(message="Invalid email."), 400

    if (not checkPassword(password)):
        return jsonify(message="Invalid password."), 400

    if User.query.filter(User.email == email).count() > 0:
        return jsonify(message="Email already exists."), 400

    user = User(email = email,password = password,forename = forename, surname = surname)


    database.session.add(user)
    database.session.commit()

    if (isCustomer):
        idRole = 2
    else:
        idRole = 3

    userRole = UserRole(userId = user.id, roleId = idRole)
    database.session.add(userRole)
    database.session.commit()

    return Response("Registration successful.",status = 200)

jwt = JWTManager(application)

@application.route("/login",methods = ["POST"])
def login():
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    emailEmpty = len(email) == 0
    passwordEmpty = len(password) == 0

    if (emailEmpty):
        return jsonify(message="Field email is missing."), 400
    if (passwordEmpty):
        return jsonify(message="Field password is missing."),400

    result = parseaddr(email)
    if (len(result[1]) == 0 or not(checkEmail(email))):
        return jsonify(message="Invalid email."), 400

    user = User.query.filter( and_(User.email == email,User.password == password)).first()
    if (not user):
        return jsonify(message="Invalid credentials."), 400

    additionalClaims={
        "forename": user.forename,
        "surname": user.surname,
        "roles":[str(role) for role in user.roles]
    }

    accessToken = create_access_token(identity=user.email, additional_claims=additionalClaims);
    refreshToken = create_refresh_token(identity=user.email, additional_claims=additionalClaims);

    return jsonify(accessToken = accessToken,refreshToken = refreshToken),200

@application.route("/refresh",methods = ["POST"])
@jwt_required ( refresh = True )
def refresh():
    identity = get_jwt_identity();
    refreshClaims = get_jwt();

    additionalClaims={
        "forename":refreshClaims["forename"],
        "surname":refreshClaims["surname"],
        "roles":refreshClaims["roles"]
    }
    return jsonify(accessToken=create_access_token(identity=identity, additional_claims=additionalClaims)), 200

@application.route("/delete",methods = ["POST"])
@decorator.roleCheck(role = "admin")
def delete():

    email = request.json.get("email", "")

    emailEmpty = len(email) == 0

    if (emailEmpty):
        return jsonify(message="Field email is missing."), 400

    result = parseaddr(email)

    if (len(result[1]) == 0 or not (checkEmail(email))):
        return jsonify(message="Invalid email."), 400


    user = User.query.filter(User.email == email).first()

    if (not user):
        return jsonify(message="Unknown user."), 400

    database.session.delete(user)
    database.session.commit();
    return "", 200;

@application.route("/check",methods = ["POST"])
@jwt_required()
def check():
    return "Token is valid!"

@application.route("/",methods = ["GET"])
def index():
    return "Hello world"

if (__name__ == "__main__"):
    database.init_app(application)
    application.run(debug = True,host="0.0.0.0",port = 5002)