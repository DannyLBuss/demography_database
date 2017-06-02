from flask_wtf import Form
from flask_wtf.file import FileField, FileAllowed, FileRequired
from werkzeug import secure_filename
from wtforms import StringField, TextAreaField, BooleanField, SelectField, SubmitField, validators
from wtforms.validators import Required, Length, Email, Regexp, DataRequired
from wtforms import ValidationError
from flask.ext.pagedown.fields import PageDownField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
# from static import archive ???
import wtforms as wtf
# upload a file - admi:n only

class Average(wtf.Form):
	filename = wtf.FileField(validators=[wtf.validators.InputRequired()])

class AddDatabaseForm(Form):
    file_title = StringField('File Title', validators=[DataRequired()])
    file_description = StringField('File Title', validators=[DataRequired()])
    file_filename = FileField()

class UploadForm(Form):
	filename = FileField(validators=[FileRequired(), FileAllowed(['txt', 'pdf','csv','RData'],'File Type Not Allowed!')
	])


# download a file - all users