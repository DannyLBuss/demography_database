from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_user, logout_user, login_required, \
    current_user
from . import admin
from .. import db
from ..models import User, Role
from ..email import send_email
from .forms import  EditProfileAdminForm
from ..decorators import admin_required, permission_required, crossdomain


@admin.route('/users')
@login_required
@admin_required
def users_page():
    users = User.query.all()
    return render_template('admin/users.html', users = users)

# edit a different profile as admin
@admin.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.about_me = form.about_me.data
        user.institute = form.institute.data
        user.institute_confirmed = form.institute_confirmed.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('admin.users_page'))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.about_me.data = user.about_me
    form.institute.data = user.institute
    form.institute_confirmed.data = user.institute_confirmed
    return render_template('admin/user_form.html', form=form, user=user)