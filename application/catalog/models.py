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

    @staticmethod
    def insert_initial_data():
        # Create dummy user
        u = User(email="BigBelly@demo-beers.com",password="fyeo",
                     name="Big Belly")
        db.session.add(u)
        db.session.commit()

        beers = [
            {
                "category": "American Amber / Red Ale",
                "items": [
                    {"name": "Fat Tire Amber Ale",
                     "description": "Made by New Belgium Brewing"},
                    {"name": "Nugget Nectar",
                     "description": "Made by Tröegs Brewing Company"},
                    {"name": "Hop Head Red Ale",
                     "description": "Made by Green Flash Brewing Co."},
                    {"name": "Amber Ale",
                     "description": "Made by Bell's Brewery - Eccentric Café & General Store"},
                    {"name": "Hopback Amber Ale",
                     "description": "Made by Tröegs Brewing Company"},
                    {"name": "Flipside Red IPA",
                     "description": "Made by Sierra Nevada Brewing Co."},
                    {"name": "Censored",
                     "description": "Made by Lagunitas Brewing Company"},
                    {"name": "Lucky 13 Mondo Large Red Ale",
                     "description": "Made by Lagunitas Brewing Company"},
                    {"name": "Nosferatu",
                     "description": "Made by Great Lakes Brewing Co."},
                    {"name": "Red Rocket Ale",
                     "description": "Made by Bear Republic Brewing Co."},
                    {"name": "Zoe",
                     "description": "Made by Maine Beer Company"},
                    {"name": "Santa's Private Reserve Ale",
                     "description": "Made by Rogue Ales"},
                    {"name": "Ruedrich's Red Seal Ale",
                     "description": "Made by North Coast Brewing Co."},
                    {"name": "Hog Heaven: Imperial Red IPA",
                     "description": "Made by Avery Brewing Company"},
                    {"name": "Boont Amber Ale",
                     "description": "Made by Anderson Valley Brewing Company"},
                    {"name": "Highland Gaelic Ale",
                     "description": "Made by Highland Brewing"},
                    {"name": "California Amber",
                     "description": "Made by Ballast Point Brewing Company"},
                    {"name": "American Amber Ale",
                     "description": "Made by Rogue Ales"},
                    {"name": "Tocobaga Red Ale",
                     "description": "Made by Cigar City Brewing"},
                    {"name": "Avalanche Ale",
                     "description": "Made by Breckenridge Brewery"}
                ]
            },
            {
                "category": "American Barleywine",
                "items": [
                    {"name": "Bigfoot Barleywine-Style Ale",
                     "description": "Made by Sierra Nevada Brewing Co."},
                    {"name": "Third Coast Old Ale",
                     "description": "Made by Bell's Brewery - Eccentric Café & General Store"},
                    {"name": "Olde School Barleywine",
                     "description": "Made by Dogfish Head Craft Brewery"},
                    {"name": "Old Ruffian Barley Wine",
                     "description": "Made by Great Divide Brewing Company"},
                    {"name": "Brewer's Reserve Bourbon Barrel Barleywine",
                     "description": "Made by Central Waters Brewing Co"},
                    {"name": "Old Guardian Barley Wine Style Ale",
                     "description": "Made by Stone Brewing"},
                    {"name": "Old Horizontal",
                     "description": "Made by Victory Brewing Company - Downingtown"},
                    {"name": "Behemoth Blonde Barleywine",
                     "description": "Made by 3 Floyds Brewing Co."},
                    {"name": "Olde GnarlyWine",
                     "description": "Made by Lagunitas Brewing Company"},
                    {"name": "Old Numbskull",
                     "description": "Made by AleSmith Brewing Company"},
                    {"name": "Flying Mouflan",
                     "description": "Made by Tröegs Brewing Company"},
                    {"name": "Sierra Nevada Bigfoot Barleywine Style Ale - Barrel-Aged",
                     "description": "Made by Sierra Nevada Brewing Co."},
                    {"name": "XS Old Crustacean",
                     "description": "Made by Rogue Ales"},
                    {"name": "Doggie Claws",
                     "description": "Made by Hair of the Dog Brewing Company / Brewery and Tasting Room"},
                    {"name": "A Deal With The Devil",
                     "description": "Made by Anchorage Brewing Company"},
                    {"name": "Cockeyed Cooper",
                     "description": "Made by Uinta Brewing Company"},
                    {"name": "Helldorado",
                     "description": "Made by Firestone Walker Brewing Co"},
                    {"name": "Solstice D'hiver",
                     "description": "Made by Brasserie Dieu du Ciel!"},
                    {"name": "Anniversary Barley Wine Ale",
                     "description": "Made by Uinta Brewing Company"},
                    {"name": "Barleywine Style Ale",
                     "description": "Made by Green Flash Brewing Co."}
                ]
            }
        ]

        for beer in beers:
            category_name = beer['category']
            c = Category(name=category_name)
            db.session.add(c)
            db.session.commit()
            for item in beer['items']:
                i = Item(name=item['name'],
                         description=item['description'],
                         user_id=u.id,
                         category_id=c.id)
                db.session.add(i)
            db.session.commit()




