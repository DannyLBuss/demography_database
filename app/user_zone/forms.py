from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField, validators
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError
from flask.ext.pagedown.fields import PageDownField
from ..models import Role, User, Institute
from wtforms.ext.sqlalchemy.fields import QuerySelectField

# Edit your profile
class EditProfileForm(Form):
    username = StringField('Username', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    name = StringField('Full name', validators=[Required()])
    institute = QuerySelectField('Institution - Please note that if you change this, it will need to be confirmed by the site admin',query_factory=lambda: Institute.query.all(), get_pk=lambda a: a.id,get_label=lambda a:a.institution_name, validators=[Required()])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')
    
    def __init__(self, user, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.user = user
    
    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')
            
            
# Create a new list

class EditUserListForm(Form):
    name = StringField('Name of list', validators=[Required()])
    description = StringField('Description', validators=[Required()])
    public = BooleanField('Public', validators=[Required()])
    DOI_ISBN = StringField('DOI_ISBN', validators=[Required()])
    
    submit = SubmitField('Submit')
    