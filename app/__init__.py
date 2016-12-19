from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.mail import Mail
from flask.ext.moment import Moment
from flask.ext.login import LoginManager
from flask.ext.pagedown import PageDown
from config import config
from sqlalchemy.orm.query import Query
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.query import Query
from sqlalchemy import or_
from flask.ext.sqlalchemy import SQLAlchemy

class VersionQuery(Query):
    def __iter__(self):
            return Query.__iter__(self)
    def all(self):
            from models import Status, Version
            status = Status.query.filter(Status.status_name=='Green').first()
            return [s for s in self.filter(Version.statuses == status).filter(Version.checked == True)]
    # def original(self):
    #         return self.filter(Version.version_number == 0)[0]
    # def latest(self):
    #         status = Status.query.filter(Status.status_name=='Green').first()
    #         return self.filter(Version.statuses == status).filter(Version.checked == True).order_by(Version.version_number.desc())[0]
    # def all_checked(self):
    #         amber = Status.query.filter(Status.status_name=='Amber').first()
    #         green = Status.query.filter(Status.status_name=='Green').first()
    #         return self.filter(or_(Version.statuses == amber, Version.statuses == green)).filter(Version.checked == True).order_by(Version.version_number.desc())
    # def all_checked_unchecked(self):
    #         amber = Status.query.filter(Status.status_name=='Amber').first()
    #         green = Status.query.filter(Status.status_name=='Green').first()
    #         return [s for s in self.filter(or_(Version.statuses == amber, Version.statuses == green)).order_by(Version.version_number.desc())]
    # def all_v(self):
    #         return [s for s in self.all()]
    # def get_version(self, id):
    #         return self.filter(Version.version_number == id)[0]

# db = SQLAlchemy(session_options={'query_cls': VersionQuery })

db = SQLAlchemy()

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
pagedown = PageDown()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

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

    from .api_1_0 import api as api_1_0_blueprint
    app.register_blueprint(api_1_0_blueprint, url_prefix='/api')

    from .user_guide import user_guide as user_guide_blueprint
    app.register_blueprint(user_guide_blueprint, url_prefix='/user-guide')

    from .compadre import compadre as compadre_blueprint
    app.register_blueprint(compadre_blueprint, url_prefix='/compadre')

    return app
