from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from .variables import Commons as cn
from flask import Flask
import base64
from sqlalchemy.sql import func
import os
from datetime import datetime
import csv

def get_time():
    return datetime.strftime(datetime.now(),"%Y-%m-%d %H:%M:%S")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+cn.DB_PATH
app.config['SECRET_KEY'] = "dsdsfagkvjvnwoidz"
app.config['UPLOAD_FOLDER'] = cn.UPLOAD_FOLDER

if not os.path.exists(app.config['UPLOAD_FOLDER']): os.makedirs(app.config['UPLOAD_FOLDER'])

db = SQLAlchemy(app)
app.app_context().push()

#### creating db models ###########

class Accounts(db.Model):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True,nullable=False,autoincrement=True)
    email = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Boolean, default=False)
    
class Messages(db.Model):
    __tablename__ = 'messages'
   
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    ref = db.Column(db.Integer,db.ForeignKey('accounts.id'),default=-1)
    tgt = db.Column(db.Integer,db.ForeignKey('accounts.id'),default=-1)
    cart_id = db.Column(db.Integer,db.ForeignKey('cart.id'),default=-1)
    message = db.Column(db.String(1000), default="")
    cost = db.Column(db.Integer,default=0)
    date = db.Column(db.String,default=get_time())
    status = db.Column(db.Integer, default=0)

class Store(db.Model):
    __tablename__ = 'store'
   
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    tag = db.Column(db.String(255), default="")
    car = db.Column(db.String(255), default="")
    product = db.Column(db.String(255), default="")
    price = db.Column(db.Integer, default=0)
    quantity = db.Column(db.Integer, default=0)

class Services(db.Model):
    __tablename__ = 'service'
   
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    tag = db.Column(db.String(255), default="")
    car = db.Column(db.String(255), default="")
    sevice = db.Column(db.String(255), default="")
    price = db.Column(db.Integer, default=0)

class Cart(db.Model):
    __tablename__ = 'cart'
   
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    ref = db.Column(db.Integer,db.ForeignKey('accounts.id'),default=-1)
    tag = db.Column(db.String(255), default="")
    car = db.Column(db.String(255), default="")
    product = db.Column(db.String(255), default="")
    location = db.Column(db.String(255), default="")
    price = db.Column(db.Integer, default=0)
    quantity = db.Column(db.Integer, default=0)
    date = db.Column(db.String,default=get_time())
    status = db.Column(db.Integer, default=0)

if not os.path.exists(os.path.join(cn.DB_ROOT,cn.DB_NAME)): 
    db.create_all()

    db.session.add(
        Accounts(
            email = "admin@autogarage.org",
            password = generate_password_hash("admin123",method='sha256'),
            status = True,
        )
    )
    db.session.commit()
    