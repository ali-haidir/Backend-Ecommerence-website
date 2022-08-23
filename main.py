from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import request
from flask_marshmallow import Marshmallow
from flask import jsonify
from webargs.flaskparser import use_args
from flask_marshmallow import Marshmallow
from marshmallow import Schema, fields, post_load, ValidationError, validate, validates
from flask_marshmallow import Marshmallow
from marshmallow.decorators import post_load
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from http import HTTPStatus
import pycountry


app = Flask(__name__)
app.config['SECRET_KEY'] = 'some secret string here'

con = 'mysql+pymysql://root:mypass123@localhost/sac'
app.config['SQLALCHEMY_DATABASE_URI'] = con

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


@app.errorhandler(HTTPStatus.UNPROCESSABLE_ENTITY)
@app.errorhandler(HTTPStatus.BAD_REQUEST)
def webargs_error_handler(err):
    headers = err.data.get("headers", None)
    messages = err.data.get("messages", ["Invalid request."])
    if headers:
        return jsonify({"errors": messages}), err.code, headers
    else:
        return jsonify({"errors": messages}), err.code


db = SQLAlchemy(app)
ma = Marshmallow(app)

#Models = MOO

# relationships
#  1) Customer and order
#          customer 1 to orders many (1 to many)

# 2) Orders and Products
# assumtion that a popular product is there in every order
# many Orders many Products (many to many )


# Models MOO
# ______________________________________________________________________________________________________________
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    postcode = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(50), nullable=False, unique=True)

    orders = db.relationship(
        'Order', backref='customer', cascade="all, delete")


order_product = db.Table('order_product',
                         db.Column('order_id', db.Integer, db.ForeignKey(
                             'order.id'), primary_key=True),
                         db.Column('product_id', db.Integer, db.ForeignKey(
                             'product.id'), primary_key=True)
                         )


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    shipped_date = db.Column(db.DateTime)
    dilivered_date = db.Column(db.DateTime)
    coupon_code = db.Column(db.String(50))
    customer_id = db.Column(db.Integer, db.ForeignKey(
        'customer.id'), nullable=False)  # for edu purposes

    products = db.relationship("Product", secondary=order_product)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    price = db.Column(db.Integer, nullable=False)


# Schemas SOO


