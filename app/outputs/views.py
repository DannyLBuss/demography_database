from flask import render_template, redirect, request, url_for, flash 
from flask.ext.login import login_user, logout_user, login_required, \
    current_user
from flask import *
from flask import send_file
from . import about
from .. import db
from bs4 import BeautifulSoup
from urllib2 import urlopen
import numpy as np
import pandas as pd
import re


# outputs/downloads
@outputs.route('/downloads', methods=['GET', 'POST'])
def downloads():
    return render_template('outputs/downloads.html')

# outputs/archive
@outputs.route('/archive', methods=['GET', 'POST'])
def archive():
    return render_template('outputs/archive.html')

# outputs/agreement
@outputs.route('/agreement', methods=['GET', 'POST'])
def agreement():
    return render_template('outputs/agreement.html')

# outputs/downloads
@outputs.route('/download_csv', methods=['GET', 'POST']) # this is a job for GET, not POST
def download_csv():
    return send_file('outputs/test.csv',
                     mimetype='text/csv',
                     attachment_filename='test.csv',
                     as_attachment=True)

@outputs.route('/download_R', methods=['GET', 'POST'])
def download_R():
    return send_file('static/archive/COMADRE_v.2.0.1.RData', as_attachment=True)



