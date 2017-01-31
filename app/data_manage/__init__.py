from flask import Blueprint

data_manage = Blueprint('data_manage', __name__)

from . import views
from ..models import Permission


@data_manage.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
