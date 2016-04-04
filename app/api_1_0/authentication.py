from flask import g, jsonify, redirect, url_for, request, current_app, render_template
from flask.ext.login import login_user, logout_user, login_required, \
    current_user
from .. import db
from flask.ext.httpauth import HTTPBasicAuth
from ..models import User, AnonymousUser, Role
from . import api
from .errors import unauthorized, forbidden

auth = HTTPBasicAuth()

@api.route('/connect')
def connect_account():
    user = current_user
    user.role = Role.query.filter_by(name='Developer').first()
    user.generate_auth_token()
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('api.home'))

@api.route('/sign-in')
def sign_in():
    redirect_to_sign_in = redirect('/auth/login')
    response = current_app.make_response(redirect_to_sign_in)
    response.set_cookie('request_path', value='api')
    return response

@api.route('/sign-up')
def sign_up():
    redirect_to_sign_up = redirect('/auth/register')
    response = current_app.make_response(redirect_to_sign_up)
    response.set_cookie('account_type', value='developer')
    return response

@api.route('/del-cookie')
def del_cookie():
    redirect_to_sign_up = redirect('/api/connect')
    response = current_app.make_response(redirect_to_sign_up)
    response.set_cookie('request_path', '', expires=0)
    return response

@auth.verify_password
@api.route('/verify_password/<email_or_token>/<password>')
def verify_password(email_or_token, password):
    if email_or_token == '':
        g.current_user = AnonymousUser()
        return True
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    user.verify_password(password)
    return get_token(g.current_user)


@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')


@api.before_request
@auth.login_required
def before_request():
    if not g.current_user.is_anonymous and \
            not g.current_user.confirmed:
        return forbidden('Unconfirmed account')


@api.route('/token')
def get_token(user):
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({'token': g.current_user.generate_auth_token(
        expiration=3600), 'expiration': 3600})
