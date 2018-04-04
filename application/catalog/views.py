import os

from flask import Blueprint, render_template, current_app, request, flash, \
    url_for, redirect, session, abort
from flask_login import login_required, current_user

from ..extensions import db
from ..catalog import Category, Item


catalog = Blueprint('catalog', __name__, url_prefix='/catalog')

@catalog.route('/categories/', methods=['GET'])
def categories():
    # redirect it to the first existing category_id
    categories = Category.query.all()
    return redirect(url_for('catalog.category_items',
                            category_id=categories[0].id))


@catalog.route('/categories/<int:category_id>/items', methods=['GET'])
def category_items(category_id):
    # All the items of category_id
    categories = Category.query.all()
    category_active = Category.query.filter_by(id=category_id).first()
    if category_active:
        items = Item.query.filter_by(category_id=category_id).all()
        return render_template('catalog/items.html',
                               categories=categories,
                               category_id=category_id,
                               category_active = category_active,
                               items=items,
                               item_id=0,
                               item_active=None)
    abort(404)


@catalog.route('/categories/<int:category_id>/items/<int:item_id>/', methods=['GET'])
def category_item(category_id, item_id):
    # Details of an item
    categories = Category.query.all()
    category_active = Category.query.filter_by(id=category_id).first()
    if category_active:
        items = Item.query.filter_by(category_id=category_id).all()
        item_active = Item.query.filter_by(id=item_id).first()
        if item_active:
            return render_template('catalog/items.html',
                                   categories=categories,
                                   category_id=category_id,
                                   category_active = category_active,
                                   items=items,
                                   item_id=item_id,
                                   item_active=item_active)
    abort(404)

@catalog.route('/categories/add',
               methods=['GET', 'POST'])
@login_required
def add_category():
    return 'TODO: IMPLEMENT add_category'

@catalog.route('/categories/<int:category_id>/edit',
               methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    return 'TODO: IMPLEMENT edit_category'

@catalog.route('/categories/<int:category_id>/delete',
               methods=['GET', 'POST'])
@login_required
def delete_category(category_id):
    return 'TODO: IMPLEMENT delete_category'

@catalog.route('/categories/<int:category_id>/items/add',
               methods=['GET', 'POST'])
@login_required
def add_category_item(category_id):
    return 'TODO: IMPLEMENT add_category_item'

@catalog.route('/categories/<int:category_id>/items/<int:item_id>/edit',
               methods=['GET', 'POST'])
@login_required
def edit_category_item(category_id, item_id):
    return 'TODO: IMPLEMENT edit_category_item'


@catalog.route('/categories/<int:category_id>/items/<int:item_id>/delete',
               methods=['GET', 'POST'])
@login_required
def delete_category_item(category_id, item_id):
    return 'TODO: IMPLEMENT delete_category_item'
