from flask import render_template, redirect, request, url_for, flash 
from flask.ext.login import login_user, logout_user, login_required, \
    current_user
from . import about
from .. import db
from app.wordpressfunction import wordpress_data
from bs4 import BeautifulSoup
from urllib2 import urlopen
import numpy as np
import pandas as pd
import re

#news
@about.route('/news')
def news():
    return render_template('about/news.html')

#team
@about.route('/team')
def team():
    return render_template('about/team.html')

#about/wordpress
@about.route('/wordpress', methods=['GET', 'POST'])
def wordpress():
    wordpress = wordpress_data()
    return render_template('wordpress.html', wordpress=wordpress)
#    wordpress.set_index(['title'], inplace=True)
#    wordpress.index.title=None
#    return render_template('wordpress.html', tables=[wordpress.to_html(classes='wordpress')]),
#    titles = ['wordpress']

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


#if __name__ == "__about__":
#    app.run(debug=True)
