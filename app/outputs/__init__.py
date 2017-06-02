from flask import Blueprint

outputs = Blueprint('outputs', __name__)

from . import views
