from datetime import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from markdown import markdown
import bleach
from flask import current_app, request, url_for
from flask.ext.login import UserMixin, AnonymousUserMixin
from app.exceptions import ValidationError
from . import db, login_manager


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
            'url': url_for('api.get_post', id=self.id, _external=True),
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

    def __repr__(self):
        return '<IUCN Status %r>' % self.status_code

class ESAStatus(db.Model):
    __tablename__ = 'esa_statuses'
    id = db.Column(db.Integer, primary_key=True)
    status_code = db.Column(db.String(64), index=True)
    status_name = db.Column(db.String(64))
    status_description = db.Column(db.Text())

    species = db.relationship("Species", backref="esa_status")

    def __repr__(self):
        return '<ESA Status %r>' % self.status_code
''' End Meta Tables for Species '''

''' Meta Tables for Taxonomy '''
class TaxonomicStatus(db.Model):
    __tablename__ = 'taxonomic_statuses'
    id = db.Column(db.Integer, primary_key=True)
    status_name = db.Column(db.String(64), index=True)
    status_description = db.Column(db.Text())

    taxonomies = db.relationship("Taxonomy", backref="taxonomic_status")

    def __repr__(self):
        return '<Taxonomic Status %r>' % self.id
''' End Meta Tables for Taxonomy '''

''' Meta Tables for Plant Traits '''
class GrowthType(db.Model):
    __tablename__ = 'growth_types'
    id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(64), index=True)

    plant_traits = db.relationship("PlantTrait", backref="growth_type")

    def __repr__(self):
        return '<Growth Type %r>' % self.type_name

class GrowthFormRaunkiaer(db.Model):
    __tablename__ = 'growth_forms_raunkiaer'
    id = db.Column(db.Integer, primary_key=True, index=True)
    form_name = db.Column(db.Text())

    plant_traits = db.relationship("PlantTrait", backref="growth_form_raunkiaer")

    def __repr__(self):
        return '<Growth Form Raunkiaer %r>' % self.form_name

class ReproductiveRepetition(db.Model):
    __tablename__ = 'reproductive_repetition'
    id = db.Column(db.Integer, primary_key=True, index=True)
    repetition_name = db.Column(db.Text())

    plant_traits = db.relationship("PlantTrait", backref="reproductive_repetition")

    def __repr__(self):
        return '<Reproductive Repetition %r>' % self.repetiton_name

class DicotMonoc(db.Model):
    __tablename__ = 'dicot_monoc'
    id = db.Column(db.Integer, primary_key=True)
    dicot_monoc_name = db.Column(db.String(64), index=True)

    plant_traits = db.relationship("PlantTrait", backref="dicot_monoc")

    def __repr__(self):
        return '<Dicot Monoc %r>' % self.dicot_monoc_name

class AngioGymno(db.Model):
    __tablename__ = 'angio_gymno'
    id = db.Column(db.Integer, primary_key=True)
    angio_gymno_name = db.Column(db.String(64), index=True)

    plant_traits = db.relationship("PlantTrait", backref="angio_gymno")

    def __repr__(self):
        return '<Angio Gymno %r>' % self.angio_gymno
''' End Meta Tables for Plant Traits '''

''' Meta Tables for Publication/Additional Source '''
class SourceType(db.Model):
    __tablename__ = 'source_types'
    id = db.Column(db.Integer, primary_key=True)
    source_name = db.Column(db.String(64), index=True)
    source_description = db.Column(db.Text())

    publications = db.relationship("Publication", backref="source_type")
    additional_sources = db.relationship("AdditionalSource", backref="source_type")

    def __repr__(self):
        return '<Source Type %r>' % self.source_name

class Purpose(db.Model):
    __tablename__ = 'purposes'
    id = db.Column(db.Integer, primary_key=True)
    purpose_name = db.Column(db.String(64), index=True)
    purpose_description = db.Column(db.Text())

    publications = db.relationship("Publication", backref="purpose")

    def __repr__(self):
        return '<Purpose %r>' % self.purpose_name

class MissingData(db.Model):
    __tablename__ = 'missing_data'
    id = db.Column(db.Integer, primary_key=True)
    missing_code = db.Column(db.String(5), index=True)
    missing_description = db.Column(db.Text())

    publications = db.relationship("Publication", backref="missing_data")

    def __repr__(self):
        return '<Missing Data %r>' % self.missing_code
