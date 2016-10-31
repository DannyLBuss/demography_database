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
    VALIDATION = 0x08
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
            'Developer': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, False),
            'Researcher': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, False),
            'Compadrino': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, False),
            'Committee': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS |
                          Permission.VALIDATION, False),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS |
                          Permission.VALIDATION, False),
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
    api_hash = db.Column(db.Text())

    institute_id = db.Column(db.Integer, db.ForeignKey('institutes.id'))
    institute_confirmed = db.Column(db.Boolean, default=False)

    versions = db.relationship("Version", backref="user")  

    @staticmethod
    def migrate():
        Institute.migrate()

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


    def to_json(self, key):
        json_user = {
            
            'username': self.username,
            'member_since': self.member_since,
            'last_seen': self.last_seen
        }
        return json_user

    def generate_auth_token(self):
        username = self.username
        hash_ = hashlib.md5(username).hexdigest()
        self.api_hash = hash_
        db.session.add(self)
        return {'id' : hash_}


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

''' Meta tables '''

''' Meta Tables for Users '''
class Institute(db.Model):
    __tablename__ = 'institutes'
    id = db.Column(db.Integer, primary_key=True)
    institution_name = db.Column(db.String(200))
    institution_short = db.Column(db.String(64))
    main_contact_email = db.Column(db.String(64))
    main_contact_name = db.Column(db.String(64))
    institution_address = db.Column(db.String(200))
    research_group = db.Column(db.String(64))
    date_joined = db.Column(db.Date(), default=datetime.now().date())
    department = db.Column(db.String(64))
    country = db.Column(db.String(64))
    website = db.Column(db.String(200))

    users = db.relationship("User", backref="institute")

    @staticmethod
    def migrate():
        with open('app/data-migrate/users.json') as user_file:
            data = json.load(user_file)
            user = data["User"]
            institute = user["Institute"]

            for ins in institute:
                i = Institute.query.filter_by(institution_name=ins['institution_name']).first()
                if i is None:
                    i = Institute()
                
                i.institution_name = ins['institution_name']
                i.institution_short = ins['institution_short']
                i.main_contact_email = ins['main_contact_email']
                i.main_contact_name = ins['main_contact_name']
                i.institution_address = ins['institution_address']
                i.research_group = ins['research_group']
                i.department = ins['department']
                i.country = ins['country']
                i.website = ins['website']

                db.session.add(i)
                db.session.commit()

    def to_json(self, key):
        print str(self.date_joined)
        institute = {
            'institution_name': self.institution_name,
            'institution_short' : self.institution_short,
            'main_contact_email' : self.main_contact_email,
            'main_contact_name' : self.main_contact_name,
            'institution_address' : self.institution_address,
            'research_group' : self.research_group,
            'date_joined' : str(self.date_joined),
            'department' : self.department,
            'country' : self.country,
            'website' : self.website,
            'users' : url_array(self, 'users', key),

        }
        return institute

    def __repr__(self):
        return str(self.id)

''' End Meta Tables for Users '''

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
            
    def to_json(self, key):
        iucn_status = {
            'status_code': self.status_code,
            'status_name' : self.status_name,
            'status_description' : self.status_description,
            'species' : url_array(self, 'species', key),

        }
        return iucn_status

    def __repr__(self):
        return str(self.id)

class ESAStatus(db.Model):
    __tablename__ = 'esa_statuses'
    id = db.Column(db.Integer, primary_key=True)
    status_code = db.Column(db.String(64), index=True, unique=True)
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

    def to_json(self, key):
        esa_status = {
            'status_code': self.status_code,
            'status_name' : self.status_name,
            'status_description' : self.status_description,
            'species' : url_array(self, 'species', key),

        }
        return esa_status

    def __repr__(self):
        return str(self.id)

''' End Meta Tables for Species '''

''' Meta Tables for Taxonomy '''

''' End Meta Tables for Taxonomy '''

''' Meta Tables for Traits '''
class OrganismType(db.Model):
    __tablename__ = 'organism_types'
    id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(64), index=True)

    traits = db.relationship("Trait", backref="organism_type")

    @staticmethod
    def migrate():
        with open('app/data-migrate/traits.json') as taxonomy_file:
            data = json.load(taxonomy_file)
            species = data["Trait"]
            growth_types = species["OrganismType"]

            for types in growth_types:
                i = OrganismType.query.filter_by(type_name=types['type_name']).first()
                if i is None:
                    i = OrganismType()

                i.type_name = types['type_name']

                db.session.add(i)
                db.session.commit()

    def to_json(self, key):

        organism_type = {
            'type_name': self.type_name,
            'traits' : url_array(self, 'traits', key),
        }
        return organism_type

    def to_json_singular(self, key):        
        organism_type = {
            'type_name': self.type_name,
        }
        return organism_type

    def __repr__(self):
        return str(self.id)

