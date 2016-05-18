from flask import Blueprint

compadre = Blueprint('compadre', __name__)

from . import views
from ..models import Permission


@compadre.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
