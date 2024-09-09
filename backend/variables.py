from flask_restful import reqparse, fields, marshal_with
import os
from pathlib import Path

class Commons:
    cur_path = __name__.split('.')[0]
    PARENT =  str(Path(cur_path).parent.absolute())
    HOME = str(Path(cur_path).absolute())

    UPLOAD_FOLDER = ".uploads"
    ALLOWED_EXTENSIONS = {'jpg','png','jpeg'}
    
    DB_HOME = ".config"
    DB_NAME = "database.db"
    DB_ROOT = os.path.join(HOME,DB_HOME)
    UPLOAD_ROOT = os.path.join(PARENT,UPLOAD_FOLDER)
    DB_PATH = os.path.join(DB_ROOT,DB_NAME)

    ##### marshal fields
    account_fields = {
        'id': fields.Integer,
        'email':fields.String,
        'password':fields.String,
        'status':fields.Boolean,
        }
        
    message_fields = {
        'id': fields.Integer,
        'tgt': fields.Integer,
        'ref': fields.Integer,
        'cart_id': fields.Integer,
        'message': fields.String,
        'cost': fields.Integer,
        'date': fields.String,
        'status':fields.Integer,
        }

    store_fields = {
        'id': fields.Integer,
        'tag': fields.String,
        'product': fields.String,
        'car': fields.String,
        'price': fields.String,
        'quantity':fields.Integer,
        }
    
    cart_fields = {
        'id': fields.Integer,
        'ref': fields.Integer,
        'tag': fields.String,
        'car': fields.String,
        'product': fields.String,
        'location': fields.String,
        'price':fields.Integer,
        'quantity':fields.Integer,
        'date':fields.String,
        'status':fields.Integer,
        }
    
    service_fields = {
        'id': fields.Integer,
        'tag': fields.String,
        'car': fields.String,
        'sevice': fields.String,
        'price': fields.Integer,
    }
    
    @marshal_with(account_fields)
    def marshal_accounts(data):
        return data

    @marshal_with(message_fields)
    def marshal_messages(data):
        return data
    
    @marshal_with(store_fields)
    def marshal_store(data):
        return data
    
    @marshal_with(cart_fields)
    def marshal_cart(data):
        return data

    @marshal_with(service_fields)
    def marshal_service(data):
        return data

class Var:
    # parse args
    acccount_args = reqparse.RequestParser()
    acccount_args.add_argument("email",type=str)
    acccount_args.add_argument("reqmail",type=str)
    acccount_args.add_argument("passwd",type=str)
   
    message_args = reqparse.RequestParser()
    message_args.add_argument("message",type=str)
    message_args.add_argument("cost",type=str)
    message_args.add_argument("id",type=int)
    
    store_args = reqparse.RequestParser()
    store_args.add_argument("tag",type=str)
    store_args.add_argument("quantity",type=int)
    store_args.add_argument("quality",type=str)
    store_args.add_argument("filter",type=str)
    store_args.add_argument("car",type=str)
    store_args.add_argument("product",type=str)
    store_args.add_argument("service",type=str)
    store_args.add_argument("location",type=str)
    
    
if not os.path.exists(Commons.DB_ROOT) or not os.path.isdir(Commons.DB_ROOT): os.makedirs(Commons.DB_ROOT) 