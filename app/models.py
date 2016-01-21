from datetime import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from markdown import markdown
import bleach
import json
from flask import current_app, request, url_for
from flask.ext.login import UserMixin, AnonymousUserMixin
from app.exceptions import ValidationError
from . import db, login_manager
from sqlalchemy.inspection import inspect


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))

    species = db.relationship("Species", backref="Species.user_created_id",primaryjoin="User.id==Species.user_modified_id", lazy="dynamic")

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     name=forgery_py.name.full_name(),
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()


    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()
        

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)


    def to_json(self):
        json_user = {
            
            'username': self.username,
            'member_since': self.member_since,
            'last_seen': self.last_seen
        }
        return json_user

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('ascii')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

''' Start Demog Stuff '''    

''' TODO: Stuff with arbitrary data - use methods to enter data (such as ecoregions), run these when deploying or setting up system '''
''' We will add a method to the matrix model to generate the unique ID, as designed by Danny, once we have decided the best protocol '''
''' Talk about enum (meta data within columns) vs meta tables '''

''' Meta tables '''
''' Meta Tables for Species '''
class IUCNStatus(db.Model):
    __tablename__ = 'iucn_status'
    id = db.Column(db.Integer, primary_key=True)
    status_code = db.Column(db.String(64), index=True)
    status_name = db.Column(db.String(64))
    status_description = db.Column(db.Text())

    species = db.relationship("Species", backref="iucn_status")

    @staticmethod
    def migrate():
        with open('app/data-migrate/species.json') as species_file:
            data = json.load(species_file)
            species = data["Species"]
            iucn = species["IUCNStatus"]

            for iu in iucn:
                i = IUCNStatus.query.filter_by(status_code=iu['status_code']).first()
                if i is None:
                    i = IUCNStatus()

                i.status_code = iu['status_code']
                i.status_name = iu['status_name']
                i.status_description = iu['status_description']

                db.session.add(i)
                db.session.commit()

    def inspects(self):
        i = inspect(self)
        class_name = i.class_.__name__
        return class_name
            

    def __repr__(self):
        return '<IUCN Status %r>' % self.id

class ESAStatus(db.Model):
    __tablename__ = 'esa_statuses'
    id = db.Column(db.Integer, primary_key=True)
    status_code = db.Column(db.String(64), index=True)
    status_name = db.Column(db.String(64))
    status_description = db.Column(db.Text())

    species = db.relationship("Species", backref="esa_status")

    @staticmethod
    def migrate():
        with open('app/data-migrate/species.json') as species_file:
            data = json.load(species_file)
            species = data["Species"]
            esa = species["ESAStatus"]

            for ea in esa:
                i = ESAStatus.query.filter_by(status_code=ea['status_code']).first()
                if i is None:
                    i = ESAStatus()

                i.status_code = ea['status_code']
                i.status_name = ea['status_name']

                db.session.add(i)
                db.session.commit()

    def __repr__(self):
        return '<ESA Status %r>' % self.id
''' End Meta Tables for Species '''

''' Meta Tables for Taxonomy '''
class TaxonomicStatus(db.Model):
    __tablename__ = 'taxonomic_statuses'
    id = db.Column(db.Integer, primary_key=True)
    status_name = db.Column(db.String(64), index=True)
    status_description = db.Column(db.Text())

    taxonomies = db.relationship("Taxonomy", backref="taxonomic_status")

    def __getitem__(self, key):
        return getattr(self, key)

    @staticmethod
    def migrate():
        with open('app/data-migrate/taxonomy.json') as taxonomy_file:
            data = json.load(taxonomy_file)
            species = data["Taxonomy"]
            taxonomic_status = species["TaxonomicStatus"]

            for tax in taxonomic_status:
                i = TaxonomicStatus.query.filter_by(status_name=tax['status_name']).first()
                if i is None:
                    i = TaxonomicStatus()

                i.status_name = tax['status_name']
                i.status_description = tax['status_description']

                db.session.add(i)
                db.session.commit()

    def __repr__(self):
        return '<Taxonomic Status %r>' % self.id
''' End Meta Tables for Taxonomy '''

''' Meta Tables for Plant Traits '''
class GrowthType(db.Model):
    __tablename__ = 'growth_types'
    id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(64), index=True)

    plant_traits = db.relationship("PlantTrait", backref="growth_type")

    @staticmethod
    def migrate():
        with open('app/data-migrate/plant_traits.json') as taxonomy_file:
            data = json.load(taxonomy_file)
            species = data["PlantTrait"]
            growth_types = species["GrowthType"]

            for types in growth_types:
                i = GrowthType.query.filter_by(type_name=types['type_name']).first()
                if i is None:
                    i = GrowthType()

                i.type_name = types['type_name']

                db.session.add(i)
                db.session.commit()

    def __repr__(self):
        return '<Growth Type %r>' % self.id

class GrowthFormRaunkiaer(db.Model):
    __tablename__ = 'growth_forms_raunkiaer'
    id = db.Column(db.Integer, primary_key=True, index=True)
    form_name = db.Column(db.Text())

    plant_traits = db.relationship("PlantTrait", backref="growth_form_raunkiaer")

    @staticmethod
    def migrate():
        with open('app/data-migrate/plant_traits.json') as taxonomy_file:
            data = json.load(taxonomy_file)
            species = data["PlantTrait"]
            growth_forms = species["GrowthFormRaunkiaer"]

            for form in growth_forms:
                i = GrowthFormRaunkiaer.query.filter_by(form_name=form['form_name']).first()
                if i is None:
                    i = GrowthFormRaunkiaer()

                i.form_name = form['form_name']

                db.session.add(i)
                db.session.commit()

    def __repr__(self):
        return '<Growth Form Raunkiaer %r>' % self.id

class ReproductiveRepetition(db.Model):
    __tablename__ = 'reproductive_repetition'
    id = db.Column(db.Integer, primary_key=True, index=True)
    repetition_name = db.Column(db.Text())

    plant_traits = db.relationship("PlantTrait", backref="reproductive_repetition")

    @staticmethod
    def migrate():
        with open('app/data-migrate/plant_traits.json') as d_file:
            data = json.load(d_file)
            json_data = data["PlantTrait"]
            nodes = json_data["ReproductiveRepetition"]

            for node in nodes:

                i = ReproductiveRepetition.query.filter_by(repetition_name=node['repetition_name']).first()
                if i is None:
                    i = ReproductiveRepetition()

                i.repetition_name = node['repetition_name']

                db.session.add(i)
                db.session.commit()

    def __repr__(self):
        return '<Reproductive Repetition %r>' % self.id

