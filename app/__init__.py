from flask import Flask, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask.ext.bootstrap import Bootstrap
from flask.ext.mail import Mail
from flask.ext.moment import Moment
from flask.ext.login import LoginManager
from flask.ext.pagedown import PageDown
from config import config
from flask_sqlalchemy import SQLAlchemy
from .util import ListConverter
import os
 
from flask import Flask
from flask.ext.alchemydumps import AlchemyDumps, AlchemyDumpsCommand
from flask.ext.script import Manager
from flask.ext.sqlalchemy import SQLAlchemy

# init Flask

# init SQLAlchemy and Flask-Script

# from sqlalchemy.orm.query import Query
# from sqlalchemy import *
# from sqlalchemy.orm import *
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm.query import Query
# from sqlalchemy import or_
# from flask_sqlalchemy import SQLAlchemy, BaseQuery

db = SQLAlchemy()
login_manager = LoginManager()
bootstrap = Bootstrap()
mail = Mail()
moment = Moment()


pagedown = PageDown()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.url_map.converters['list'] = ListConverter

    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static/uploads')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    db = SQLAlchemy(app)
    manager = Manager(app)
    alchemydumps = AlchemyDumps(app, db)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)

    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        from flask.ext.sslify import SSLify
        sslify = SSLify(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from .about import about as about_blueprint
    app.register_blueprint(about_blueprint, url_prefix='/about')

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    from .outputs import outputs as outputs_blueprint
    app.register_blueprint(outputs_blueprint, url_prefix='/outputs')
    
    from .resources import resources as resources_blueprint
    app.register_blueprint(resources_blueprint, url_prefix='/resources')

    from .api_1_0 import api as api_1_0_blueprint
    app.register_blueprint(api_1_0_blueprint, url_prefix='/api')

    from .user_guide import user_guide as user_guide_blueprint
    app.register_blueprint(user_guide_blueprint, url_prefix='/user-guide')

    from .data_manage import data_manage as data_manage_blueprint
    app.register_blueprint(data_manage_blueprint, url_prefix='/data-manage')
    
    from .user_zone import user_zone as user_zone_blueprint
    app.register_blueprint(user_zone_blueprint, url_prefix='/user-area')

    from .outputs import outputs as outputs_blueprint
    app.register_blueprint(outputs_blueprint, url_prefix='/outputs')

    return app
