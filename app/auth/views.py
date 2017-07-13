from flask import render_template, redirect, request, url_for, flash, abort
from flask.ext.login import login_user, logout_user, login_required, \
    current_user, session
from . import auth
from .. import db
from ..models import User, Role
from ..google_auth_class import Auth
from ..email import send_email
from .forms import LoginForm, RegistrationForm, ChangePasswordForm,\
    PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm
from requests_oauthlib import OAuth2Session
import json
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    
# google auth stuff
def get_google_auth(state=None, token=None):
    if token:
        return OAuth2Session(Auth.CLIENT_ID, token=token)
    if state:
        return OAuth2Session(
            Auth.CLIENT_ID,
            state=state,
            redirect_uri=Auth.REDIRECT_URI)
    oauth = OAuth2Session(
        Auth.CLIENT_ID,
        redirect_uri=Auth.REDIRECT_URI,
        scope=Auth.SCOPE)
    return oauth

# not sure what this does
@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint[:5] != 'auth.' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))

# where you get directed if you try to log in but you haven't confirmed your email yet
@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

# log in page
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    print request.cookies
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            try:
                request_path = request.cookies['request_path']
            except KeyError:
                return redirect(request.args.get('next') or url_for('main.index'))
            else:
                if request_path == "api":
                    return redirect(request.args.get('next') or url_for('api.del_cookie'))
                else:
                    return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)

#google open auth2 log in page
@auth.route('/login_with_google')
def login_with_google():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    google = get_google_auth()
    auth_url, state = google.authorization_url(
        Auth.AUTH_URI, access_type='offline')
    session['oauth_state'] = state
    return render_template('auth/login_google.html', auth_url=auth_url)

# google auth callback
@auth.route('/oauth2callback')
def callback():

    # Redirect user to home page if already logged in.
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if 'error' in request.args:
        if request.args.get('error') == 'access_denied':
            return 'You denied access.'
        return 'Error encountered.'
    if 'code' not in request.args and 'state' not in request.args:
        return redirect(url_for('auth.login_with_google'))
    else:
        # Execution reaches here when user has
        # successfully authenticated our app.
        google = get_google_auth(state=session['oauth_state'])
        try:
            token = google.fetch_token(
            Auth.TOKEN_URI,
            client_secret=Auth.CLIENT_SECRET,
            authorization_response=request.url)
        except:
            return redirect(url_for('auth.login_with_google'))
        google = get_google_auth(token=token)
        resp = google.get(Auth.USER_INFO)
        if resp.status_code == 200:
            
            user_data = resp.json()
            email = user_data['email']
            user = User.query.filter_by(email=email).first()
            
            if user is not None:
                next_form = False
                flash("You have succesfully logged in")
            else:
                next_form = True
                
            if user is None:
                user = User()
                user.role = Role.query.filter_by(name="User").first()
                user.email = email
                
            user.name = user_data['name'] # gets name data, doesn't have to be unique
            
            #generating a unique username
            username_auto = user_data['name'].replace(" ", "_").lower() # autogenerate from oauth2 json
            if username_auto == "": # to avoid errors where it doesn't get name data from oauth2
                username_auto = "anon"
            while User.query.filter_by(username=username_auto).first() is not None: # test to see if the autogenerated name exists
                username_auto = username_auto + "_duplicate" # adds "_dupe" to username until it becomes a unique name
            
            user.username = username_auto
            user.confirmed = 1
            user.tokens = json.dumps(token)
            db.session.add(user)
            db.session.commit()
            login_user(user)

            if next_form == True:
                return redirect(url_for('main.index'))
                flash("You have not created a new account in the database, please try again")
            else:
                return redirect(url_for('main.index'))

        return 'Could not fetch your information.'
    
# #register google page
# @auth.route('/registergoogle', methods=['GET', 'POST'])
# def register_google(user = current_user):

        
#     try:
#         account_type = request.cookies['account_type']
#     except KeyError:
#         account_type = ''
        
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         user = User(email=form.email.data,
#                     username=form.username.data,
#                     password=form.password.data,
#                     name = form.name.data,
#                     role = form.role.data,
#                     institute = form.institute.data)

#         if account_type == 'developer':
#             user.role = Role.query.filter_by(name='Developer').first()
#             user.generate_auth_token(3600)

#         db.session.add(user)
#         db.session.commit()

#         return redirect(url_for('auth.index'))
#     return render_template('auth/register.html', form=form, account_type=account_type)

#register page
@auth.route('/register', methods=['GET', 'POST'])
def register():

    try:
        account_type = request.cookies['account_type']
    except KeyError:
        account_type = ''

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data,
                    name = form.name.data,
                    #role = form.role.data,
                    institute = form.institute.data)

        if account_type == 'developer':
            user.role = Role.query.filter_by(name='Developer').first()
            user.generate_auth_token(3600)

        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form, account_type=account_type)

# log out page which redirects you to the homepage
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

# confirming your email address 
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))

# resending confirmation email
@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))

# change password
@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash('Your password has been updated.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password.')
    return render_template("auth/change_password.html", form=form)

# reset your password, requesting an email to reset password
@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Reset Your Password',
                       'auth/email/reset_password',
                       user=user, token=token,
                       next=request.args.get('next'))
        flash('An email with instructions to reset your password has been '
              'sent to you.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)

# using the link sent in the email to reset password
@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)

# change email, send email to new address
@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, 'Confirm your email address',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash('An email with instructions to confirm your new email '
                  'address has been sent to you.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.')
    return render_template("auth/change_email.html", form=form)

# use email sent to you to change your email
@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('Your email address has been updated.')
    else:
        flash('Invalid request.')
    return redirect(url_for('main.index'))
