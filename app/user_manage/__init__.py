from flask import Blueprint

user_manage = Blueprint('admin_manage', __name__)

from . import views