''' End Meta Tables for Publication/Additional Source '''

''' Meta Tables for Author Contact '''
class ContentEmail(db.Model):
    __tablename__ = 'content_email'
    id = db.Column(db.Integer, primary_key=True)
    content_code = db.Column(db.String(5), index=True)
    content_description = db.Column(db.Text())

    author_contacts = db.relationship("AuthorContact", backref="content_email")

    def __repr__(self):
        return '<Missing Data %r>' % self.content_code
''' End Meta Tables for Author Contact '''

''' Meta Tables for Population '''
class Ecoregion(db.Model):
    __tablename__ = 'ecoregions'
    id = db.Column(db.Integer, primary_key=True)
    ecoregion_code = db.Column(db.String(5), index=True)
    ecoregion_description = db.Column(db.Text())

    populations = db.relationship("Population", backref="ecoregion")

    def __repr__(self):
        return '<Ecoregion %r>' % self.ecoregion_code

class Continent(db.Model):
    __tablename__ = 'continents'
    id = db.Column(db.Integer, primary_key=True)
    continent_name = db.Column(db.String(64), index=True)   
    
    populations = db.relationship("Population", backref="continent")

    def __repr__(self):
        return '<Continent %r>' % self.continent_name
''' End Meta Tables for Population '''

''' Meta Tables for Stage Type '''
class StageTypeClass(db.Model):
    __tablename__ = 'stage_type_classes'
    id = db.Column(db.Integer, primary_key=True)
    type_class = db.Column(db.String(64), index=True)

    stage_types = db.relationship("StageType", backref="stage_type_class")

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

    def __repr__(self):
        return '<Transition Type %r>' % self.id
''' End Meta Tables for MatrixValue '''

''' Meta Tables for Matrix '''
class MatrixComposition(db.Model):
    __tablename__ = 'matrix_compositions'
    id = db.Column(db.Integer, primary_key=True)
    comp_name = db.Column(db.String(64))

    matrices = db.relationship("Matrix", backref="matrix_composition")

    def __repr__(self):
        return '<Matrix Composition %r>' % self.id

class Periodicity(db.Model):
    __tablename__ = 'periodicities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)

    matrices = db.relationship("Matrix", backref="periodicity")

    def __repr__(self):
        return '<Periodicity %r>' % self.id

class Season(db.Model):
    __tablename__ = 'seasons'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)

    # matrices = db.relationship("Matrix", backref="season")
    matrices = db.relationship("Matrix", backref="Matrix.matrix_start_season_id",primaryjoin="Season.id==Matrix.matrix_end_season_id", lazy="dynamic")

    def __repr__(self):
        return '<Season %r>' % self.id

class StudiedSex(db.Model):
    __tablename__ = 'studied_sex'
    id = db.Column(db.Integer, primary_key=True)
    sex_code = db.Column(db.String(5), index=True)
    sex_description = db.Column(db.Text())

    matrices = db.relationship("Matrix", backref="studied_sex")

    def __repr__(self):
        return '<Studied Sex %r>' % self.id

class Captivity(db.Model):
    __tablename__ = 'captivities'
    id = db.Column(db.Integer, primary_key=True)
    cap_code = db.Column(db.String(5), index=True)
    cap_description = db.Column(db.Text())

    matrices = db.relationship("Matrix", backref="captivities")

    def __repr__(self):
        return '<Captivity %r>' % self.id
''' End Meta Tables for Matrix '''
''' End Meta Tables '''

class Species(db.Model):
    __tablename__ = 'species'
    id = db.Column(db.Integer, primary_key=True)
    # subspecies = db.Column(db.String(64))
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

    def __repr__(self):
        return '<Taxonomy %r>' % self.species_author


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
    date_digitised = db.Column(db.Date(), default=datetime.utcnow)
    embargo = db.Column(db.Date()) #nullable
    missing_data_id = db.Column(db.Integer, db.ForeignKey('missing_data.id'))

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

    def __repr__(self):
        return '<Publication %r>' % self.id


