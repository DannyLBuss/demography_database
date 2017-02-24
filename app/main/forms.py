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



#Create contact form class
def CheckNameLength(form, field):
    if len(field.data) < 3:
        raise ValidationError('Name must have more then 2 characters')

class ContactForm(Form):
    name = StringField('Name:', [validators.DataRequired(), CheckNameLength])
    email = StringField('E-mail address:', [validators.DataRequired(), validators.Email('your@email.com')])
    message = TextAreaField('Your message:', [validators.DataRequired()])
    submit = SubmitField('Send Message')

    