from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response, jsonify
from flask.ext.login import login_required, current_user
from flask.ext.sqlalchemy import get_debug_queries
from . import user_zone
from .forms import EditProfileForm, EditUserListForm
from ..models import UserList, UserListEntry
from .. import db

# edit your own profile (non admin)
@user_zone.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = current_user
    print(user)
    print(current_user)
    form = EditProfileForm(user=user)
    if form.validate_on_submit():
        user.name = form.name.data
        user.username = form.username.data
        user.about_me = form.about_me.data
    
        # unconfirming institure if they change institute (non admins)
        if user.institute != form.institute.data and user.role_id != 1:
            user.institute_confirmed = 0
            
        user.institute = form.institute.data
    
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.name.data = user.name
    form.username.data = user.username
    form.about_me.data = user.about_me
    form.institute.data = user.institute
        
    return render_template('admin/user_form.html', form=form)


@user_zone.route('/', methods=['GET', 'POST'])
def area():
    user = current_user
    lists = (UserList.query.filter_by(user_id=user.id)).all()
    return render_template('user_area/area.html',user=user,lists=lists)


@user_zone.route('/edit_list/<int:id>', methods=['GET', 'POST'])
def edit_list():
    userlist = UserList.query.get_or_404(id)
    user = current_user
    form = EditUserListForm(userlist=userlist)
    
    if form.validate_on_submit():
        userlist.name = form.name.data
        userlist.description = form.description.data
        userlist.public = form.public.data
        userlist.DOI_ISBN = form.DOI_ISBN.data
        userlist.user_id = current_user.id
        
        flash('Your list has been updated')
        return redirect(url_for('.area'))
    
    form.name.data = userlist.name
    form.description.data = userlist.description
    form.public.data = userlist.public
    form.DOI_ISBN.data = userlist.DOI_ISBN
    
    return render_template('data_manage/generic_form.html', form=form)

@user_zone.route('/new_list', methods=['GET', 'POST'])
def new_list():
    userlist = UserList()
    user = current_user
    form = EditUserListForm(userlist=userlist)
    
    if form.validate_on_submit():
        userlist.name = form.name.data
        userlist.description = form.description.data
        userlist.public = form.public.data
        userlist.DOI_ISBN = form.DOI_ISBN.data
        userlist.user_id = current_user.id
        db.session.add(userlist)
        db.session.commit()
        
        flash('Your list has been created')
        return redirect(url_for('.area'))

    
    return render_template('data_manage/generic_form.html', form=form)
    