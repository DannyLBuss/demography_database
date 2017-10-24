from flask import Flask, render_template, redirect, request, url_for, flash, session
from flask.ext.login import login_user, logout_user, login_required, \
    current_user
from flask import *
from . import about
from .. import db
from app.wordpressfunction import wordpress_data
from bs4 import BeautifulSoup
from urllib2 import urlopen
import numpy as np
import pandas as pd
import re
import twitter
from twitter import Twitter

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
    data = wordpress_data()
    data['Contents'].replace(regex=True,inplace=True, to_replace=r'\\n\\t\\t\\t',value=r'')
    return render_template('about/wordpress.html', wordpress=wordpress, data=[data.to_html(header=True, index=False, border=True)])

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

@about.route('/socialmedia')
def socialmedia():
    return render_template('about/social_media.html')

# @about.route('/social_media')
# def social_media():
#     api = twitter.Api(
#     	consumer_key='4G7C729hkGfcpHDI8zCTFZkBA',
#     	consumer_secret='hA67P0DOFE8jISpIMgqp25rAxh2WpEhtrlyEQw6diluaJwdGkm',
#     	access_token_key='23463646-j5rbrfFGlMPmQMK7dsL1IC6f5g8K5GuccwKykU8PK',
#     	access_token_secret='VOsJmHgp7o8gkMxlB5ffMRjeTTD3wIAx2MO2CYLA37O2r'
#     	)

#     twitter_user = "spand_ex"
#     statuses = api.GetUserTimeline(screen_name=twitter_user)

#     twitter_statuses = []

#     for s in statuses:
#         status = {}
#         status["text"] = s.text
#         status["status_id"] = s.id

#         if s.media != []:
#             status["media"] = []
#             for media in s.media:
#                 media_item = {}
#                 media_item["display_url"] = media["display_url"]
#                 media_item["media_url"] = media["media_url"]
#                 media_item["type"] = media["type"]
#                 status["media"].append(media_item)


#         status["created_date"] = s.created_at
        
#         usr = s.user
#         status["user_id"] = usr.id
#         status["user_name"] = usr.name 
#         status["profile_background_color"] = usr.profile_background_color
#         status["profile_background_image_url"] = usr.profile_background_image_url
#         status["profile_image_url"] = usr.profile_image_url
#         status["profile_link_color"] = usr.profile_link_color
#         status["user_url"] = usr.url
#         status["profile_sidebar_fill_color"] = usr.profile_sidebar_fill_color
#         status["user_screen_name"] = usr.screen_name

#         twitter_statuses.append(status)

# #    return render_template('social_media.html', nav=nav_init(), tweets=twitter_statuses)


#if __name__ == "__about__":
#    app.run(debug=True)