class GrowthFormRaunkiaer(db.Model):
    __tablename__ = 'growth_forms_raunkiaer'
    id = db.Column(db.Integer, primary_key=True, index=True)
    form_name = db.Column(db.Text())

    traits = db.relationship("Trait", backref="growth_form_raunkiaer")

    @staticmethod
    def migrate():
        with open('app/data-migrate/traits.json') as taxonomy_file:
            data = json.load(taxonomy_file)
            species = data["Trait"]
            growth_forms = species["GrowthFormRaunkiaer"]

            for form in growth_forms:
                i = GrowthFormRaunkiaer.query.filter_by(form_name=form['form_name']).first()
                if i is None:
                    i = GrowthFormRaunkiaer()

                i.form_name = form['form_name']

                db.session.add(i)
                db.session.commit()

    def to_json(self, key):
        growth_form = {
            'type_name': self.form_name,
            'traits' : url_array(self, 'traits', key),
        }
        return growth_form

    def to_json_singular(self, key):
        growth_form = {
            'type_name': self.form_name,
        }
        return organism_type

    def __repr__(self):
        return str(self.id)

class ReproductiveRepetition(db.Model):
    __tablename__ = 'reproductive_repetition'
    id = db.Column(db.Integer, primary_key=True, index=True)
    repetition_name = db.Column(db.Text())

    traits = db.relationship("Trait", backref="reproductive_repetition")

    @staticmethod
    def migrate():
        with open('app/data-migrate/traits.json') as d_file:
            data = json.load(d_file)
            json_data = data["Trait"]
            nodes = json_data["ReproductiveRepetition"]

            for node in nodes:

                i = ReproductiveRepetition.query.filter_by(repetition_name=node['repetition_name']).first()
                if i is None:
                    i = ReproductiveRepetition()

                i.repetition_name = node['repetition_name']

                db.session.add(i)
                db.session.commit()

    def __repr__(self):
        return str(self.id)

class DicotMonoc(db.Model):
    __tablename__ = 'dicot_monoc'
    id = db.Column(db.Integer, primary_key=True)
    dicot_monoc_name = db.Column(db.String(64), index=True)

    traits = db.relationship("Trait", backref="dicot_monoc")

    @staticmethod
    def migrate():
        with open('app/data-migrate/traits.json') as d_file:
            data = json.load(d_file)
            json_data = data["Trait"]
            nodes = json_data["DicotMonoc"]

            for node in nodes:
                i = DicotMonoc.query.filter_by(dicot_monoc_name=node['dicot_monoc_name']).first()
                if i is None:
                    i = DicotMonoc()

                i.dicot_monoc_name = node['dicot_monoc_name']

                db.session.add(i)
                db.session.commit()

    def __repr__(self):
        return str(self.id)

class AngioGymno(db.Model):
    __tablename__ = 'angio_gymno'
    id = db.Column(db.Integer, primary_key=True)
    angio_gymno_name = db.Column(db.String(64), index=True)

    traits = db.relationship("Trait", backref="angio_gymno")

    @staticmethod
    def migrate():
        with open('app/data-migrate/traits.json') as d_file:
            data = json.load(d_file)
            json_data = data["Trait"]
            nodes = json_data["AngioGymno"]

            for node in nodes:
                i = AngioGymno.query.filter_by(angio_gymno_name=node['angio_gymno_name']).first()
                if i is None:
                    i = AngioGymno()

                i.angio_gymno_name = node['angio_gymno_name']

                db.session.add(i)
                db.session.commit()

    def __repr__(self):
        return str(self.id)

class SpandExGrowthType(db.Model):
    __tablename__ = 'spand_ex_growth_types'
    id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(64), index=True)
    type_description = db.Column(db.Text)

    traits = db.relationship("Trait", backref="spand_ex_growth_types")

    @staticmethod
    def migrate():

        with open('app/data-migrate/traits.json') as d_file:
            data = json.load(d_file)
            json_data = data["Trait"]
            nodes = json_data["SpandExGrowthType"]

            for node in nodes:          
                i = SpandExGrowthType.query.filter_by(type_name=node['growth_type_name']).first()
                if i is None:
                    i = SpandExGrowthType()

                i.type_name = node['growth_type_name']
                i.type_description = node['growth_type_description']

                db.session.add(i)
                db.session.commit()

    def __repr__(self):
        return str(self.id)
''' End Meta Tables for Traits '''

''' Meta Tables for Publication/Additional Source '''
class SourceType(db.Model):
    __tablename__ = 'source_types'
    id = db.Column(db.Integer, primary_key=True)
    source_name = db.Column(db.String(64), index=True)
    source_description = db.Column(db.Text())

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
        return str(self.id)

