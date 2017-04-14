from flask import Blueprint

about = Blueprint('outputs', __name__)

from . import views
