from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_user, logout_user, login_required, \
    current_user
from . import resources
from .. import db

#education
@resources.route('/education')
def education():
    return render_template('resources/education_pages/education.html')

# education ppm
@resources.route('/education_ppm')
def education_ppm():
    return render_template('resources/education_pages/education_matrix_modelling.html')

#publications
@resources.route('/publications')
def publications():
    return render_template('resources/publications.html')