class Study(db.Model):
    __tablename__ = 'studies'
    id = db.Column(db.Integer, primary_key=True)
    publication_id = db.Column(db.Integer, db.ForeignKey('publications.id'))
    study_duration = db.Column(db.Integer(), index=True)
    study_start = db.Column(db.Date())
    study_end = db.Column(db.Date())

    matrices = db.relationship("Matrix", backref="study")
    populations = db.relationship("Population", backref="study")
    number_populations = db.Column(db.Integer()) #could verify with populations.count()

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

    def __repr__(self):
        return '<Stage %r>' % self.id

class StageType(db.Model):
    __tablename__ = 'stage_types'
    id = db.Column(db.Integer, primary_key=True, index=True)
    type_name = db.Column(db.Text())
    type_class_id = db.Column(db.Integer, db.ForeignKey('stage_type_classes.id'))

    stages = db.relationship("Stage", backref="stage_types")

    def __repr__(self):
        return '<Stage Type %r>' % self.id


class Treatment(db.Model):
    __tablename__ = 'treatments'
    id = db.Column(db.Integer, primary_key=True, index=True)
    publication_id = db.Column(db.Integer, db.ForeignKey('publications.id'))
    treatment_type_id = db.Column(db.Integer, db.ForeignKey('treatment_types.id'))
    name = db.Column(db.Text()) #Schema says 'author's', need clarification - author's name possibly, according to protocol?
    description = db.Column(db.Text())

    matrices = db.relationship("Matrix", backref="treatment")

    def __repr__(self):
        return '<Treatment %r>' % self.id

class TreatmentType(db.Model):
    __tablename__ = 'treatment_types'
    id = db.Column(db.Integer, primary_key=True, index=True)
    type_name = db.Column(db.Text())
    

    treatments = db.relationship("Treatment", backref="treatment_types")

    def __repr__(self):
        return '<Treatment Type %r>' % self.id

class MatrixStage(db.Model):
    __tablename__ = 'matrix_stages'
    id = db.Column(db.Integer, primary_key=True)
    stage_order = db.Column(db.SmallInteger())
    stage_id = db.Column(db.Integer, db.ForeignKey('stages.id'))

    matrix_id = db.Column(db.Integer, db.ForeignKey('matrices.id'))

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

    def __repr__(self):
        return '<Matrix Value %r>' % self.id

class Matrix(db.Model):
    __tablename__ = 'matrices'
    id = db.Column(db.Integer, primary_key=True)
    population_id = db.Column(db.Integer, db.ForeignKey('populations.id'))
    treatment_id = db.Column(db.Integer, db.ForeignKey('treatments.id'))
    matrix_split = db.Column(db.Boolean())
    matrix_composition_id = db.Column(db.Integer, db.ForeignKey('matrix_compositions.id'))
    survival_issue = db.Column(db.Float())
    n_intervals = db.Column(db.SmallInteger()) # Danny/Jenni/Dave, what are these? Schema says, "Number of transition intervals represented in the matrix - should only be >1 for mean matrices", so 0 or 1 or more? Can it be a float, ie 0.8?
    periodicity_id = db.Column(db.Integer, db.ForeignKey('periodicities.id'))
    # relative = db.Column(db.Boolean()) --> in schema with no description, must confirm with Judy what this relates to, any below?
    matrix_criteria_size = db.Column(db.Boolean())
    matrix_criteria_ontogeny = db.Column(db.Boolean())
    matrix_criteria_age = db.Column(db.Boolean())
    study_id = db.Column(db.Integer, db.ForeignKey('studies.id'))
    matrix_start = db.Column(db.Date()) # These will include month, day, etc. Create method to return these - matrix_start.day() matrix_start.year() etc
    matrix_end = db.Column(db.Date()) # These will include month, day, etc. Create method to return these - matrix_start.day() matrix_start.year() etc
    matrix_start_season_id = db.Column(db.Integer, db.ForeignKey('seasons.id')) # Proto says season used as described in manuscript, maybe not safe to derive this from latdeg, country, date
    matrix_start_season = db.relationship('Season', foreign_keys='Matrix.matrix_start_season_id')
    matrix_end_season_id = db.Column(db.Integer, db.ForeignKey('seasons.id')) # Proto says season used as described in manuscript, maybe not safe to derive this from latdeg, country, date
    matrix_end_season = db.relationship('Season', foreign_keys='Matrix.matrix_end_season_id')
    matrix_fec = db.Column(db.Boolean())
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

    def __repr__(self):
        return '<Interval %r>' % self.id
