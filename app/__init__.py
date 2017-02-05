from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.mail import Mail
from flask.ext.moment import Moment
from flask.ext.login import LoginManager
from flask.ext.pagedown import PageDown
from config import config
from flask_sqlalchemy import SQLAlchemy
from .util import ListConverter
 


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

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    from .api_1_0 import api as api_1_0_blueprint
    app.register_blueprint(api_1_0_blueprint, url_prefix='/api')

    from .user_guide import user_guide as user_guide_blueprint
    app.register_blueprint(user_guide_blueprint, url_prefix='/user-guide')

    from .data_manage import data_manage as data_manage_blueprint
    app.register_blueprint(data_manage_blueprint, url_prefix='/data-manage')

    return app
