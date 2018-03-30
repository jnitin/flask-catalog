import os

from flask import Blueprint, render_template, current_app, request, flash, \
    url_for, redirect, session, abort
from flask_login import login_required, current_user

from ..extensions import db
from . import Meal


meal = Blueprint('meal', __name__)

@meal.route('/meals/', methods=['GET'])
@meal.route('/meals/<int:meal_id>', methods=['GET'])
@login_required
def meals(meal_id=None):
    """List all the meals for current user"""
    meal_active = None
    user_meals = Meal.query.filter_by(user_id=current_user.id).all()
    return render_template('meal/meals.html',
                           meals=user_meals,
                           meal_id=meal_id,
                           meal_active=meal_active)


@meal.route('/meals/<int:meal_id>/edit', methods=['GET'])
@login_required
def edit_meal(meal_id):
    """Edit a meal"""
    return "edit_meal to be implemented"


@meal.route('/meals/<int:meal_id>/delete', methods=['GET'])
@login_required
def delete_meal(meal_id):
    """Delete a meal"""
    return "delete_meal to be implemented"
