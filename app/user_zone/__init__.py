from flask import Blueprint

user_zone = Blueprint('user_zone', __name__)

from . import views