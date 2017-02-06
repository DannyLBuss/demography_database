from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_user, logout_user, login_required, \
    current_user
from . import about
from .. import db

#news
@about.route('/news')
def news():
    return render_template('about/news.html')

#team
@about.route('/team')
def team():
    return render_template('about/team.html')

#history
@about.route('/history')
def history():
    return render_template('about/history.html')

# funding
@about.route('/funding')
def funding():
    return render_template('about/funding.html')

#faqs
@about.route('/FAQs')
def FAQs():
    return render_template('about/FAQs.html')