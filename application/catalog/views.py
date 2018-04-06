import os

from flask import Blueprint, render_template, current_app, request, flash, \
    url_for, redirect, session, abort
from flask_login import login_required, current_user

from .forms import add_category_form, edit_category_form, \
     add_item_form, edit_item_form
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
    form = add_category_form()

    if form.validate_on_submit():
        if Category.query.filter_by(name=form.name.data).first():
            flash("Category '<b>{}</b>' already exists".format(form.name.data),
                  'danger')
        else:
            new_category = Category(name=form.name.data,
                                    user_id=current_user.id)
            db.session.add(new_category)
            db.session.commit()

            flash("Category '<b>{}</b>' created".format(form.name.data),
                  'success')

            return redirect(url_for('catalog.category_items',
                                    category_id=new_category.id))

    return render_template('catalog/add_category.html', form=form)

@catalog.route('/categories/<int:category_id>/edit',
               methods=['GET', 'POST'])
@login_required
def edit_category(category_id):

    category_active = Category.query.filter_by(id=category_id).first()

    if category_active is None:
        abort(404)

    if category_active.user != current_user:
        message = 'You are not authorized to edit this category, because'+\
            ' you are not the owner.'
        return render_template('catalog/403.html', message=message)

    # pass category_active to initialize the values of the fields
    form = edit_category_form(obj=category_active)

    if form.validate_on_submit():
        if Category.query.filter_by(name=form.name.data).first():
            flash("Category '<b>{}</b>' already exists".format(form.name.data),
                  'danger')
        else:
            category_active.name=form.name.data
            db.session.commit()

            flash("Category renamed to '<b>{}</b>'".format(form.name.data),
                  'success')

            return redirect(url_for('catalog.category_items',
                                    category_id=category_id))

    return render_template('catalog/edit_category.html', form=form,
                           category_active = category_active)

@catalog.route('/categories/<int:category_id>/delete',
               methods=['GET'])
@login_required
def delete_category(category_id):
    #
    # NOTES:
    # Confirmation if user really wants to delete is done on client side
    # so, we do not use a form asking for confirmation, just go & delete it
    #
    category_active = Category.query.filter_by(id=category_id).first()

    if category_active is None:
        abort(404)

    if category_active.user != current_user:
        message = 'You are not authorized to delete this category, because'+\
            ' you are not the owner.'
        return render_template('catalog/403.html', message=message)

    # first delete all items that belong to this category
    # since user owns this category, we allow deletion all items, even
    # those that were added by other users.
    items = Item.query.filter_by(category_id=category_id).all()
    for item in items:
        db.session.delete(item)

    # now delete the category
    cat_name = category_active.name  # save name for flash message
    db.session.delete(category_active)
    db.session.commit()

    flash("Deleted category '<b>{}</b>' and all it's Items".format(cat_name),
          'success')

    return redirect(url_for('catalog.categories'))


@catalog.route('/categories/<int:category_id>/items/add',
               methods=['GET', 'POST'])
@login_required
def add_category_item(category_id):
    category_active = Category.query.filter_by(id=category_id).first()

    if category_active is None:
        abort(404)

    form = add_item_form()

    if form.validate_on_submit():
        if Item.query.filter_by(name=form.name.data).first():
            flash("Item '<b>{}</b>' already exists".format(form.name.data),
                  'danger')
        else:
            new_item = Item(name=form.name.data,
                            description=form.description.data,
                            user_id=current_user.id,
                            category_id=category_id)
            db.session.add(new_item)
            db.session.commit()

            flash("Item '<b>{}</b>' Created".format(form.name.data),
                  'success')

            return redirect(url_for('catalog.category_item',
                                    category_id=category_id,
                                    item_id=new_item.id))

    return render_template('catalog/add_category_item.html', form=form,
                           category_active = category_active)

@catalog.route('/categories/<int:category_id>/items/<int:item_id>/edit',
               methods=['GET', 'POST'])
@login_required
def edit_category_item(category_id, item_id):
    category_active = Category.query.filter_by(id=category_id).first()
    item_active = Item.query.filter_by(id=item_id).first()

    if category_active is None or item_active is None:
        abort(404)

    # pass item_active to initialize the values of the fields
    form = edit_item_form(obj=item_active)

    if form.validate_on_submit():
        # update description
        item_active.description=form.description.data
        db.session.commit()
        flash('Successfully updated Item description',
              'success')

        # check if name of item was modified, and if so, if new name is unique
        if form.name.data != item_active.name:
            if Item.query.filter_by(name=form.name.data).first():
                flash("Cannot rename Item to '<b>{}</b>', because that name already exists".format(form.name.data),
                      'danger')
            else:
                item_active.name=form.name.data
                db.session.commit()

                flash('Successfully updated Item name',
                      'success')

        return redirect(url_for('catalog.category_item',
                                category_id=category_id,
                                item_id=item_id))


    return render_template('catalog/edit_category_item.html', form=form,
                           category_active=category_active,
                           item_active=item_active)



@catalog.route('/categories/<int:category_id>/items/<int:item_id>/delete',
               methods=['GET', 'POST'])
@login_required
def delete_category_item(category_id, item_id):
    #
    # NOTES:
    # Confirmation if user really wants to delete is done on client side
    # so, we do not use a form asking for confirmation, just go & delete it
    #
    category_active = Category.query.filter_by(id=category_id).first()
    item_active = Item.query.filter_by(id=item_id).first()

    if category_active is None or item_active is None:
        abort(404)

    if item_active.user != current_user:
        message = 'You are not authorized to delete this item, because'+\
            ' you are not the owner.'
        return render_template('catalog/403.html', message=message)

    item_name = item_active.name  # save name for flash message
    db.session.delete(item_active)
    db.session.commit()

    flash("Deleted Item '<b>{}</b>'".format(item_name),
          'success')

    return redirect(url_for('catalog.categories'))