class DicotMonoc(db.Model):
    __tablename__ = 'dicot_monoc'
    id = db.Column(db.Integer, primary_key=True)
    dicot_monoc_name = db.Column(db.String(64), index=True)

    plant_traits = db.relationship("PlantTrait", backref="dicot_monoc")

    @staticmethod
    def migrate():
        with open('app/data-migrate/plant_traits.json') as d_file:
            data = json.load(d_file)
            json_data = data["PlantTrait"]
            nodes = json_data["DicotMonoc"]

            for node in nodes:
                i = DicotMonoc.query.filter_by(dicot_monoc_name=node['dicot_monoc_name']).first()
                if i is None:
                    i = DicotMonoc()

                i.dicot_monoc_name = node['dicot_monoc_name']

                db.session.add(i)
                db.session.commit()

    def __repr__(self):
        return '<Dicot Monoc %r>' % self.id

class AngioGymno(db.Model):
    __tablename__ = 'angio_gymno'
    id = db.Column(db.Integer, primary_key=True)
    angio_gymno_name = db.Column(db.String(64), index=True)

    plant_traits = db.relationship("PlantTrait", backref="angio_gymno")

    @staticmethod
    def migrate():
        with open('app/data-migrate/plant_traits.json') as d_file:
            data = json.load(d_file)
            json_data = data["PlantTrait"]
            nodes = json_data["AngioGymno"]

            for node in nodes:
                i = AngioGymno.query.filter_by(angio_gymno_name=node['angio_gymno_name']).first()
                if i is None:
                    i = AngioGymno()

                i.angio_gymno_name = node['angio_gymno_name']

                db.session.add(i)
                db.session.commit()

    def __repr__(self):
        return '<Angio Gymno %r>' % self.id
''' End Meta Tables for Plant Traits '''

''' Meta Tables for Publication/Additional Source '''
class SourceType(db.Model):
    __tablename__ = 'source_types'
    id = db.Column(db.Integer, primary_key=True)
    source_name = db.Column(db.String(64), index=True)
    source_description = db.Column(db.Text())
    database_id = db.Column(db.Integer, db.ForeignKey('databases.id'))

    publications = db.relationship("Publication", backref="source_type")
    additional_sources = db.relationship("AdditionalSource", backref="source_type")

    @staticmethod
    def migrate():
        with open('app/data-migrate/publications.json') as d_file:
            data = json.load(d_file)
            json_data = data["Publication"]
            nodes = json_data["SourceType"]

            for node in nodes:
                i = SourceType.query.filter_by(source_name=node['source_name']).first()
                if i is None:
                    i = SourceType()

                i.source_name = node['source_name']
                i.source_description = node['source_description']

                db.session.add(i)
                db.session.commit()

    def __repr__(self):
        return '<Source Type %r>' % self.id

class Database(db.Model):
    __tablename__ = 'databases'
    id = db.Column(db.Integer, primary_key=True)
    database_name = db.Column(db.String(64), index=True)
    database_description = db.Column(db.Text())

    sources = db.relationship("SourceType", backref="database")

    @staticmethod
    def migrate():
        with open('app/data-migrate/publications.json') as d_file:
            data = json.load(d_file)
            json_data = data["Publication"]
            nodes = json_data["Database"]

            for node in nodes:
                i = Database.query.filter_by(database_name=node['database_name']).first()
                if i is None:
                    i = Database()

                i.database_name = node['database_name']
                i.database_description = node['database_description']

                db.session.add(i)
                db.session.commit()

    def __repr__(self):
        return '<Database %r>' % self.id

class Purpose(db.Model):
    __tablename__ = 'purposes'
    id = db.Column(db.Integer, primary_key=True)
    purpose_name = db.Column(db.String(64), index=True)
    purpose_description = db.Column(db.Text())

    publications = db.relationship("Publication", backref="purpose")

    @staticmethod
    def migrate():
        with open('app/data-migrate/publications.json') as d_file:
            data = json.load(d_file)
            json_data = data["Publication"]
            nodes = json_data["Purpose"]

            for node in nodes:
                i = Purpose.query.filter_by(purpose_name=node['purpose_name']).first()
                if i is None:
                    i = Purpose()

                i.purpose_name = node['purpose_name']
                i.purpose_description = node['purpose_description']

                db.session.add(i)
                db.session.commit()

    def __repr__(self):
        return '<Purpose %r>' % self.id

publication_purposes = db.Table('publication_purposes', db.Model.metadata,
    db.Column('id', db.Integer, primary_key=True),
    db.Column('purpose_id', db.Integer, db.ForeignKey('purposes.id')),
    db.Column('publication_id', db.Integer, db.ForeignKey('publications.id'))
)

class MissingData(db.Model):
    __tablename__ = 'missing_data'
    id = db.Column(db.Integer, primary_key=True)
    missing_code = db.Column(db.String(5), index=True)
    missing_description = db.Column(db.Text())

    publications = db.relationship("Publication", backref="missing_data")

    @staticmethod
    def migrate():
        with open('app/data-migrate/publications.json') as d_file:
            data = json.load(d_file)
            json_data = data["Publication"]
            nodes = json_data["MissingData"]

            for node in nodes:
                i = MissingData.query.filter_by(missing_code=node['missing_code']).first()
                if i is None:
                    i = MissingData()

                i.missing_code = node['missing_code']
                i.missing_description = node['missing_description']

                db.session.add(i)
                db.session.commit()

    def __repr__(self):
        return '<Missing Data %r>' % self.id


publication_missing_data = db.Table('publication_missing_data', db.Model.metadata,
    db.Column('id', db.Integer, primary_key=True),
    db.Column('missing_data_id', db.Integer, db.ForeignKey('missing_data.id')),
    db.Column('publication_id', db.Integer, db.ForeignKey('publications.id'))
)

''' End Meta Tables for Publication/Additional Source '''

''' Meta Tables for Author Contact '''
class ContentEmail(db.Model):
    __tablename__ = 'content_email'
    id = db.Column(db.Integer, primary_key=True)
    content_code = db.Column(db.String(5), index=True)
    content_description = db.Column(db.Text())

    author_contacts = db.relationship("AuthorContact", backref="content_email")

    @staticmethod
    def migrate():
        with open('app/data-migrate/author_contacts.json') as d_file:
            data = json.load(d_file)
            json_data = data["AuthorContact"]
            nodes = json_data["ContentEmail"]

            for node in nodes:
                i = ContentEmail.query.filter_by(content_code=node['content_code']).first()
                if i is None:
                    i = ContentEmail()

                i.content_code = node['content_code']
                i.content_description = node['content_description']

                db.session.add(i)
                db.session.commit()

    def __repr__(self):
        return '<Missing Data %r>' % self.id
