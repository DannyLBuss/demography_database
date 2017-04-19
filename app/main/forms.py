from flask.ext.wtf import Form, validators
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError
from flask.ext.pagedown.fields import PageDownField
from ..models import Role, User, Institute
from wtforms.ext.sqlalchemy.fields import QuerySelectField
import wtforms






#Create contact form class
def CheckNameLength(form, field):
    if len(field.data) < 3:
        raise ValidationError('Name must have more then 2 characters')

class ContactForm(Form):
    name = StringField("Name", [wtforms.validators.Required('Please enter your name')])
    email = StringField("Email", [wtforms.validators.Required('Please enter your email'), wtforms.validators.Email()])
    subject = StringField("Subject", [wtforms.validators.Required('Please enter a subject')])
    message = TextAreaField("Message", [wtforms.validators.Required('Please enter a message')])
    submit = SubmitField("Send")
    