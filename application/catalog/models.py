from sqlalchemy import Column, desc
from sqlalchemy.orm import backref
from flask import current_app, g
from flask_login import UserMixin, AnonymousUserMixin
from ..extensions import db, login_manager, bcrypt
from ..user import User
import os
import base64
from datetime import datetime, date, timedelta


class Category(db.Model):

    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    name = db.Column(db.String(96), unique=True)
    description = db.Column(db.String(1024))


class Item(db.Model):

    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    name = db.Column(db.String(96), unique=True)
    description = db.Column(db.String(1024))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))

    user = db.relationship('User', backref=db.backref('items'))
    category = db.relationship('Category', backref=db.backref('items'))




