from flask_restful import Api, Resource,abort
from .models import *
from .variables import Var as Args
from .variables import Commons as cn
import mimetypes
import os
from flask import url_for, Response, request, jsonify, send_from_directory, current_app
import json
import base64
import time
from flask_login import login_user,login_required,logout_user,current_user
from werkzeug.security import generate_password_hash,check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime

from pathlib import Path
from sqlalchemy.sql import func

### generate endpoint resouces
class AutoGarage(Resource):
    def __init__(self):
        # try:
            self.acc = Args.acccount_args.parse_args()

            self.data = {
                "email": self.acc['email'],
                "reqmail": self.acc['reqmail'],
                "password": self.acc['passwd'],
                }
            
            self.storeReq = Args.store_args.parse_args()
        
            self.store = {
                "filter": self.storeReq['filter'],
                "tag": self.storeReq['tag'],
                "quantity": self.storeReq['quantity'],
                "quality": self.storeReq['quality'],
                "product": self.storeReq['product'],
                "service": self.storeReq['service'],
                "location": self.storeReq['location'],
                "car": self.storeReq['car'],
                }
            
            self.msg = Args.message_args.parse_args()
        
            self.info = {
                "id": self.msg['id'],
                "cost": self.msg['cost'],
                "message": self.msg['message'],

                }
        # except:
        #     pass
    
    @staticmethod
    def __check_action_(action):
        req = request.method
        methodAction = {
            "post":["login","load","logout","message"],
            "put":["register","purchase","multi"],
            "patch":["update","remove","status"],
        }
        if not methodAction.get(req.lower()): return
        if action.lower() not in methodAction[req.lower()]:
            return abort(405, message="Method not allowed to handle request")
   
    @staticmethod
    def __check_exist__(reqmail):
        exists = Accounts.query.filter_by(email=reqmail).first()
        if exists: return True, exists
        return False, None

    def __load__(self):
        if not self.data["reqmail"]: return abort(404, message=f"Invalid request.")
        exists,_ = self.__check_exist__(self.data["reqmail"])
        if not exists: return abort(404,message="Action not verified")
        if self.store["filter"] and self.store['filter'] == "service":
            all_service = Services.query.all()
            if not all_service: return abort(404,message="No data found")
            marsh_results = cn.marshal_service(all_service)
            returned_marsh = [] 
            for marsh_result in marsh_results:
                marsh_result.pop("id")
                returned_marsh.append(marsh_result)
            return {"results":returned_marsh},200
        
        if self.store["filter"] and self.store['filter'] == "store":
            all_stores = Store.query.all()
            if not all_stores: return abort(404,message="No data found")
            marsh_results = cn.marshal_store(all_stores)
            returned_marsh = [] 
            for marsh_result in marsh_results:
                marsh_result.pop("id")
                returned_marsh.append(marsh_result)
            return {"results":returned_marsh},200
        
        if self.store["filter"] and self.store['filter'] == "cart":
            all_cart = Cart.query.all()
            if not all_cart: return abort(404,message="No data found")
            marsh_results = cn.marshal_cart(all_cart)
            returned_marsh = [] 
            for marsh_result in marsh_results:
                target = Accounts.query.get(marsh_result["ref"])
                marsh_result["target"] = ""
                if target:
                    marsh = cn.marshal_accounts(target)
                    marsh_result["target"] = marsh["email"]
                marsh_result.pop("id")
                returned_marsh.append(marsh_result)
            return {"results":returned_marsh},200
        
        if self.store["filter"] and self.store['filter'] == "message":
            all_messeges = Messages.query.all()
            if not all_messeges: return abort(404,message="No data found")
            marsh_results = cn.marshal_messages(all_messeges)
            returned_marsh = [] 
            for marsh_result in marsh_results:
                target = Accounts.query.get(marsh_result["ref"])
                marsh_result["target"] = ""
                if target:
                    marsh = cn.marshal_accounts(target)
                    marsh_result["target"] = marsh["email"]
                #marsh_result.pop("id")
                returned_marsh.append(marsh_result)
            return {"results":returned_marsh},200

        return {}, 200
    
    def __logout__(self):
        if not self.data["reqmail"]: return abort(404, message=f"Invalid request.")
        exists,results = self.__check_exist__(self.data["reqmail"])
        if not exists: return abort(404,message="Action not verified")
        
        results.logout_date = get_time()
        results.authenticated = False

        db.session.add(results)
        db.session.commit()
        

        return {}, 200
    
    def __login__(self):
        if not self.data["email"] or not self.data["password"]: return abort(404, message=f"Invalid request.")
        exists,results = self.__check_exist__(self.data["email"])
        if not exists: return abort(409, message="Account not found!")
        if not check_password_hash(results.password,self.data["password"]): abort(409, message="Authentication failed")
        
        marsh_results = cn.marshal_accounts(results)
        marsh_results["priv"] = "user" 
        
        if marsh_results["id"] == 1:
            marsh_results["priv"] = "admin" 
        
        marsh_results["priv"] = marsh_results["priv"] + f'::{marsh_results["id"]}'
        marsh_results.pop("password")
        marsh_results.pop("id")
        
        return marsh_results,200
    
    def __message__(self):
        if not self.data["reqmail"]: return abort(404, message=f"Invalid request.")
        exists,sender = self.__check_exist__(self.data["reqmail"])
        if not exists: return abort(404,message="Action not verified")
        
        if self.info["message"]:
            db.session.add(
                Messages(
                    ref = sender.id,
                    message = self.info["message"],
                    cost = int(self.info["cost"]) if self.info["cost"] else 0,
                )
            )
            db.session.commit()
        
        return {}, 200


    def post(self,action):
        self.__check_action_(action)
        if action == "load": return self.__load__()
        if action == "login": return self.__login__()
        if action == "message": return self.__message__()
        return {},200

    def __register__(self):
        ignored = ["reqmail"]
        for k,v in self.data.items():
            print(k,v)
            if v == None and k not in ignored: return abort(404, message="Invalid request")
        exists,results = self.__check_exist__(self.data["email"])
        if exists: return abort(409, message="Account already exists!")
        return Accounts(
            email = self.data["email"],
            password = generate_password_hash(self.data["password"],method='sha256'),
        )

    def __add_multi__(self):
        if not self.data["reqmail"]: return abort(404, message=f"Invalid request.")
        exists,sender = self.__check_exist__(self.data["reqmail"])
        if not exists: return abort(404,message="Action not verified")
        if not sender.status: return abort(404,message="Unauthorized action!")
        
        required = []
        model = None
        if self.store["product"]:
            required = [
                self.store["car"],
                self.store["product"],
                self.info["cost"],
                self.store["quantity"],
                self.store["tag"],
            ]

            for v in required:
                if v == None: return abort(404, message="Invalid request")

            model = Store(
                tag = self.store["tag"],
                car = self.store["car"],
                product = self.store["product"],
                price = self.info["cost"],
                quantity = self.store["quantity"],
            )
        if self.store["service"]:
            required = [
                self.store["service"],
                self.info["cost"],
                self.store["car"],
                self.store["tag"],
            ]

            for v in required:
                if v == None: return abort(404, message="Invalid request")

            model = Services(
                tag = self.store["tag"],
                car = self.store["car"],
                sevice = self.store["service"],
                price = self.info["cost"],
            )
        if self.data["email"]:
            required = [
                self.data["email"],
            ]


            for v in required:
                if v == None: return abort(404, message="Invalid request")
            
            exists,results = self.__check_exist__(self.data["email"])
            if exists: return abort(409, message="Account already exists!")

            model = Accounts(
                email = self.data["email"],
                password = generate_password_hash("123456",method='sha256'),
                status = True,
            )
        return model

    def __purchase__(self):
        if not self.data["reqmail"]: return abort(404, message=f"Invalid request.")
        exists,sender = self.__check_exist__(self.data["reqmail"])
        if not exists: return abort(404,message="Action not verified")
        required = [
            self.store["tag"],
            self.store["quantity"],
            self.store["product"],
            self.store["car"],
            self.store["location"],
            self.info["cost"],
            self.info["message"],
        ]
        for v in required:
            if v == None: return abort(404, message="Invalid request")
        
        store = Store.query.filter_by(car=self.store["car"],tag=self.store["tag"],product=self.store["product"]).first()
        if not store: return abort(404, message="Out of stock")

        marsh_result = cn.marshal_store(store)
        if int(marsh_result["quantity"]) < int(self.store["quantity"]): return abort(404,message="Out of stock")
        store.quantity = int(marsh_result["quantity"]) - int(self.store["quantity"])
        db.session.add(store)
        db.session.add(Cart(
            ref= sender.id,
            tag= self.store["tag"],
            quantity= int(self.store["quantity"]),
            product= self.store["product"],
            car= self.store["car"],
            price= self.info["cost"],
            location= self.store["location"],
        ))

        db.session.commit()

        just_added = Cart.query.filter_by(
            ref= sender.id,
            tag= self.store["tag"],
            quantity= int(self.store["quantity"]),
            product= self.store["product"],
            car= self.store["car"],
            price= self.info["cost"],
            location= self.store["location"]
        ).first()

        cart_id = -1
        if just_added: cart_id = just_added.id

        db.session.add(Messages(
            cart_id = just_added.id,
            ref = sender.id,
            message = self.info["message"],
            cost = int(self.info["cost"]) if self.info["cost"] else 0,
        ))

        db.session.commit()

        return None

    def put(self,action):
        self.__check_action_(action)
        model = None
        if action == "register": model = self.__register__()
        if action == "multi": model = self.__add_multi__()
        if action == "purchase": model = self.__purchase__()
        if model: 
            try:
                db.session.add(model)
                db.session.commit()
            except Exception as e:
                return {"message":f"Error adding data: {e}"},404
        
        return {"message":"Data added successfully"},201
    
    def __forgot__(self):
        if not self.data["reqmail"] or not self.data["password"] : return abort(404, message=f"Invalid request")
        
        exists,results = self.__check_exist__(self.data["reqmail"])
        if not exists: return abort(409, message="Account not found!")
        
        marsh_results = cn.marshal_accounts(results)
        if marsh_results['id'] == 1: return abort(409, message="Unverified request!")

        results.password = generate_password_hash(self.data["password"],method='sha256')
        db.session.add(results)
        db.session.commit()
        return {}, 201

    def __update__(self):
        if not self.data["reqmail"]: return abort(404, message=f"Invalid request")
        
        exists,results = self.__check_exist__(self.data["reqmail"])
        if not exists: return abort(409, message="Account not found!")
        
        if self.data["email"]:
            results.email = self.data["email"]
        
        if self.data["password"]:
            results.password = generate_password_hash(self.data["password"],method='sha256')
        
        db.session.add(results)
        db.session.commit()
        return {}, 201
    
    def __update_status__(self):
        if not self.data["reqmail"]: return abort(404, message=f"Invalid request")
        exists,results = self.__check_exist__(self.data["reqmail"])
        if not exists: return abort(409, message="Invalid request!")
        
        required = [
            self.info['id'],
            self.store['filter'],
        ]

        for v in required:
            if v == None: return abort(404, message="Invalid request")
        
        exists,sender_results = self.__check_exist__(self.store['filter'])
        if not exists: return abort(409, message="Invalid request!")

        orig_msg = Messages.query.filter_by(
            id = self.info['id'],
            ref = sender_results.id,
        ).first()

        if not orig_msg: return abort(404, message="Invalid request")
        
        marsh_msg = cn.marshal_messages(orig_msg)
        has_cart = False if marsh_msg['cart_id'] == -1 else True

        if has_cart:
            tgt_cart = Cart.query.get(
                marsh_msg['cart_id']
            )
            if tgt_cart:
                tgt_cart.status = 1
                db.session.add(tgt_cart)
        
        orig_msg.status = 1

        db.session.add(orig_msg)

        db.session.commit()


        return {}, 201
    
    def __update_message__(self):
        if not self.data["reqmail"]: return abort(404, message=f"Invalid request")
        exists,results = self.__check_exist__(self.data["reqmail"])
        if not exists: return abort(409, message="Account not found!")
        
        if self.info["id"]:
            msg = Messages.query.get(self.info["id"])
            msg.status = -1
            db.session.add(msg)
            db.session.commit()
        return {}, 201
        
    
    def patch(self,action):
        self.__check_action_(action)
        if action == "update": return self.__update__()
        if action == "status": return self.__update_status__()
        if action == "remove": return self.__update_message__()
        return {},201

    def delete(self,action):
        self.__check_action_(action)
        
        return {},200
    

def check_mime(extension):
    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp'
    }

    content_type = 'application/octet-stream'
    # Set the content type based on the file extension
    if extension in mime_types:
        content_type = mime_types[extension]
    return content_type

@app.route('/image/<tag>')
def get_image(tag):
    decoded_user = base64.b64decode(user.encode('utf-8')).decode('utf-8')
    exists, userData = AutoGarage().__check_exist__(str(decoded_user))
    if not exists: return abort(404,message="user missing")
    ref = cn.marshal_accounts(userData)['id']
    part_name = f"profile_{ref}"
    
    content_type = None
    filename = None
    for file in os.listdir(cn.UPLOAD_ROOT):
        fileObj = Path(file)
        ext = str(fileObj.suffix)
        name = (fileObj.stem)
        if part_name == name:
            content_type = check_mime(ext)
            filename = name + ext
            break
    
    
    if not content_type or not filename:
        filename = "no_profile.png"
        content_type = 'image/png'
    return send_from_directory(cn.UPLOAD_ROOT, filename, mimetype=content_type)

#### register endpoints
api = Api(app, prefix="/api/v1")
api.add_resource(AutoGarage,"/autogarage/<string:action>")