class Database(db.Model):
    __tablename__ = 'databases'
    id = db.Column(db.Integer, primary_key=True)
    database_name = db.Column(db.String(64), index=True)
    database_description = db.Column(db.Text())
    database_master_version = db.Column(db.String(64))
    database_date_created = db.Column(db.Date())
    database_number_species_accepted = db.Column(db.Integer())
    database_number_studies = db.Column(db.Integer())
    database_number_matrices = db.Column(db.Integer())
    database_agreement = db.Column(db.String(64))

    versions = db.relationship("Version", backref="database")  

    @staticmethod
    def migrate():
        with open('app/data-migrate/versions.json') as d_file:
            data = json.load(d_file)
            json_data = data["Version"]
            nodes = json_data["Database"]

            for node in nodes:
                i = Database.query.filter_by(database_name=node['database_name']).first()
                if i is None:
                    i = Database()

                i.database_name = node['database_name']
                i.database_description = node['database_description']
                i.database_master_version = None
                i.database_date_created = None
                i.database_number_species_accepted = None
                i.database_number_studies = None
                i.database_number_matrices = None
                i.database_agreement = None

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
        return str(self.id)

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
        return str(self.id)


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
        return str(self.id)
''' End Meta Tables for Author Contact '''

''' Meta Tables for Study'''
class PurposeEndangered(db.Model):
    __tablename__ = 'purposes_endangered'
    id = db.Column(db.Integer, primary_key=True)
    purpose_name = db.Column(db.String(64), index=True)
    purpose_description = db.Column(db.Text())

    studies = db.relationship("Study", backref="purpose_endangered")

    @staticmethod
    def migrate():
        with open('app/data-migrate/studies.json') as d_file:
            data = json.load(d_file)
            json_data = data["Study"]
            nodes = json_data["PurposeEndangered"]

            for node in nodes:

                i = PurposeEndangered.query.filter_by(purpose_name=node['purpose_name']).first()

                if i is None:
                    i = PurposeEndangered()

                i.purpose_name = node['purpose_name']
                i.purpose_description = node['purpose_description']

                print i.purpose_name

                db.session.add(i)
                db.session.commit()

    def __repr__(self):
        return str(self.id)

class PurposeWeed(db.Model):
    __tablename__ = 'purposes_weed'
    id = db.Column(db.Integer, primary_key=True)
    purpose_name = db.Column(db.String(64), index=True)
    purpose_description = db.Column(db.Text())

    studies = db.relationship("Study", backref="purpose_weed")

    @staticmethod
    def migrate():
        with open('app/data-migrate/studies.json') as d_file:
            data = json.load(d_file)
            json_data = data["Study"]
            nodes = json_data["PurposeWeed"]

            for node in nodes:

                i = PurposeWeed.query.filter_by(purpose_name=node['purpose_name']).first()

                if i is None:
                    i = PurposeWeed()

                i.purpose_name = node['purpose_name']
                i.purpose_description = node['purpose_description']

                print i.purpose_name

                db.session.add(i)
                db.session.commit()

    def __repr__(self):
        return str(self.id)

''' End Meta Tables for Study '''

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
        return str(self.id)

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
        return str(self.id)

class InvasiveStatusStudy(db.Model):
    __tablename__ = 'invasivestatusstudies'
    id = db.Column(db.Integer, primary_key=True)
    status_name = db.Column(db.String(64), index=True)
    status_description = db.Column(db.Text)

    populations = db.relationship("Population", backref="invasivestatusstudies")

    @staticmethod
    def migrate():
        with open('app/data-migrate/populations.json') as d_file:
            data = json.load(d_file)
            json_data = data["Population"]
            nodes = json_data["InvasiveStatusStudy"]

            for node in nodes:
                i = InvasiveStatusStudy.query.filter_by(status_name=node['status_name']).first()
                if i is None:
                    i = InvasiveStatusStudy()

                i.status_name = node['status_name']
                i.status_description = node['status_description']

                db.session.add(i)
                db.session.commit()

    def __repr__(self):
        return str(self.id)

class InvasiveStatusElsewhere(db.Model):
    __tablename__ = 'invasive_status_elsewhere'
    id = db.Column(db.Integer, primary_key=True)
    status_name = db.Column(db.String(64), index=True)
    status_description = db.Column(db.Text)

    populations = db.relationship("Population", backref="invasive_status_elsewhere")

    @staticmethod
    def migrate():
        with open('app/data-migrate/populations.json') as d_file:
            data = json.load(d_file)
            json_data = data["Population"]
            nodes = json_data["InvasiveStatusElsewhere"]

            for node in nodes:
                i = InvasiveStatusElsewhere.query.filter_by(status_name=node['status_name']).first()
                if i is None:
                    i = InvasiveStatusElsewhere()

                i.status_name = node['status_name']
                i.status_description = node['status_description']

                db.session.add(i)
                db.session.commit()

    def __repr__(self):
        return str(self.id)
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
        return str(self.id)

