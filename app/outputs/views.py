from flask import Flask, render_template, redirect, request, url_for
from flask_wtf import Form
from flask_wtf.file import FileField
from werkzeug import secure_filename
from flask import send_from_directory
from flask.ext.login import login_user, logout_user, login_required, current_user
from flask import *
from flask import send_file
from . import outputs
from .. import db
from bs4 import BeautifulSoup
from urllib2 import urlopen
from werkzeug.utils import secure_filename
from forms import Average, AddDatabaseForm, UploadForm
import numpy as np
import pandas as pd
import wtforms as wtf
import re
import os
import random

###Download files from UPLOAD FOLDER

@outputs.route('/downloads')
def downloads():
	downloadfiles = []
	filenames = []
	items = os.listdir('/Users/daniellebuss/Sites/demography_database/app/static/uploads')
	for img in items:
		if img.endswith(".RData"):
			downloadfiles.append(img)
		return downloadfiles[image].split(".")[0]
		image = random.randint(0, len(downloadfiles)-1)
	for names in downloadfiles:
		filenames.append(downloadfiles.img)
	return filenames
	return render_template("outputs/downloads.html")


import os
items = os.listdir(".")

newlist = []
for names in items:
    if names.endswith(".txt"):
        newlist.append(names)
print newlist

#@outputs.route('/downloads')
#def downloads():
#	downloads = downloadfiles 
#	return render_template("outputs/downloads.html")

@outputs.route('/random_image')
def random_image():
	downloadfiles2 = os.listdir(os.path.join(app.static_folder, 'outputs'))
	img_url = url_for('static', filename=os.path.join('imgs', choice(downloadfiles2)))

	return render_template("outputs/random_image.html", img_url=img_url)

#@outputs.route('/return-files/')
#def return_files_tut():
#	try:
#		return send_file('', attachment_filename='/Users/daniellebuss/Sites/demography_database/app/static/uploads')

# outputs/downloads
#@outputs.route('/download_csv', methods=['GET', 'POST']) # this is a job for GET, not POST
#def download_csv():
#    return send_file('outputs/test.csv',
#                     mimetype='text/csv',
#                     attachment_filename='test.csv',
#                     as_attachment=True)

#@outputs.route('/download_R', methods=['GET', 'POST'])
#def download_R():
#    return send_file('static/archive/COMADRE_v.2.0.1.RData', as_attachment=True)
#if __name__ == '__main__':
#   app.run(debug = True)