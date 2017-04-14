from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField, validators
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError
from flask.ext.pagedown.fields import PageDownField
from ..models import Role, User, Institute
from wtforms.ext.sqlalchemy.fields import QuerySelectField






#Create contact form class
def CheckNameLength(form, field):
    if len(field.data) < 3:
        raise ValidationError('Name must have more then 2 characters')

class ContactForm(Form):
    name = StringField('Name:', [validators.DataRequired(), CheckNameLength])
    email = StringField('E-mail address:', [validators.DataRequired(), validators.Email('your@email.com')])
    message = TextAreaField('Your message:', [validators.DataRequired()])
    submit = SubmitField('Send Message')

    