''' End Meta Tables for Author Contact '''

''' Meta Tables for Population '''
class Ecoregion(db.Model):
    __tablename__ = 'ecoregions'
    id = db.Column(db.Integer, primary_key=True)
    ecoregion_code = db.Column(db.String(5), index=True)
    ecoregion_description = db.Column(db.Text())

    populations = db.relationship("Population", backref="ecoregion")

    @staticmethod
    def migrate():
        with open('app/data-migrate/populations.json') as d_file:
            data = json.load(d_file)
            json_data = data["Population"]
            nodes = json_data["Ecoregion"]

            for node in nodes:
                i = Ecoregion.query.filter_by(ecoregion_code=node['ecoregion_code']).first()
                if i is None:
                    i = Ecoregion()

                i.ecoregion_code = node['ecoregion_code']
                i.ecoregion_description = node['ecoregion_description']

                db.session.add(i)
                db.session.commit()

    def __repr__(self):
        return '<Ecoregion %r>' % self.id

class Continent(db.Model):
    __tablename__ = 'continents'
    id = db.Column(db.Integer, primary_key=True)
    continent_name = db.Column(db.String(64), index=True)   
    
    populations = db.relationship("Population", backref="continent")

    @staticmethod
    def migrate():
        with open('app/data-migrate/populations.json') as d_file:
            data = json.load(d_file)
            json_data = data["Population"]
            nodes = json_data["Continent"]

            for node in nodes:
                i = Continent.query.filter_by(continent_name=node['continent_name']).first()
                if i is None:
                    i = Continent()

                i.continent_name = node['continent_name']

                db.session.add(i)
                db.session.commit()

    def __repr__(self):
        return '<Continent %r>' % self.id
''' End Meta Tables for Population '''

''' Meta Tables for Stage Type '''
class StageTypeClass(db.Model):
    __tablename__ = 'stage_type_classes'
    id = db.Column(db.Integer, primary_key=True)
    type_class = db.Column(db.String(64), index=True)

    stage_types = db.relationship("StageType", backref="stage_type_class")

    @staticmethod
    def migrate():
        with open('app/data-migrate/stage_types.json') as d_file:
            data = json.load(d_file)
            json_data = data["StageType"]
            nodes = json_data["StageTypeClass"]

            for node in nodes:
                i = StageTypeClass.query.filter_by(type_class=node['type_class']).first()
                if i is None:
                    i = StageTypeClass()

                i.type_class = node['type_class']

                db.session.add(i)
                db.session.commit()

    def __repr__(self):
        return '<Stage Type Class %r>' % self.id
''' End Meta Tables for Stage Type '''

''' Meta Tables for MatrixValue '''
class TransitionType(db.Model):
    __tablename__ = 'transition_types'
    id = db.Column(db.Integer, primary_key=True)
    trans_code = db.Column(db.String(64), index=True)
    trans_description = db.Column(db.Text())

    matrix_values = db.relationship("MatrixValue", backref="transition_type")

    @staticmethod
    def migrate():
        with open('app/data-migrate/matrix_values.json') as d_file:
            data = json.load(d_file)
            json_data = data["MatrixValue"]
            nodes = json_data["TransitionType"]

            for node in nodes:
                i = TransitionType.query.filter_by(trans_code=node['trans_code']).first()
                if i is None:
                    i = TransitionType()

                i.trans_code = node['trans_code']
                i.trans_description = node['trans_description']

                db.session.add(i)
                db.session.commit()

    def __repr__(self):
        return '<Transition Type %r>' % self.id
''' End Meta Tables for MatrixValue '''

''' Meta Tables for Matrix '''
class MatrixComposition(db.Model):
    __tablename__ = 'matrix_compositions'
    id = db.Column(db.Integer, primary_key=True)
    comp_name = db.Column(db.String(64))

    matrices = db.relationship("Matrix", backref="matrix_composition")

    @staticmethod
    def migrate():
        with open('app/data-migrate/matrices.json') as d_file:
            data = json.load(d_file)
            json_data = data["Matrix"]
            nodes = json_data["MatrixComposition"]

            for node in nodes:
                i = MatrixComposition.query.filter_by(comp_name=node['comp_name']).first()
                if i is None:
                    i = MatrixComposition()

                i.comp_name = node['comp_name']

                db.session.add(i)
                db.session.commit()

    def __repr__(self):
        return '<Matrix Composition %r>' % self.id

class Season(db.Model):
    __tablename__ = 'seasons'
    id = db.Column(db.Integer, primary_key=True)
    season_id = db.Column(db.Integer())
    season_name = db.Column(db.String(64), index=True)

    matrices = db.relationship("Matrix", backref="Matrix.matrix_start_season_id",primaryjoin="Season.id==Matrix.matrix_end_season_id", lazy="dynamic")

    @staticmethod
    def migrate():
        with open('app/data-migrate/matrices.json') as d_file:
            data = json.load(d_file)
            json_data = data["Matrix"]
            nodes = json_data["Season"]

            for node in nodes:
                i = Season.query.filter_by(season_id=node['season_id']).first()
                if i is None:
                    i = Season()

                i.season_id = node['season_id']
                i.season_name = node['season_name']

                db.session.add(i)
                db.session.commit()

    def __repr__(self):
        return '<Season %r>' % self.id

class StudiedSex(db.Model):
    __tablename__ = 'studied_sex'
    id = db.Column(db.Integer, primary_key=True)
    sex_code = db.Column(db.String(5), index=True)
    sex_description = db.Column(db.Text())

    matrices = db.relationship("Matrix", backref="studied_sex")

    @staticmethod
    def migrate():
        with open('app/data-migrate/matrices.json') as d_file:
            data = json.load(d_file)
            json_data = data["Matrix"]
            nodes = json_data["StudiedSex"]

            for node in nodes:
                i = StudiedSex.query.filter_by(sex_code=node['sex_code']).first()
                if i is None:
                    i = StudiedSex()

                i.sex_code = node['sex_code']
                i.sex_description = node['sex_description']

                db.session.add(i)
                db.session.commit()

    def __repr__(self):
        return '<Studied Sex %r>' % self.id

class Captivity(db.Model):
    __tablename__ = 'captivities'
    id = db.Column(db.Integer, primary_key=True)
    cap_code = db.Column(db.String(5), index=True)
    cap_description = db.Column(db.Text())

    matrices = db.relationship("Matrix", backref="captivities")

    @staticmethod
    def migrate():
        with open('app/data-migrate/matrices.json') as d_file:
            data = json.load(d_file)
            json_data = data["Matrix"]
            nodes = json_data["Captivity"]

            for node in nodes:
                i = Captivity.query.filter_by(cap_code=node['cap_code']).first()
                if i is None:
                    i = Captivity()

                i.cap_code = node['cap_code']
                i.cap_description = node['cap_description']

                db.session.add(i)
                db.session.commit()

    def __repr__(self):
        return '<Captivity %r>' % self.id
