from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_user, logout_user, login_required, \
    current_user
from . import admin
from .. import db
from ..models import User, Role
from ..email import send_email


@admin.route('/users')
#@login_required
def users_page():
    users = User.query.all()
    return render_template('admin/users.html', users = users)