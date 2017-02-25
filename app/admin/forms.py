from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SelectField,SubmitField, validators, PasswordField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User, Role, Institute

    

from wtforms.ext.sqlalchemy.fields import QuerySelectField

# edit any profile as admin
class EditProfileAdminForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    username = StringField('Username', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    institute = QuerySelectField('Institution',query_factory=lambda: Institute.query.all(), get_pk=lambda a: a.id,get_label=lambda a:a.institution_name, validators=[Required()])
    institute_confirmed = BooleanField('Confirm institution')
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')
            
class EditInstituteAdminForm(Form):
    institution_name = StringField('Institution name')
    institution_short = StringField('Institution short name')
    main_contact_email = StringField('Institution contact email', validators = [Email()])
    main_contact_name = StringField('Institution contact name')
    institution_address = StringField('Institution address')
    research_group = StringField('Research group')
    #date_joined
    department = StringField('Department')
    country = StringField('Country')
    website = StringField('Website')
    submit = SubmitField('Submit')
    