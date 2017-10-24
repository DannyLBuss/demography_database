from flask import Flask, render_template, redirect, request, url_for, flash, session
from flask.ext.login import login_user, logout_user, login_required, \
    current_user
from . import resources
from .. import db

#education
@resources.route('/education')
def education():
    return render_template('resources/education_pages/education.html')

# r resources
@resources.route('/r_resources')
def r_resources():
    return render_template('resources/education_pages/r_resources.html')

# lifecycles
@resources.route('/lifecycles')
def lifecycles():
    return render_template('resources/education_pages/lifecycles.html')

# education ppm
@resources.route('/education_ppm')
def education_ppm():
    return render_template('resources/education_pages/education_matrix_modelling.html')

#publications
@resources.route('/publications')
def publications():
    return render_template('resources/publications.html')