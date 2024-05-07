# web-store

Application for customer, buyer, warehouseman and admin relations.

Testing commands:

python main.py --type authentication --authentication-address http://127.0.0.1:5002 --jwt-secret JWT_SECRET_KEY --roles-field roles --administrator-role admin --customer-role buyer --warehouse-role warehouseman

python main.py --type level0 --with-authentication --authentication-address http://127.0.0.1:5002 --customer-address http://127.0.0.1:5001 --warehouse-address http://127.0.0.1:5003

python main.py --type level1 --with-authentication --authentication-address http://127.0.0.1:5002 --customer-address http://127.0.0.1:5001 --warehouse-address http://127.0.0.1:5003

python main.py --type level3 --with-authentication --authentication-address http://127.0.0.1:5002 --customer-address http://127.0.0.1:5001 --warehouse-address http://127.0.0.1:5003 --administrator-address http://127.0.0.1:5006

python main.py --type all --with-authentication --authentication-address http://127.0.0.1:5002 --jwt-secret JWT_SECRET_KEY --roles-field roles --administrator-role admin --customer-role buyer --warehouse-role warehouseman --customer-address http://127.0.0.1:5001 --warehouse-address http://127.0.0.1:5003 --administrator-address http://127.0.0.1:5006