class CustomerScheme(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        include_relationships = True
        load_instance = True


class OrderScheme(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order
        include_relationships = True
        load_instance = True

    customer_id = fields.Int(required=True)

    order_date = fields.DateTime()
    shipped_date = fields.DateTime()
    dilivered_date = fields.DateTime()
    coupon_code = fields.Str()

    # @validates('shipped_date')
    # def validate_city(self, shipped_date):
    #
    #     print(shipped_date)
    #     # 2022-08-17 07:28:1
    #     regex = (
    #         r"^([0-9]{4}) - ([0 1]\d) - ([0 1 2 3]\d)\w{8} $"
    #     )


class ProductScheme(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        include_relationships = True
        load_instance = True
    name = fields.Str(validate=validate.Length(min=1, max=20))
    price = fields.Int(validate=validate.Range(min=1, max=2000))


def Email_check(value):
    if "@" in value and ".com" in value:

        return True
    else:
        raise ValidationError("Not a Valid Email")


class CustomerScheme2(Schema):
    first_name = fields.Str(
        required=True, validate=validate.Length(min=2, max=10))
    last_name = fields.Str(
        required=True, validate=validate.Length(min=0, max=5))
    address = fields.Str()
    city = fields.Str()

    email = fields.Str(validate=Email_check)
    # regex = r"^[a-z\d\.-]+ @[a-z\d-]+\.[a-z]{2,8}(\.[a-z]{2,8})? $"
    # email = fields.Str(validate=validate.Regexp(
    #     "^[a-z\d\.-]+ @[a-z\d-]+\.[a-z]{2,8}(\.[a-z]{2,8})? $"))

    @validates('city')
    def validate_city(self, city):
        print(city)
        # cities = ["Islamabad", "Karachi", "Lahore"]
        # if city in cities:
        #     return True
        # else:
        #     raise ValidationError(" city not valid city ")
        for co in list(pycountry.countries):

            if city in co.name:
                return True
            else:
                continue
        raise ValidationError("country not a real country")

    @post_load
    def load1(self, data, **kwargs):
        # breakpoint()
        return Customer(**data)


class ProductScheme2(ma.SQLAlchemyAutoSchema):
    name = fields.Str(validate=validate.Length(min=1, max=20))
    price = fields.Int(validate=validate.Range(min=1, max=2000))

    @post_load
    def load1(self, data, **kwargs):
        # breakpoint()
        return Product(**data)


# _________________________________________________________________________________________________________
# routes here ROO

# @app.route('/insert', methods=["POST"])
# def insert_product():
#     new_product = Product(name=request.args.get(
#         'name'), price=request.args.get('price'))
#     db.session.add(new_product)
#     db.session.commit()
#     return new_product.name

# --------------------------------------------------------------

#
# class ProductScheme2(ma.SQLAlchemyAutoSchema):
#     name = fields.Str(required=True, validate=validate.Length(min=5))
#     price = fields.Int()
#
#     @post_load
#     def load(self, data, **kwargs):
#
#         return Product(**data)


@app.route('/insert', methods=["POST"])
@use_args(ProductScheme, location="query")
def insert_product(args):
    # print(args)
    new_product = args
    db.session.add(new_product)
    db.session.commit()
    return new_product.name
# --------------------------------------------------------------------


# @app.route('/insert_cus', methods=["POST"])
# def insert_customer():
#     new_customer = Customer(first_name=request.args.get(
#         'first_name'),
#         last_name=request.args.get('last_name'),
#         address=request.args.get('address'),
#         city=request.args.get('city'),
#         email=request.args.get('email')
#     )
#     db.session.add(new_customer)
#     db.session.commit()
#     return new_customer.first_name


@app.route('/insert_cus', methods=["POST"])
@use_args(CustomerScheme2, location="query")
def insert_customer(args):

    try:
        # print("Arguments : ", args)

        new_customer = args
        # print(args)
        print("arguments: ", new_customer.email)

        db.session.add(new_customer)
        db.session.commit()
        return new_customer.first_name
    except Exception as e:
        # print("Error : ", e)
        return "error ..."


# @app.route('/insert_ord', methods=["POST"])
# def insert_order():
#     new_order = Order(customer_id=request.args.get(
#         'customer_id'))
#     db.session.add(new_order)
#     db.session.commit()
#     return jsonify(new_order.order_date)

@app.route('/insert_ord', methods=["POST"])
@use_args(OrderScheme, location="query")
def insert_order(args):
    new_order = args
    db.session.add(new_order)
    db.session.commit()
    return jsonify(new_order.order_date)


# updating route
@app.route('/update_pro', methods=["PUT"])
@use_args(ProductScheme, location="json")
def update_pro(args):
    updated_product = args
    db.session.add(updated_product)
    db.session.commit()
    return jsonify(updated_product.name)


@app.route('/update_cus', methods=["PUT"])
@use_args(CustomerScheme2, location="json")
def update_cus(args):
    updated_cus = args
    # print(updated_cus.first_name)
    db.session.add(updated_cus)
    db.session.commit()
    return jsonify(updated_cus.first_name)


@app.route('/update_ord', methods=["PUT"])
@use_args(OrderScheme, location="json")
def update_ord(args):
    updated_ord = args
    db.session.add(updated_ord)
    db.session.commit()
    return jsonify(updated_ord.id)


# delete route
@app.route('/delete_pro', methods=["DELETE"])
@use_args({"id": fields.Integer()}, location="json")
def delete_pro(args):
    deleteed_product = db.session.query(
        Product).filter(Product.id == args["id"]).first()

    db.session.delete(deleteed_product)
    db.session.commit()
    return jsonify(deleteed_product.name)


@app.route('/delete_cus', methods=["DELETE"])
@use_args({"id": fields.Integer()}, location="json")
def delete_cus(args):
    deleted_cus = db.session.query(Customer).filter(
        Customer.id == args["id"]).first()
    # breakpoint()

    db.session.delete(deleted_cus)
    db.session.commit()
    return jsonify(deleted_cus.first_name)


@app.route('/delete_ord', methods=["DELETE"])
@use_args({"id": fields.Integer()}, location="json")
def delete_ord(args):
    deleted_ord = db.session.query(Order).filter(
        Order.id == args["id"]).first()
    db.session.delete(deleted_ord)
    db.session.commit()
    return jsonify(deleted_ord.id)


# joo
# working with joins

# inner joins

# getiing orders corresponding to Customers

class join_schema2(ma.SQLAlchemyAutoSchema):
    Customer = fields.Nested(CustomerScheme())
    Order = fields.Nested(OrderScheme())


@app.route('/innerjoin', methods=["GET"])
def inner_join():

    schema = join_schema2(many=True)
    r = db.session.query(Customer, Order).join(
        Order, Customer.id == Order.customer_id).order_by(Customer.id).all()
    # print(r)

    for result in r:
        if result[1]:
            print('Customer id: {} Name: {}{} order id : {}'.format(
                result[0].id, result[0].first_name, result[0].last_name, result[1].id))
        else:
            print('Name: {} did not make any Purchase'.format(
                result[0].first_name))

    output = schema.dump(r)
    # print("output  = ", output)
    return output

    return output

# getting Customers corresponding to orders


@app.route('/ijo', methods=["GET"])
def ijo():
    r = db.session.query(Order, Customer).join(
        Customer, Customer.id == Order.customer_id).order_by(Customer.id).all()
    print(r)
    for result in r:
        if result[1]:
            print('Oder id: {} Name: {}{} Customer id : {}'.format(
                result[0].id, result[1].first_name, result[1].last_name, result[1].id))
        else:
            print('Name: {} did not make any Purchase'.format(
                result[0].first_name))
    return "True"


# outerjoin

# getiing orders corresponding to Customers
class join_schema(ma.SQLAlchemyAutoSchema):
    first_name = fields.Str()
    id = fields.Int()


@app.route('/oj', methods=["GET"])
def oj():
    # schema = CustomerScheme(many=True)
    schema = join_schema(many=True)

    # q = db.session.query(Customer).all()
    # print("q = ", q)
    r = db.session.query(Customer.first_name, Order.id).outerjoin(
        Order, Customer.id == Order.customer_id).all()
    print(r)

    # for result in r:
    #     if result[1]:
    #         print('Customer id: {} Name: {}{} order id : {}'.format(
    #             result[0].id, result[0].first_name, result[0].last_name, result[1].id))
    #     else:
    #         print('Customer id: {} with Name: {} did not make any Purchase'.format(
    #             result[0].id, result[0].first_name))
    #
    output = schema.dump(r)
    print("output  = ", output)
    return output


# getting Customers corresponding to orders
@app.route('/ojo', methods=["GET"])
def ojo():
    customer_scheme = join_schema(many=True)
    r = db.session.query(Order.id, Customer.first_name).outerjoin(
        Customer, Customer.id == Order.customer_id).order_by(Customer.id).all()
    print(r)
    # for result in r:
    #     if result[1]:
    #         print('Oder id: {} Name: {}{} Customer id : {}'.format(
    #             result[0].id, result[1].first_name, result[1].last_name, result[1].id))
    #     else:
    #         print('Customer id: {} with Name: {} did not make any Purchase'.format(
    #             result[0].id, result[0].first_name))
    output = customer_scheme.dump(r)
    print("output = ", output)
    return output


# # orders products
# r = db.session.query(Order, Product).join(
#     Product, Order.products.id == Product.id).all()
# print("result = ", r)
# # for result in r:
#     if result[1]:
#         print('Oder id: {} Name: {}{} Customer id : {}'.format(
#             result[0].id, result[1].first_name, result[1].last_name, result[1].id))
#     else:
#         print('Name: {} did not make any Purchase'.format(
#             result[0].first_name))


@app.route('/')
def home():
    return "Hello World"