''' End Meta Tables for Matrix '''

''' Meta Tables for Bussy '''
stage_class_info_bussys = db.Table('stage_class_info_bussys', db.Model.metadata,
    db.Column('id', db.Integer, primary_key=True),
    db.Column('stage_class_info_id', db.Integer, db.ForeignKey('stage_class_infos.id')),
    db.Column('bussys_id', db.Integer, db.ForeignKey('bussys.id'))
)

class VectorAvailability(db.Model):
    __tablename__ = 'vector_availabilities'
    id = db.Column(db.Integer, primary_key=True)
    availability_name = db.Column(db.String(200), index=True)

    bussys = db.relationship("Bussy", backref="vector_availabilities")

    @staticmethod
    def migrate():
        with open('app/data-migrate/bussys.json') as d_file:
            data = json.load(d_file)
            json_data = data["Bussy"]
            nodes = json_data["VectorAvailability"]

            for node in nodes:
                i = VectorAvailability.query.filter_by(availability_name=node['availability_name']).first()
                if i is None:
                    i = VectorAvailability()

                i.availability_name = node['availability_name']

                db.session.add(i)
                db.session.commit()

    def __repr__(self):
        return '<Vector Availability %r>' % self.id

class StageClassInfo(db.Model):
    __tablename__ = 'stage_class_infos'
    id = db.Column(db.Integer, primary_key=True)
    info_code = db.Column(db.String(200), index=True)
    info_description = db.Column(db.Text())

    @staticmethod
    def migrate():
        with open('app/data-migrate/bussys.json') as d_file:
            data = json.load(d_file)
            json_data = data["Bussy"]
            nodes = json_data["StageClassInfo"]

            for node in nodes:
                i = StageClassInfo.query.filter_by(info_code=node['info_code']).first()
                if i is None:
                    i = StageClassInfo()

                i.info_code = node['info_code']
                i.info_description = node['info_description']

                db.session.add(i)
                db.session.commit()

    def __repr__(self):
        return '<StageClassInfo %r>' % self.id

class Small(db.Model):
    __tablename__ = 'smalls'
    id = db.Column(db.Integer, primary_key=True)
    small_name = db.Column(db.String(200), index=True)
    small_description = db.Column(db.Text())

    bussys = db.relationship("Bussy", backref="smalls")

    @staticmethod
    def migrate():
        with open('app/data-migrate/bussys.json') as d_file:
            data = json.load(d_file)
            json_data = data["Bussy"]
            nodes = json_data["Small"]

            for node in nodes:
                i = Small.query.filter_by(small_name=node['small_name']).first()
                if i is None:
                    i = Small()

                i.small_name = node['small_name']
                i.small_description = node['small_description']

                db.session.add(i)
                db.session.commit()

    def __repr__(self):
        return '<StageClassInfo %r>' % self.id
''' End Meta Tables for Bussy '''

''' End Meta Tables '''

class Species(db.Model):
    __tablename__ = 'species'
    id = db.Column(db.Integer, primary_key=True)
    # subspecies = db.Column(db.String(64))
    species_accepted = db.Column(db.String(64))
    iucn_status_id = db.Column(db.Integer, db.ForeignKey('iucn_status.id'))
    esa_status_id = db.Column(db.Integer, db.ForeignKey('esa_statuses.id'))
    invasive_status = db.Column(db.Boolean())
    user_created = db.relationship('User', foreign_keys='Species.user_created_id') # user keys might be a problem.. or might not.. will implement and find out
    user_created_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user_modified = db.relationship('User', foreign_keys='Species.user_modified_id')
    user_modified_id = db.Column(db.Integer, db.ForeignKey('users.id'))    
    timestamp_created = db.Column(db.DateTime, default=datetime.utcnow)
    timestamp_modified = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    taxonomies = db.relationship("Taxonomy", backref="species")
    plant_traits = db.relationship("PlantTrait", backref="species")
    populations = db.relationship("Population", backref="species")
    stages = db.relationship("Stage", backref="species")

    @staticmethod
    def migrate():
        IUCNStatus.migrate()
        ESAStatus.migrate()

    def to_json(self):
        species = {
            'species_accepted': self.species_accepted,
            'taxonomy' : [taxonomy.to_json() for taxonomy in self.taxonomies][0],
            'plant_traits' : [plant_trait.to_json() for plant_trait in self.plant_traits][0],
            'populations' : [population.to_json() for population in self.populations][0]
            # 'stages' : [stage.to_json() for stage in self.stages][0]
        }
        return species


    def __repr__(self):
        return '<Species %r>' % self.id

class Taxonomy(db.Model):
    __tablename__ = 'taxonomies'
    id = db.Column(db.Integer, primary_key=True)
    species_id = db.Column(db.Integer, db.ForeignKey('species.id'))
    publication_id = db.Column(db.Integer, db.ForeignKey('publications.id'))
    species_author = db.Column(db.String(64), index=True)
    species_accepted = db.Column(db.String(64))
    authority = db.Column(db.Text())
    taxonomic_status_id = db.Column(db.Integer, db.ForeignKey('taxonomic_statuses.id'))
    tpl_version = db.Column(db.String(64)) # Currently at 1.0, which could be float, but sometimes releases are 1.0.1 etc, best as string for now?
    infraspecies_accepted = db.Column(db.String(64))
    species_epithet_accepted = db.Column(db.String(64))
    genus_accepted = db.Column(db.String(64))
    genus = db.Column(db.String(64))
    family = db.Column(db.String(64))
    tax_order = db.Column(db.String(64))
    tax_class = db.Column(db.String(64))
    phylum = db.Column(db.String(64))
    kingdom = db.Column(db.String(64))

    @staticmethod
    def migrate():
        TaxonomicStatus.migrate()

    def to_json(self):
        try:
            taxonomy = {
                'species_author' : self.species_author,
                'species_accepted' : self.species_accepted,
                'publication' : (self.publication).to_json(),
                'authority' : self.authority,
                'taxonomic_status' : self.taxonomic_status.status_name,
                'tpl_version' : self.tpl_version,
                'infraspecies_accepted' : self.infraspecies_accepted,
                'species_epithet_accepted' : self.species_epithet_accepted,
                'genus_accepted' : self.genus_accepted,
                'genus' : self.genus,
                'family' : self.family,
                'tax_order' : self.tax_order,
                'tax_class' : self.tax_class,
                'phylum' : self.phylum,
                'kingdom' : self.kingdom
            }
        except:
            taxonomy = {
                'species_author' : self.species_author,
                'species_accepted' : self.species_accepted,
                'publication' : (self.publication).to_json(),
                'authority' : self.authority,
                'tpl_version' : self.tpl_version,
                'infraspecies_accepted' : self.infraspecies_accepted,
                'species_epithet_accepted' : self.species_epithet_accepted,
                'genus_accepted' : self.genus_accepted,
                'genus' : self.genus,
                'family' : self.family,
                'tax_order' : self.tax_order,
                'tax_class' : self.tax_class,
                'phylum' : self.phylum,
                'kingdom' : self.kingdom
            }
        return taxonomy

    def __repr__(self):
        return '<Taxonomy %r>' % self.id