class StartSeason(db.Model):
    __tablename__ = 'start_seasons'
    id = db.Column(db.Integer, primary_key=True)
    season_id = db.Column(db.Integer())
    season_name = db.Column(db.String(64), index=True)

    matrices = db.relationship("Matrix", backref="start_season", lazy="dynamic")

    @staticmethod
    def migrate():
        with open('app/data-migrate/matrices.json') as d_file:
            data = json.load(d_file)
            json_data = data["Matrix"]
            nodes = json_data["Season"]

            for node in nodes:
                i = StartSeason.query.filter_by(season_id=node['season_id']).first()
                if i is None:
                    i = StartSeason()

                i.season_id = node['season_id']
                i.season_name = node['season_name']

                db.session.add(i)
                db.session.commit()

    def __repr__(self):
        return str(self.id)

class EndSeason(db.Model):
    __tablename__ = 'end_seasons'
    id = db.Column(db.Integer, primary_key=True)
    season_id = db.Column(db.Integer())
    season_name = db.Column(db.String(64), index=True)

    matrices = db.relationship("Matrix", backref="end_season", lazy="dynamic")

    @staticmethod
    def migrate():
        with open('app/data-migrate/matrices.json') as d_file:
            data = json.load(d_file)
            json_data = data["Matrix"]
            nodes = json_data["Season"]

            for node in nodes:
                i = EndSeason.query.filter_by(season_id=node['season_id']).first()
                if i is None:
                    i = EndSeason()

                i.season_id = node['season_id']
                i.season_name = node['season_name']

                db.session.add(i)
                db.session.commit()

    def __repr__(self):
        return str(self.id)

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
        return str(self.id)

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
        return str(self.id)


class Status(db.Model):
    __tablename__ = 'statuses'
    id = db.Column(db.Integer, primary_key=True)
    status_name = db.Column(db.String(64), index=True)
    status_description = db.Column(db.Text())
    notes = db.Column(db.Text())

    versions = db.relationship("Version", backref="statuses")

    @staticmethod
    def migrate():
        with open('app/data-migrate/versions.json') as d_file:
            data = json.load(d_file)
            json_data = data["Version"]
            nodes = json_data["Status"]

            for node in nodes:
                i = Status.query.filter_by(status_name=node['status_name']).first()
                if i is None:
                    i = Status()

                i.status_name = node['status_name']
                i.status_description = node['status_description']

                db.session.add(i)
                db.session.commit()

    def __repr__(self):
        return str(self.id)
''' End Meta Tables for Matrix '''

''' Meta Tables for Fixed '''
class Small(db.Model):
    __tablename__ = 'smalls'
    id = db.Column(db.Integer, primary_key=True)
    small_name = db.Column(db.String(200), index=True)
    small_description = db.Column(db.Text())

    fixed = db.relationship("Fixed", backref="smalls")

    @staticmethod
    def migrate():
        with open('app/data-migrate/fixed.json') as d_file:
            data = json.load(d_file)
            json_data = data["Fixed"]
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
        return '<Small %r>' % self.id

class CensusTiming(db.Model):
    __tablename__ = 'census_timings'
    id = db.Column(db.Integer, primary_key=True)
    census_name = db.Column(db.String(200), index=True)
    census_description = db.Column(db.Text())

    fixed = db.relationship("Fixed", backref="census_timings")

    @staticmethod
    def migrate():
        with open('app/data-migrate/fixed.json') as d_file:
            data = json.load(d_file)
            json_data = data["Fixed"]
            nodes = json_data["CensusTiming"]

            for node in nodes:
                i = CensusTiming.query.filter_by(census_name=node['census_name']).first()
                if i is None:
                    i = CensusTiming()

                i.census_name = node['census_name']
                i.census_description = node['census_description']

                db.session.add(i)
                db.session.commit()

    def __repr__(self):
        return '<StageClassInfo %r>' % self.id
''' End Meta Tables for Fixed '''

''' End Meta Tables '''

