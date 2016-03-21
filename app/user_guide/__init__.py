from flask import Blueprint

user_guide = Blueprint('user_guide', __name__)

from . import views