class PlantTrait(db.Model):
    __tablename__ = 'plant_traits'
    id = db.Column(db.Integer, primary_key=True)
    species_id = db.Column(db.Integer, db.ForeignKey('species.id'))
    max_height = db.Column(db.Float()) #This should be a double, eventually
    growth_type_id = db.Column(db.Integer, db.ForeignKey('growth_types.id'))
    growth_form_raunkiaer_id = db.Column(db.Integer, db.ForeignKey('growth_forms_raunkiaer.id'))
    reproductive_repetition_id = db.Column(db.Integer, db.ForeignKey('reproductive_repetition.id'))
    dicot_monoc_id = db.Column(db.Integer, db.ForeignKey('dicot_monoc.id'))
    angio_gymno_id = db.Column(db.Integer, db.ForeignKey('angio_gymno.id'))

    @staticmethod
    def migrate():
        GrowthType.migrate()
        GrowthFormRaunkiaer.migrate()
        ReproductiveRepetition.migrate()
        DicotMonoc.migrate()
        AngioGymno.migrate()

    def to_json(self):
        plant_trait = {
            'max_height' : self.max_height,
            'growth_type_id' : self.growth_type.type_name,
            # 'growth_form_raunkiaer' : self.growth_form_raunkiaer.form_name,
            # 'reproductive_repetition' : self.reproductive_repetition.repetition_name,
            'dicot_monoc' : self.dicot_monoc.dicot_monoc_name,
            'angio_gymno' : self.angio_gymno.angio_gymno_name
        }
        return plant_trait

    def __repr__(self):
        return '<Plant Trait %r>' % self.id

class Publication(db.Model):
    __tablename__ = 'publications'
    id = db.Column(db.Integer, primary_key=True)
    source_type_id = db.Column(db.Integer, db.ForeignKey('source_types.id'))
    authors = db.Column(db.Text()) # These appear as vectors in Judy's schema, trying to think of the best way to implement this within MySQL and Django/Flask
    editors = db.Column(db.Text())
    pub_title = db.Column(db.Text())
    journal_book_conf = db.Column(db.Text())
    year = db.Column(db.SmallInteger()) #proto
    volume = db.Column(db.Text())
    pages = db.Column(db.Text())
    publisher = db.Column(db.Text())
    city = db.Column(db.Text())
    country = db.Column(db.Text())
    institution = db.Column(db.Text())
    DOI_ISBN = db.Column(db.Text())
    name = db.Column(db.Text()) #r-generated, needs more info, probably generated in method of this model
    corresponding_author = db.Column(db.Text())
    email = db.Column(db.Text())
    purposes_id = db.Column(db.Integer, db.ForeignKey('purposes.id'))
    date_digitised = db.Column(db.DateTime(), default=datetime.now)
    embargo = db.Column(db.Date()) #nullable
    missing_data_id = db.Column(db.Integer, db.ForeignKey('missing_data.id'))
    additional_source_string = db.Column(db.Text())

    # Again, these might be problematic
    user_created = db.Column(db.Integer, db.ForeignKey('users.id'))
    user_modified = db.Column(db.Integer, db.ForeignKey('users.id'))
    timestamp_created = db.Column(db.DateTime, default=datetime.utcnow)
    timestamp_modified = db.Column(db.DateTime, default=datetime.utcnow)

    # Establishing one to many relationships between tables
    author_contacts = db.relationship("AuthorContact", backref="publication")
    additional_sources = db.relationship("AdditionalSource", backref="publication")
    populations = db.relationship("Population", backref="publication")
    stages = db.relationship("Stage", backref="publication")
    treatments = db.relationship("Treatment", backref="publication")
    taxonomies = db.relationship("Taxonomy", backref="publication")
    studies = db.relationship("Study", backref="publication")

    @staticmethod
    def migrate():
        SourceType.migrate()
        Database.migrate()
        Purpose.migrate()
        MissingData.migrate()

    def to_json(self):
        publication = {
            # 'source_type' : self.source_type.source_name,
            'authors' : self.authors,
            'editors' : self.editors,
            'pub_title' : self.pub_title,
            'journal_book_conf' : self.journal_book_conf,
            'year' : self.year,
            'volume' : self.volume,
            'pages' : self.pages,
            'publisher' : self.publisher,
            'city' : self.city,
            'country' : self.country,
            'DOI_ISBN' : self.DOI_ISBN,
            'name' : self.name,
            'corresponding_author' : self.corresponding_author,
            'email' : self.email,
            # 'purposes' : self.purposes.purpose_name,
            # 'date_digitised' : self.date_digitised,
            'embargo' : self.embargo,
            # 'missing_data' : self.missing_data.missing_code,
            'additional_source_string' : self.additional_source_string,
            # Author contacts?
            # Additional Sources?
            'populations' : url_array(self, 'populations'),   
            # 'stages' : [stage.to_json() for stage in self.stages][0]
            # 'treatments' : [treatment.to_json() for treatment in self.treatments][0]
            'taxonomies' : url_array(self, 'taxonomies'),
            'studies' : url_array(self, 'studies')
        }
        return publication


    def __repr__(self):
        return '<Publication %r>' % self.id


class Study(db.Model):
    __tablename__ = 'studies'
    id = db.Column(db.Integer, primary_key=True)
    publication_id = db.Column(db.Integer, db.ForeignKey('publications.id'))
    study_duration = db.Column(db.Integer(), index=True)
    study_start = db.Column(db.Integer())
    study_end = db.Column(db.Integer())

    matrices = db.relationship("Matrix", backref="study")
    populations = db.relationship("Population", backref="study")
    number_populations = db.Column(db.Integer()) #could verify with populations.count()

    def to_json(self):
        study = {
            'publication' : url_for('api.get_publication', id=self.publication.id,
                                  _external=False),
            'study_duration' : self.study_duration,
            'study_start' : self.study_start,
            'study_end' : self.study_end,
            'number_populations' : self.number_populations,           
            'matrices' : url_array(self, 'matrices'),
            'populations' : url_array(self, 'populations')
        }
        return study

    def __repr__(self):
        return '<Study %r>' % self.id