class Species(db.Model):
    __tablename__ = 'species'
    id = db.Column(db.Integer, primary_key=True)
    # subspecies = db.Column(db.String(64))
    species_accepted = db.Column(db.String(64))
    species_common = db.Column(db.String(200))
    iucn_status_id = db.Column(db.Integer, db.ForeignKey('iucn_status.id'))
    esa_status_id = db.Column(db.Integer, db.ForeignKey('esa_statuses.id'))
    invasive_status = db.Column(db.Boolean())
    gbif_taxon_key = db.Column(db.Integer)
    image_path = db.Column(db.Text)
    image_path2 = db.Column(db.Text)
    taxonomies = db.relationship("Taxonomy", backref="species")
    traits = db.relationship("Trait", backref="species")
    populations = db.relationship("Population", backref="species")
    stages = db.relationship("Stage", backref="species")

    versions = db.relationship("Version", backref="species")

    @staticmethod
    def migrate():
        IUCNStatus.migrate()
        ESAStatus.migrate()

    def save_as_version(self):
        print self

    def to_json(self, key):
        species = {
            'species_accepted': self.species_accepted,
            'taxonomy' : [taxonomy.to_json(key) for taxonomy in self.taxonomies][0],
            'traits' : [trait.to_json(key) for trait in self.traits][0],
            'populations' : url_array(self, 'populations', key),
            'number_populations' : len(url_array(self, 'populations', key)),
            'gbif_taxon_key' : self.gbif_taxon_key
            # 'stages' : [stage.to_json() for stage in self.stages][0]
        }
        return species

    def to_json_simple(self, key):
        species = {
            'species_accepted': self.species_accepted,
            'taxonomy' : url_array(self, 'taxonomies', key),
            'traits' : url_array(self, 'traits', key),
            'populations' : url_array(self, 'populations', key)
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

    col_check_ok = db.Column(db.Boolean())
    col_check_date = db.Column(db.Date())

    versions = db.relationship("Version", backref="taxonomy")

    @staticmethod
    def migrate():
        pass

    def to_json(self, key):
        try:
            taxonomy = {
                'species_author' : self.species_author,
                'species_accepted' : self.species_accepted,
                'publication' : (self.publication).to_json(key),
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
                'publication' : (self.publication).to_json(key),
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


class Trait(db.Model):
    __tablename__ = 'traits'
    id = db.Column(db.Integer, primary_key=True)
    species_id = db.Column(db.Integer, db.ForeignKey('species.id'))
    max_height = db.Column(db.Float()) #This should be a double, eventually
    organism_type_id = db.Column(db.Integer, db.ForeignKey('organism_types.id'))
    growth_form_raunkiaer_id = db.Column(db.Integer, db.ForeignKey('growth_forms_raunkiaer.id'))
    reproductive_repetition_id = db.Column(db.Integer, db.ForeignKey('reproductive_repetition.id'))
    dicot_monoc_id = db.Column(db.Integer, db.ForeignKey('dicot_monoc.id'))
    angio_gymno_id = db.Column(db.Integer, db.ForeignKey('angio_gymno.id'))
    spand_ex_growth_type_id = db.Column(db.Integer, db.ForeignKey('spand_ex_growth_types.id'))

    versions = db.relationship("Version", backref="trait")

    @staticmethod
    def migrate():
        OrganismType.migrate()
        GrowthFormRaunkiaer.migrate()
        ReproductiveRepetition.migrate()
        DicotMonoc.migrate()
        AngioGymno.migrate()
        SpandExGrowthType.migrate()

    def to_json(self, key):
        trait = {
            'max_height' : self.max_height,
            'organism_type_id' : self.organism_type.type_name,
            # 'growth_form_raunkiaer' : self.growth_form_raunkiaer.form_name,
            # 'reproductive_repetition' : self.reproductive_repetition.repetition_name,
            # 'dicot_monoc' : self.dicot_monoc.dicot_monoc_name,
            # 'angio_gymno' : self.angio_gymno.angio_gymno_name
        }
        return trait

    def __repr__(self):
        return '<Trait %r>' % self.id

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
    colour = db.Column(db.String(6))

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
    taxonomies = db.relationship("Taxonomy", backref="publication")
    studies = db.relationship("Study", backref="publication")

    versions = db.relationship("Version", backref="publication")

    @staticmethod
    def migrate():
        SourceType.migrate()
        Purpose.migrate()
        MissingData.migrate()

    def to_json(self, key):
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
            'populations' : url_array(self, 'populations', key),   
            # 'stages' : [stage.to_json() for stage in self.stages][0]
            # 'treatments' : [treatment.to_json() for treatment in self.treatments][0]
            'taxonomies' : url_array(self, 'taxonomies', key),
            'studies' : url_array(self, 'studies', key)
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

    purpose_endangered_id = db.Column(db.Integer, db.ForeignKey('purposes_endangered.id'))
    purpose_weed_id = db.Column(db.Integer, db.ForeignKey('purposes_weed.id'))

    matrices = db.relationship("Matrix", backref="study")
    populations = db.relationship("Population", backref="study")
    number_populations = db.Column(db.Integer()) #could verify with populations.count()

    versions = db.relationship("Version", backref="study")

    @staticmethod
    def migrate():
        PurposeEndangered.migrate()
        PurposeWeed.migrate()

    def to_json(self, key):
        study = {
            'publication' : url_for('api.get_publication', id=self.publication.id, key=key,
                                  _external=False),
            'study_duration' : self.study_duration,
            'study_start' : self.study_start,
            'study_end' : self.study_end,
            'number_populations' : self.number_populations,           
            'matrices' : url_array(self, 'matrices', key),
            'populations' : url_array(self, 'populations', key)
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

    versions = db.relationship("Version", backref="author_contact")


    @staticmethod
    def migrate():
        ContentEmail.migrate()

    def to_json(self, key):
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

    versions = db.relationship("Version", backref="additional_source")

    def to_json(self, key):
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
    invasive_status_study_id = db.Column(db.Integer, db.ForeignKey('invasivestatusstudies.id'))
    invasive_status_elsewhere_id = db.Column(db.Integer, db.ForeignKey('invasive_status_elsewhere.id'))
    country = db.Column(db.Text())
    continent_id = db.Column(db.Integer, db.ForeignKey('continents.id'))
    geometries = db.Column(db.Text())
    latitude = db.Column(db.Float())
    longitude = db.Column(db.Float())
    altitude = db.Column(db.Float())
    pop_size = db.Column(db.Text())

    matrices = db.relationship("Matrix", backref="population")

    versions = db.relationship("Version", backref="population")

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

        if lat_we != 'NA':
            if lat_we == 'W':
                lon_deg = -float(lon_deg)
                
        try:
            decimal_lat = float(lat_deg)+float(lat_min)/60+float(lat_sec)/3600
            decimal_lon = float(lon_deg)+float(lon_min)/60+float(lon_sec)/3600
            altitude = float(altitude)
        except:
            decimal_lat = 'NA'
            decimal_lon = 'NA'
            altitude = 'NA'

        geometries = {"latitude" : decimal_lat, "longitude" : decimal_lon, "altitude" : altitude}
        return geometries


    def to_json(self, key):
        try:
            population = {
                'species' : url_for('api.get_species', id=self.species.id, key=key,
                                      _external=False),
                'publication' : url_for('api.get_publication', id=self.publication.id, key=key,
                                      _external=False),
                'study' : self.study.to_json(key),
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
            'species' : url_for('api.get_species', id=self.species.id, key=key,
                                  _external=False),
            'publication' : url_for('api.get_publication', id=self.publication.id, key=key,
                                  _external=False),
            'study' : self.study.to_json(key),
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
        InvasiveStatusStudy.migrate()
        InvasiveStatusElsewhere.migrate()

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

    versions = db.relationship("Version", backref="stage")

    def to_json(self, key):
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

    versions = db.relationship("Version", backref="stage_type")

    def to_json(self, key):
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


class Treatment(db.Model):
    __tablename__ = 'treatments'
    id = db.Column(db.Integer, primary_key=True, index=True)
    treatment_name = db.Column(db.Text())
    
    matrices = db.relationship("Matrix", backref="treatment")
    

    @staticmethod
    def migrate():
        with open('app/data-migrate/matrices.json') as d_file:
            data = json.load(d_file)
            json_data = data["Matrix"]
            nodes = json_data["Treatment"]

            for node in nodes:
                i = Treatment.query.filter_by(treatment_name=node['type_name']).first()
                if i is None:
                    i = Treatment()

                i.type_name = node['treatment_name']

                db.session.add(i)
                db.session.commit()

    def to_json(self, key):
        treatment= {
            'type_name' : self.type_name,

            # Matrices?
        }
        return treatment_type


    def __repr__(self):
        return '<Treatment %r>' % self.id

class MatrixStage(db.Model):
    __tablename__ = 'matrix_stages'
    id = db.Column(db.Integer, primary_key=True)
    stage_order = db.Column(db.SmallInteger())
    stage_id = db.Column(db.Integer, db.ForeignKey('stages.id'))

    matrix_id = db.Column(db.Integer, db.ForeignKey('matrices.id'))

    versions = db.relationship("Version", backref="matrix_stage")

    def to_json(self, key):
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

    versions = db.relationship("Version", backref="matrix_value")

    @staticmethod
    def migrate():
        TransitionType.migrate()

    def to_json(self, key):
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
    uid = db.Column(db.String(200), index=True, unique=True)
    population_id = db.Column(db.Integer, db.ForeignKey('populations.id'))
    treatment_id = db.Column(db.Integer, db.ForeignKey('treatments.id'))
    matrix_split = db.Column(db.String(64))
    matrix_composition_id = db.Column(db.Integer, db.ForeignKey('matrix_compositions.id'))
    seasonal = db.Column(db.Boolean())
    survival_issue = db.Column(db.Float())
    n_intervals = db.Column(db.SmallInteger()) # Danny/Jenni/Dave, what are these? Schema says, "Number of transition intervals represented in the matrix - should only be >1 for mean matrices", so 0 or 1 or more? Can it be a float, ie 0.8?
    periodicity = db.Column(db.String(200))
    # relative = db.Column(db.Boolean()) --> in schema with no description, must confirm with Judy what this relates to, any below?
    matrix_criteria_size = db.Column(db.String(200))
    matrix_criteria_ontogeny = db.Column(db.Boolean())
    matrix_criteria_age = db.Column(db.Boolean())
    study_id = db.Column(db.Integer, db.ForeignKey('studies.id'))
    matrix_start = db.Column(db.String(64)) # These will include month, day, etc. Create method to return these - matrix_start.day() matrix_start.year() etc
    matrix_start_year = db.Column(db.Integer)
    matrix_start_month = db.Column(db.Integer())
    matrix_end_year = db.Column(db.Integer)
    matrix_end_month = db.Column(db.Integer())
    matrix_end = db.Column(db.String(64)) # These will include month, day, etc. Create method to return these - matrix_start.day() matrix_start.year() etc
    matrix_start_season_id = db.Column(db.Integer, db.ForeignKey('start_seasons.id')) # Proto says season used as described in manuscript, maybe not safe to derive this from latdeg, country, date
    matrix_end_season_id = db.Column(db.Integer, db.ForeignKey('end_seasons.id')) # Proto says season used as described in manuscript, maybe not safe to derive this from latdeg, country, date
    matrix_fec = db.Column(db.Boolean())
    matrix_a_string = db.Column(db.Text())
    matrix_u_string = db.Column(db.Text())
    matrix_f_string = db.Column(db.Text())
    matrix_c_string = db.Column(db.Text())
    matrix_class_string = db.Column(db.Text())
    matrix_difficulty = db.Column(db.String(64))
    matrix_complete = db.Column(db.Boolean())
    independence_origin = db.Column(db.Text())
    n_plots = db.Column(db.SmallInteger()) # Danny/Jenni/Dave, will need your help with plots too - not quite sure what they are.
    plot_size = db.Column(db.Float()) # Schema states, 'R convert to m^2'
    n_individuals = db.Column(db.Integer()) # Schema states, 'total number of individuals observed'
    studied_sex_id = db.Column(db.Integer, db.ForeignKey('studied_sex.id'))
    captivity_id = db.Column(db.Integer, db.ForeignKey('captivities.id'))
    matrix_dimension = db.Column(db.Integer()) # dimension of matrix population A   
    observations = db.Column(db.Text())

    class_organized = db.Column(db.Text())
    class_author = db.Column(db.Text())
    class_number = db.Column(db.Text())

    vectors_includes_na = db.Column(db.Boolean())

    

    
    independent = db.Column(db.Boolean())
    non_independence = db.Column(db.Text())
    non_independence_author = db.Column(db.Text())

    intervals = db.relationship("Interval", backref="matrix")
    matrix_values = db.relationship("MatrixValue", backref="matrix")
    matrix_stages = db.relationship("MatrixStage", backref="matrix")
    fixed = db.relationship("Fixed", backref="matrix")
    seeds = db.relationship("Seed", backref="matrix")

    # Versioning
    versions = db.relationship("Version", backref="matrix")
    

    @staticmethod
    def migrate():
        MatrixComposition.migrate()
        StartSeason.migrate()
        EndSeason.migrate()
        StudiedSex.migrate()
        Captivity.migrate()
        Status.migrate()

    # Generate UID for this Matrix
    def create_uid(self):
        import re
        species_accepted = self.population.species.species_accepted
        journal = self.population.publication.pub_title
        year_pub = self.population.publication.year
        authors = self.population.publication.authors[:15].encode('utf-8')
        pop_name = self.population.name.encode('utf-8')
        
        try:
            composite = self.matrix_composition.comp_name
        except AttributeError:
            composite = ''

        # treatment = self.treatment.treatment_name
        try:
            start_year = self.matrix_start[-4:]
        except TypeError:
            start_year = ''

        # observation = self.observations.encode('utf-8')
        # matrix_a_string = self.matrix_a_string

        import time
        timestamp = time.time()
        print(species_accepted, journal, year_pub, authors, pop_name, composite, start_year)
        uid_concat = '{}{}{}{}{}{}{}{}'.format(species_accepted, journal, year_pub, authors, pop_name, composite, start_year, timestamp)
        uid_lower = uid_concat.lower()
        uid = re.sub('[\W_]+', '', uid_lower)

        self.uid = uid
        if Matrix.query.filter_by(uid=uid).first() == None:
            # db.session.add(self)
            # db.session.commit()
            print uid
        else:
            print("UID already exists")
            return 

    def to_json(self, key):
        try:
            matrix = {
                'population' : url_for('api.get_population', key=key, id=self.population.id,
                                  _external=False),
                'study' : url_for('api.get_study', id=self.study.id, key=key,
                                  _external=False),
                'treatment' : self.treatment.treatment_name,
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
                # Fixed?
            }
        except:
            # Without seasons
            matrix = {
                'population' : url_for('api.get_population', id=self.population.id, key=key,
                                  _external=False),
                'study' : url_for('api.get_study', id=self.study.id, key=key,
                                  _external=False),
                'treatment' : self.treatment.treatment_name,
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
                # Fixed?
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

    def to_json(self, key):
        interval = {
            # 'matrix' : self.matrix.id (url?)
            'interval_order' : self.interval_order,
            'interval_start' : self.interval_start,
            'interval_end' : self.interval_end
        }
        return interval

    def __repr__(self):
        return '<Interval %r>' % self.id

''' Secret & Important Fixed Stuff '''
class Fixed(db.Model):
    __tablename__ = 'fixed'
    id = db.Column(db.Integer, primary_key=True)
    matrix_id = db.Column(db.Integer, db.ForeignKey('matrices.id'), index=True)
    vector_str = db.Column(db.Text())
    vector_present = db.Column(db.Boolean())
    total_pop_no = db.Column(db.Integer())
    small_id = db.Column(db.Integer, db.ForeignKey('smalls.id'))
    census_timing_id = db.Column(db.Integer, db.ForeignKey('census_timings.id'))
    seed_stage_error = db.Column(db.Boolean())
    private = db.Column(db.Boolean(), default=True)

    versions = db.relationship("Version", backref="fixed")

    @staticmethod
    def migrate():
        CensusTiming.migrate()
        Small.migrate()

    def to_json(self, key):
        fixed = {
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
        return fixed

    def __repr__(self):
        return '<Fixed %r>' % self.id

''' Do we even need this? '''
class Seed(db.Model):
    __tablename__ = 'seeds'
    id = db.Column(db.Integer, primary_key=True)
    matrix_id = db.Column(db.Integer, db.ForeignKey('matrices.id'), index=True)
    matrix_a = db.Column(db.Text())

    def to_json(self):
        seeds = {
            # 'matrix' : self.matrix.id (url?)
            'matrix_a' : self.matrix_a,
            #'version' : self.version,
        }

    def __repr__(self, key):
        return '<Seed %r>' % self.id


class Version(db.Model):
    __tablename__ = 'versions'
    id = db.Column(db.Integer, primary_key=True)
    version_number = db.Column(db.Integer(), default=0)
    version_of_id = db.Column(db.Integer, db.ForeignKey('versions.id')) 
    version_date_added = db.Column(db.Date())
    version_timestamp_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    # This is as if treating as a whole row, but we are trying to get away from that
    version_uid = db.Column(db.Text())
    
    versions = db.relationship("Version", backref="original_version", remote_side="Version.id", uselist=True)
    checked = db.Column(db.Boolean())
    
    status_id = db.Column(db.Integer, db.ForeignKey('statuses.id'))
    checked_count = db.Column(db.Integer(), default=0)

    # Utility relationships
    version_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    database_id = db.Column(db.Integer, db.ForeignKey('databases.id'))

    # Demography relationships
    species_id = db.Column(db.Integer, db.ForeignKey('species.id'))
    taxonomy_id = db.Column(db.Integer, db.ForeignKey('taxonomies.id'))
    trait_id = db.Column(db.Integer, db.ForeignKey('traits.id'))
    publication_id = db.Column(db.Integer, db.ForeignKey('publications.id'))
    study_id = db.Column(db.Integer, db.ForeignKey('studies.id'))
    population_id = db.Column(db.Integer, db.ForeignKey('populations.id'))
    matrix_id = db.Column(db.Integer, db.ForeignKey('matrices.id'))
    fixed_id = db.Column(db.Integer, db.ForeignKey('fixed.id'))

    stage_id = db.Column(db.Integer, db.ForeignKey('stages.id'))
    stage_type_id = db.Column(db.Integer, db.ForeignKey('stage_types.id'))

    matrix_stage_id = db.Column(db.Integer, db.ForeignKey('matrix_stages.id'))
    matrix_value_id = db.Column(db.Integer, db.ForeignKey('matrix_values.id'))

    author_contact_id = db.Column(db.Integer, db.ForeignKey('author_contacts.id'))
    additional_source_id = db.Column(db.Integer, db.ForeignKey('additional_sources.id')) 
    


    @staticmethod
    def migrate():
        Database.migrate()

    def __repr__(self):
        return '<Version %r>' % self.id

from datetime import datetime
def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError ("Type not serializable")

def url_array(self, string, key):
    if string == 'populations':
        population_urls = []
        for population in self.populations:
            url = url_for('api.get_population', key=key, id=population.id,
                                  _external=False)
            population_urls.append(url)
        return population_urls

    elif string == 'taxonomies':
        taxonomy_urls = []
        for taxonomy in self.taxonomies:
            url = url_for('api.get_taxonomy', id=taxonomy.id, key=key,
                                  _external=False)
            taxonomy_urls.append(url)
        return taxonomy_urls
    elif string == 'studies':
        study_urls = []
        for study in self.studies:
            url = url_for('api.get_study', id=study.id, key=key,
                                  _external=False)
            study_urls.append(url)
        return study_urls
    elif string == 'matrices':
        matrix_urls = []
        for matrix in self.matrices:
            url = url_for('api.get_matrix', id=matrix.id, key=key,
                                  _external=False)
            matrix_urls.append(url)
        return matrix_urls
    elif string == 'traits':
        trait_urls = []
        for trait in self.traits:
            url = url_for('api.get_trait', id=trait.id, key=key,
                                  _external=False)
            trait_urls.append(url)
        return trait_urls
    
    elif string == 'users':
        user_urls = []
        for user in self.users:
            url = url_for('api.get_user', id=user.id, key=key,
                                  _external=False)
            user_urls.append(url)
        return user_urls



