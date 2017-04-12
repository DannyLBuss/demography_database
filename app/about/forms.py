from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField, validators
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError
from flask.ext.pagedown.fields import PageDownField
from wtforms.ext.sqlalchemy.fields import QuerySelectField


# Wordpress blog posts


#class WordpressForm(Form):
#    title = StringField('Name:', [validators.DataRequired()])
#    author = StringField('E-mail address:', [validators.DataRequired()])
#    content = TextAreaField('Your message:', [validators.DataRequired()])
#    date = SubmitField('Send Message')
#    hyperlinj = SubmitField('Send Message')

    