class AuthorContact(db.Model):
    __tablename__ = 'author_contacts'
    id = db.Column(db.Integer, primary_key=True)
    publication_id = db.Column(db.Integer, db.ForeignKey('publications.id'))
    date_contacted = db.Column(db.Date(), index=True)
    contacting_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    content_email_id = db.Column(db.Integer, db.ForeignKey('content_email.id')) #possibly many to many, probably a good idea if vector
    author_reply = db.Column(db.Text())

    @staticmethod
    def migrate():
        ContentEmail.migrate()

    def to_json(self):
        author_contact = {
            # 'publication' : self.publication, url??
            'date_contacted' : self.date_contacted,
            'contacting_user_id' : self.contacting_user_id,
            'content_email_id' : self.content_email_id,
            'author_reply' : self.author_reply,
        }
        return author_contact

    def __repr__(self):
        return '<Author Contact %r>' % self.id

class AdditionalSource(db.Model):
    __tablename__ = 'additional_sources'
    id = db.Column(db.Integer, primary_key=True)
    publication_id = db.Column(db.Integer, db.ForeignKey('publications.id'))
    source_type_id = db.Column(db.Integer, db.ForeignKey('source_types.id'))
    authors = db.Column(db.Text())
    editors = db.Column(db.Text())
    pub_title = db.Column(db.Text())
    journal_book_conf = db.Column(db.Text())
    year = db.Column(db.SmallInteger()) #proto
    volume = db.Column(db.Text())
    pages = db.Column(db.Text())
    publisher = db.Column(db.Text())
    city = db.Column(db.Text())
    country = db.Column(db.Text())
    institution = db.Column(db.Text())
    DOI_ISBN = db.Column(db.Text())
    name = db.Column(db.Text()) #r-generated, needs more info, probably to be generated in method of this model, first author in author list?
    description = db.Column(db.Text())

    def to_json(self):
        additional_source = {
            # 'publication' : self.publication, url??
            'source_type' : self.source_type.source_name,
            'contacting_user_id' : self.contacting_user_id,
            'authors' : self.authors,
            'editors' : self.editors,
            'pub_title' : self.pub_title,
            'journal_book_conf' : self.journal_book_conf,
            'year' : self.year,
            'volume' : self.volume,
            'pages' : self.pages,
            'publisher' : self.publisher,
            'city' : self.city,
            'country' : self.country,
            'institution' : self.institution,
            'DOI_ISBN' : self.DOI_ISBN,
            'name' : self.name,
            'description' : self.description
        }
        return additional_source

    def __repr__(self):
        return '<Additional Source %r>' % self.id

class Population(db.Model):
    __tablename__ = 'populations'
    id = db.Column(db.Integer, primary_key=True, index=True)
    species_id = db.Column(db.Integer, db.ForeignKey('species.id'))
    publication_id = db.Column(db.Integer, db.ForeignKey('publications.id'))
    study_id = db.Column(db.Integer, db.ForeignKey('studies.id'))
    species_author = db.Column(db.String(64))
    name = db.Column(db.Text())
    ecoregion_id = db.Column(db.Integer, db.ForeignKey('ecoregions.id'))
    #Django plugin for country, and generic python package too - we'll be just fine. Unfortunately, unless we download a CSV of this and enter into sep table, will probably be more efficient to do this outside of the database. Further thought reqd!
    country = db.Column(db.Text())
    continent_id = db.Column(db.Integer, db.ForeignKey('continents.id'))
    geometries = db.Column(db.Text()) #This needs work once i've decided wether to use Flask or Django - such good cases for both. Databases support point geometry, including altitude.

    matrices = db.relationship("Matrix", backref="population")

    def geometries_dec(self):
        geo = json.loads(self.geometries)

        lat_min = geo['lat_min']
        lat_deg = geo['lat_deg']
        lat_sec = geo['lat_sec']
        lat_ns = geo['lat_ns']
        lon_min = geo['lon_min']
        lon_deg = geo['lon_deg']
        lon_sec = geo['lon_sec']
        lat_we = geo['lat_we']
        altitude = geo['altitude']

        try:
            decimal_lat = (float(lat_deg) + (float(lat_min) * 1/60) + (float(lat_sec) * 1/60 * 1/60))
            decimal_lon = (float(lon_deg) + (float(lon_min) * 1/60) + (float(lon_sec) * 1/60 * 1/60))
            altitude = float(altitude)
        except:
            decimal_lat = 'NA'
            decimal_lon = 'NA'
            altitude = 'NA'

        geometries = {"latitude" : decimal_lat, "longitude" : decimal_lon, "altitude" : altitude}
        return geometries


    def to_json(self):
        try:
            population = {
                'species' : url_for('api.get_species', id=self.species.id,
                                      _external=False),
                'publication' : url_for('api.get_publication', id=self.publication.id,
                                      _external=False),
                'study' : self.study.to_json(),
                'species_author' : self.species_author,
                'name' : self.name,
                'ecoregion' : self.ecoregion.ecoregion_code,
                'country' : self.country,
                'continent' : self.continent.continent_name,
                'geometries' : self.geometries_dec()

                # Matrices?
            }
        except: 
            population = {
            'species' : url_for('api.get_species', id=self.species.id,
                                  _external=False),
            'publication' : url_for('api.get_publication', id=self.publication.id,
                                  _external=False),
            'study' : self.study.to_json(),
            'species_author' : self.species_author,
            'name' : self.name,
            'country' : self.country,
            'geometries' : self.geometries_dec()

            # Matrices?
        }
        return population
        return population

    @staticmethod
    def migrate():
        Ecoregion.migrate()
        Continent.migrate()

    def __repr__(self):
        return '<Population %r>' % self.id

class Stage(db.Model):
    __tablename__ = 'stages'
    id = db.Column(db.Integer, primary_key=True, index=True)
    species_id = db.Column(db.Integer, db.ForeignKey('species.id'))
    publication_id = db.Column(db.Integer, db.ForeignKey('publications.id'))
    stage_type_id = db.Column(db.Integer, db.ForeignKey('stage_types.id')) 
    name = db.Column(db.Text()) #Schema says 'author's', need clarification - author's name possibly, according to protocol?

    matrix_stages = db.relationship("MatrixStage", backref="stage")

    def to_json(self):
        stage = {
            # species : self.species url?
            # publication : self.publication url?
            # stage_type: self.stage_type url?
            'name' : self.name

            # matrix_stages ?
        }
        return stage

    def __repr__(self):
        return '<Stage %r>' % self.id

