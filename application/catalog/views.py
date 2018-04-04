import os

from flask import Blueprint, render_template, current_app, request, flash, \
    url_for, redirect, session, abort
from flask_login import login_required, current_user

from .forms import AddCategoryForm
from ..extensions import db
from ..catalog import Category, Item


catalog = Blueprint('catalog', __name__, url_prefix='/catalog')

@catalog.route('/categories/',
               methods=['GET'])
def categories():
    categories = Category.query.all()
    if categories:
        #redirect it to the first existing category_id
        return redirect(url_for('catalog.category_items',
                                category_id=categories[0].id))
    else:
        # database is empty
        return render_template('catalog/items.html',
                               categories=[],
                               category_id=0,
                               category_active = None,
                               items=[],
                               item_id=0,
                               item_active=None)




@catalog.route('/categories/<int:category_id>/items',
               methods=['GET'])
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

@catalog.route('/categories/<int:category_id>/items/<int:item_id>/',
               methods=['GET'])
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
    form = AddCategoryForm()

    if form.validate_on_submit():
        if Category.query.filter_by(name=form.name.data).first():
            flash('Category {} Already Exists'.format(form.name.data),
                  'danger')
        else:
            new_category = Category(name=form.name.data,
                                    user_id=current_user.id)
            db.session.add(new_category)
            db.session.commit()

            flash('New Category {} Created'.format(form.name.data),
                  'success')

            categories = Category.query.all()
            return render_template('catalog/items.html',
                                   categories=categories,
                                   category_id=new_category.id,
                                   category_active = new_category,
                                   items=[],
                                   item_id=0,
                                   item_active=None)

    return render_template('catalog/add_category.html', form=form)

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
