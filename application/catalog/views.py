import os

from flask import Blueprint, render_template, send_from_directory, request, \
    current_app, flash
from flask_login import login_required, current_user

from .forms import ItemsForm

from ..extensions import db
from ..utils import get_current_time


catalog = Blueprint('catalog', __name__, url_prefix='/catalog')


@catalog.route('/items', methods=['GET'])
def items():
    form = ItemsForm(obj=current_user)

    return render_template('catalog/items.html', form=form)