class StageType(db.Model):
    __tablename__ = 'stage_types'
    id = db.Column(db.Integer, primary_key=True, index=True)
    type_name = db.Column(db.Text())
    type_class_id = db.Column(db.Integer, db.ForeignKey('stage_type_classes.id'))

    stages = db.relationship("Stage", backref="stage_types")

    def to_json(self):
        stage_type = {
            'type_name' : self.type_name,
            'type_class' : self.type_class.type_class

            # Stages?
        }
        return stage_type

    @staticmethod
    def migrate():
        StageTypeClass.migrate()

    def __repr__(self):
        return '<Stage Type %r>' % self.id


#Ignore this one for a while, not enough data just yet
class Treatment(db.Model):
    __tablename__ = 'treatments'
    id = db.Column(db.Integer, primary_key=True, index=True)
    publication_id = db.Column(db.Integer, db.ForeignKey('publications.id'))
    treatment_type_id = db.Column(db.Integer, db.ForeignKey('treatment_types.id'))
    name = db.Column(db.Text()) #Schema says 'author's', need clarification - author's name possibly, according to protocol?
    description = db.Column(db.Text())

    # matrices = db.relationship("Matrix", backref="treatment")

    def __repr__(self):
        return '<Treatment %r>' % self.id

class TreatmentType(db.Model):
    __tablename__ = 'treatment_types'
    id = db.Column(db.Integer, primary_key=True, index=True)
    type_name = db.Column(db.Text())
    
    matrices = db.relationship("Matrix", backref="treatment")
    # treatments = db.relationship("Treatment", backref="treatment_types")
    

    @staticmethod
    def migrate():
        with open('app/data-migrate/matrices.json') as d_file:
            data = json.load(d_file)
            json_data = data["Matrix"]
            nodes = json_data["TreatmentType"]

            for node in nodes:
                i = TreatmentType.query.filter_by(type_name=node['type_name']).first()
                if i is None:
                    i = TreatmentType()

                i.type_name = node['type_name']

                db.session.add(i)
                db.session.commit()

    def to_json(self):
        treatment_type = {
            'type_name' : self.type_name,

            # Matrices?
        }
        return treatment_type


    def __repr__(self):
        return '<Treatment Type %r>' % self.id

class MatrixStage(db.Model):
    __tablename__ = 'matrix_stages'
    id = db.Column(db.Integer, primary_key=True)
    stage_order = db.Column(db.SmallInteger())
    stage_id = db.Column(db.Integer, db.ForeignKey('stages.id'))

    matrix_id = db.Column(db.Integer, db.ForeignKey('matrices.id'))

    def to_json(self):
        matrix_stage = {
            'stage_order' : self.stage_order,
            'stage_id' : self.stage_id
            # 'matrix' : self.matrix.id (url?)
        }
        return matrix_stage

    def __repr__(self):
        return '<Matrix Stage %r>' % self.id

class MatrixValue(db.Model):
    __tablename__ = 'matrix_values'
    id = db.Column(db.Integer, primary_key=True)
    column_number = db.Column(db.SmallInteger())
    row_number = db.Column(db.SmallInteger())
    transition_type_id = db.Column(db.Integer, db.ForeignKey('transition_types.id'))
    value = db.Column(db.Float())

    matrix_id = db.Column(db.Integer, db.ForeignKey('matrices.id'))

    @staticmethod
    def migrate():
        TransitionType.migrate()

    def to_json(self):
        matrix_value = {
            'column_number' : self.column_number,
            'row_number' : self.row_number,
            'transition_type' : self.transition_type.trans_code,
            'value' : self.value
            # 'matrix' : self.matrix.id (url?)
        }
        return matrix_value

    def __repr__(self):
        return '<Matrix Value %r>' % self.id

