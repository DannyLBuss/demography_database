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

#@outputs.route('/downloading', methods=['GET','POST'])
#def downloading():
#    error=None
#    # ...

#    if request.method == 'POST':
#        if download_list == None or len(download_list) < 1:
#            error = 'No files to download'
#        else:
#            timestamp = dt.now().strftime('%Y%m%d:%H%M%S')
#           zfname = 'reports-' + str(timestamp) + '.zip'
#            zf = zipfile.ZipFile(downloaddir + zfname, 'a')
#            for f in download_list:
#                zf.write(downloaddir + f, f)
#            zf.close()

            # TODO: remove zipped files, move zip to archive

#            return send_from_directory(downloaddir, zfname, as_attachment=True)

#    return render_template('downloads.html', error=error, download_list=download_list)

#@outputs.route('/downloads')
#def downloads():
#	downloadfiles = []
#	filenames = []
#	items = os.listdir('/Users/daniellebuss/Sites/demography_database/app/static/uploads')
#	for img in items:
#		if img.endswith(".RData"):
#			downloadfiles.append(img)
#		return downloadfiles[image].split(".")[0]
#		image = random.randint(0, len(downloadfiles)-1)
#	for names in downloadfiles:
#		filenames.append(downloadfiles.img)
#	return filenames
#	return render_template("outputs/downloads.html")

#UPLOAD_FOLDER = '/Users/daniellebuss/Sites/demography_database/app/static/uploads'
#ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'csv', 'RData'])

#app = Flask(__name__)
#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS

#@outputs.route('/static/uploads/<path:filename>', methods=['GET', 'POST'])
#def download(filename):
#    uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
#    return send_from_directory(directory=uploads, filename=filename)

#@outputs.route('/getFile', methods=['GET','POST'])
#def getFile(dirname, filename=None):
#    """
#    Flie delivery to the client.
#    """
#    if not checkFileName(dirname.split('.')[0]):
#        abort(410)
#    if filename:
#        # If dir and filename  is provided, serve it directly
#        return send_from_directory('static/uploads/%s' % dirname, filename)
#    elif not filename:
#        # Otherwise, find the filename and redirect back with it
#        if os.path.exists('static/uploads/%s' % dirname):
#            files = os.listdir('static/uploads/%s' % dirname)
#            if files:
#                # redirect back
#                return redirect(url_for('getFile', dirname=dirname, filename=files[0]))
#        else:
#            abort(404)

#	downloadfiles = []
#	filenames = []
#	items = os.listdir('/Users/daniellebuss/Sites/demography_database/app/static/uploads')
#	for img in items:
#		if img.endswith(".RData"):
#			downloadfiles.append(img)
#		return downloadfiles[image].split(".")[0]
#		image = random.randint(0, len(downloadfiles)-1)
#	for names in downloadfiles:
#		filenames.append(downloadfiles.img)
#	return filenames
#	return render_template("outputs/downloads.html")


#import os
#items = os.listdir(".")

#newlist = []
#for names in items:
#    if names.endswith(".txt"):
#        newlist.append(names)
#print newlist

#@outputs.route('/random_image')
#def random_image():
#	downloadfiles2 = os.listdir(os.path.join(app.static_folder, 'outputs'))
#	img_url = url_for('static', filename=os.path.join('imgs', choice(downloadfiles2)))
#
#	return render_template("outputs/random_image.html", img_url=img_url)

# outputs/downloads
#@outputs.route('/download_csv', methods=['GET', 'POST']) # this is a job for GET, not POST
#def download_csv():
#    return send_file('outputs/test.csv',
#                     mimetype='text/csv',
#                     attachment_filename='test.csv',
#                     as_attachment=True)


#if __name__ == '__main__':
#   app.run(debug = True)