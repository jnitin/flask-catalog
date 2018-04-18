from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields


class CategorySchema(Schema):
    """Flask-REST-JSONAPI: Logical data abstraction for Category model"""
    class Meta:
        type_ = 'category'
        self_view = 'api.category_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'api.category_list'

    id = fields.Integer(as_string=True, dump_only=True)
    timestamp = fields.DateTime()
    name = fields.Str()

    user = Relationship(attribute='user',
                        self_view='api.category_user',
                        self_view_kwargs={'category_id': '<id>'},
                        related_view='api.user_detail',
                        related_view_kwargs={'category_id': '<id>'},
                        schema='UserSchema',
                        type_='user')


class ItemSchema(Schema):
    """Flask-REST-JSONAPI: Logical data abstraction for Item model"""
    class Meta:
        type_ = 'item'
        self_view = 'api.item_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'api.item_list'

    id = fields.Integer(as_string=True, dump_only=True)
    name = fields.Str()
    description = fields.Str()

    user = Relationship(attribute='user',
                        self_view='api.item_user',
                        self_view_kwargs={'item_id': '<id>'},
                        related_view='api.user_detail',
                        related_view_kwargs={'item_id': '<id>'},
                        schema='UserSchema',
                        type_='user')