class Matrix(db.Model):
    __tablename__ = 'matrices'
    id = db.Column(db.Integer, primary_key=True)
    population_id = db.Column(db.Integer, db.ForeignKey('populations.id'))
    treatment_id = db.Column(db.Integer, db.ForeignKey('treatment_types.id'))
    matrix_split = db.Column(db.Boolean())
    matrix_composition_id = db.Column(db.Integer, db.ForeignKey('matrix_compositions.id'))
    survival_issue = db.Column(db.Float())
    n_intervals = db.Column(db.SmallInteger()) # Danny/Jenni/Dave, what are these? Schema says, "Number of transition intervals represented in the matrix - should only be >1 for mean matrices", so 0 or 1 or more? Can it be a float, ie 0.8?
    periodicity = db.Column(db.String(64))
    # relative = db.Column(db.Boolean()) --> in schema with no description, must confirm with Judy what this relates to, any below?
    matrix_criteria_size = db.Column(db.Boolean())
    matrix_criteria_ontogeny = db.Column(db.Boolean())
    matrix_criteria_age = db.Column(db.Boolean())
    study_id = db.Column(db.Integer, db.ForeignKey('studies.id'))
    matrix_start = db.Column(db.String(64)) # These will include month, day, etc. Create method to return these - matrix_start.day() matrix_start.year() etc
    matrix_end = db.Column(db.String(64)) # These will include month, day, etc. Create method to return these - matrix_start.day() matrix_start.year() etc
    matrix_start_season_id = db.Column(db.Integer, db.ForeignKey('seasons.id')) # Proto says season used as described in manuscript, maybe not safe to derive this from latdeg, country, date
    matrix_start_season = db.relationship('Season', foreign_keys='Matrix.matrix_start_season_id')
    matrix_end_season_id = db.Column(db.Integer, db.ForeignKey('seasons.id')) # Proto says season used as described in manuscript, maybe not safe to derive this from latdeg, country, date
    matrix_end_season = db.relationship('Season', foreign_keys='Matrix.matrix_end_season_id')
    matrix_fec = db.Column(db.Boolean())
    matrix_a_string = db.Column(db.Text())
    matrix_class_string = db.Column(db.Text())
    n_plots = db.Column(db.SmallInteger()) # Danny/Jenni/Dave, will need your help with plots too - not quite sure what they are.
    plot_size = db.Column(db.Float()) # Schema states, 'R convert to m^2'
    n_individuals = db.Column(db.Integer()) # Schema states, 'total number of individuals observed'
    studied_sex_id = db.Column(db.Integer, db.ForeignKey('studied_sex.id'))
    captivity_id = db.Column(db.Integer, db.ForeignKey('captivities.id'))
    matrix_dimension = db.Column(db.Integer()) # dimension of matrix population A   
    observations = db.Column(db.Text())

    intervals = db.relationship("Interval", backref="matrix")
    matrix_values = db.relationship("MatrixValue", backref="matrix")
    matrix_stages = db.relationship("MatrixStage", backref="matrix")
    bussys = db.relationship("Bussy", backref="matrix")

    @staticmethod
    def migrate():
        MatrixComposition.migrate()
        Season.migrate()
        StudiedSex.migrate()
        Captivity.migrate()

    def to_json(self):
        try:
            matrix = {
                'population' : url_for('api.get_population', id=self.population.id,
                                  _external=False),
                'study' : url_for('api.get_study', id=self.study.id,
                                  _external=False),
                'treatment' : self.treatment.type_name,
                'matrix_split' : self.matrix_split,
                'matrix_composition' : self.matrix_composition.comp_name,
                'survival_issue' : self.survival_issue,
                'n_intervals' : self.n_intervals,
                'periodicity' : self.periodicity,
                'matrix_criteria_size' : self.matrix_criteria_size,
                'matrix_criteria_ontogeny' : self.matrix_criteria_ontogeny,
                'matrix_criteria_age' : self.matrix_criteria_age,
                'matrix_start' : self.matrix_start,
                'matrix_end' : self.matrix_end,
                'matrix_start_season' : self.matrix_start_season.season_name,
                'matrix_end_season' : self.matrix_end_season.season_name,
                'matrix_fec' : self.matrix_fec,
                'matrix_a_string' : self.matrix_a_string,
                'matrix_class_string' : self.matrix_class_string,
                'n_plots' : self.n_plots,
                'plot_size' : self.plot_size,
                'studied_sex' : self.studied_sex.sex_code,
                'captivity' : self.captivity.cap_code,
                'matrix_dimension' : self.matrix_dimension,
                'observations' : self.observations
                
                # Intervals?
                # Matrix Values?
                # Matrix Stages?
                # Stages?
                # Bussys?
            }
        except:
            # Without seasons
            matrix = {
                'population' : url_for('api.get_population', id=self.population.id,
                                  _external=False),
                'study' : url_for('api.get_study', id=self.study.id,
                                  _external=False),
                'treatment' : self.treatment.type_name,
                'matrix_split' : self.matrix_split,
                'matrix_composition' : self.matrix_composition.comp_name,
                'survival_issue' : self.survival_issue,
                'n_intervals' : self.n_intervals,
                'periodicity' : self.periodicity,
                'matrix_criteria_size' : self.matrix_criteria_size,
                'matrix_criteria_ontogeny' : self.matrix_criteria_ontogeny,
                'matrix_criteria_age' : self.matrix_criteria_age,
                'matrix_start' : self.matrix_start,
                'matrix_end' : self.matrix_end,
                'matrix_start_season' : None,
                'matrix_end_season' : None,
                'matrix_fec' : self.matrix_fec,
                'matrix_a_string' : self.matrix_a_string,
                'matrix_class_string' : self.matrix_class_string,
                'n_plots' : self.n_plots,
                'plot_size' : self.plot_size,
                # 'studied_sex' : self.studied_sex.sex_code,
                'captivity' : None,
                'matrix_dimension' : self.matrix_dimension,
                'observations' : self.observations
                
                # Intervals?
                # Matrix Values?
                # Matrix Stages?
                # Stages?
                # Bussys?
            }
        return matrix

    def __repr__(self):
        return '<Matrix %r>' % self.id

''' This table only applies to mean matrices, to identify the intervals that the mean values are derived from '''
class Interval(db.Model):
    __tablename__ = 'intervals'
    id = db.Column(db.Integer, primary_key=True)
    matrix_id = db.Column(db.Integer, db.ForeignKey('matrices.id'))
    interval_order = db.Column(db.Integer())
    interval_start = db.Column(db.Date())
    interval_end = db.Column(db.Date())

    def to_json(self):
        interval = {
            # 'matrix' : self.matrix.id (url?)
            'interval_order' : self.interval_order,
            'interval_start' : self.interval_start,
            'interval_end' : self.interval_end
        }
        return interval

    def __repr__(self):
        return '<Interval %r>' % self.id

''' Secret & Important Bussy Stuff '''
class Bussy(db.Model):
    __tablename__ = 'bussys'
    id = db.Column(db.Integer, primary_key=True)
    matrix_id = db.Column(db.Integer, db.ForeignKey('matrices.id'), index=True)
    vector_str = db.Column(db.Text())
    vector_present = db.Column(db.Boolean())
    total_pop_no = db.Column(db.Integer())
    vector_availablility_id = db.Column(db.Integer, db.ForeignKey('vector_availabilities.id'))
    stage_class_info = db.relationship('StageClassInfo', secondary=stage_class_info_bussys, backref=db.backref('bussys', lazy='dynamic')) 
    availability_notes = db.Column(db.Text())
    population_info = db.Column(db.Text())
    sampled_entire = db.Column(db.Text())
    small_id = db.Column(db.Integer, db.ForeignKey('smalls.id'))
    private = db.Column(db.Boolean(), default=True)

    @staticmethod
    def migrate():
        VectorAvailability.migrate()
        StageClassInfo.migrate()
        Small.migrate()

    def to_json(self):
        bussy = {
            # 'matrix' : self.matrix.id (url?)
            'vector_str' : self.vector_str,
            'interval_start' : self.interval_start,
            'vector_present' : self.vector_present,
            'total_pop_no' : self.total_pop_no,
            'vector_availablility' : self.vector_availablility.availability_name,
            'availability_notes' : self.availability_notes,
            'population_info' : self.population_info,
            'sampled_entire' : self.sampled_entire,
            'small' : self.small_name,
            'private' : self.private

            # Stage Class Info?
        }
        return bussy

    def __repr__(self):
        return '<Bussy %r>' % self.id

def url_array(self, string):
    if string == 'populations':
        population_urls = []
        for population in self.populations:
            url = url_for('api.get_population', id=population.id,
                                  _external=False)
            population_urls.append(url)
        return population_urls

    elif string == 'taxonomies':
        taxonomy_urls = []
        for taxonomy in self.taxonomies:
            url = url_for('api.get_taxonomy', id=taxonomy.id,
                                  _external=False)
            taxonomy_urls.append(url)
        return taxonomy_urls
    elif string == 'studies':
        study_urls = []
        for study in self.studies:
            url = url_for('api.get_study', id=study.id,
                                  _external=False)
            study_urls.append(url)
        return study_urls
    elif string == 'matrices':
        matrix_urls = []
        for matrix in self.matrices:
            url = url_for('api.get_matrix', id=matrix.id,
                                  _external=False)
            matrix_urls.append(url)
        return matrix_urls



