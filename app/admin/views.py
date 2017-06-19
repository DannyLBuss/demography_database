from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_user, logout_user, login_required, \
    current_user
from . import admin
from .. import db
from ..models import User, Role, Institute, DigitizationProtocol
from ..email import send_email
from .forms import  EditProfileAdminForm, EditInstituteAdminForm, EditProtocolAdminForm
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
@admin_required
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
        db.session.commit()
        
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

@admin.route('/institutes')
@login_required
@admin_required
def institutes_page():
    institutes = Institute.query.all()
    return render_template('admin/institutes.html', institutes = institutes)

@admin.route('/edit-institute/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_institute_admin(id):
    institute = Institute.query.get_or_404(id)
    form = EditInstituteAdminForm(institute=institute)
    if form.validate_on_submit():
        
        institute.institution_name = form.institution_name.data
        institute.institution_short = form.institution_short.data
        institute.main_contact_email = form.main_contact_email.data
        institute.main_contact_name = form.main_contact_name.data
        institute.institution_address = form.institution_address.data
        institute.research_group = form.research_group.data
        institute.date_joined = form.email.data
        institute.department = form.department.data
        institute.country = form.country.data
        institute.website = form.website.data
        db.session.commit()

        flash('The profile has been updated.')
        return redirect(url_for('admin.institute_page'))
    
    form.institution_name.data = institute.institution_name
    form.institution_short.data = institute.institution_short
    form.main_contact_email.data = institute.main_contact_email 
    form.main_contact_name.data = institute.main_contact_name
    form.institution_address.data = institute.institution_address
    form.research_group.data = institute.research_group
    #form.email.data = institute.date_joined 
    form.department.data = institute.department
    form.country.data = institute.country 
    form.website.data = institute.website 

    return render_template('admin/institute_form.html', form=form, institute=institute)

@admin.route('/new-institute', methods=['GET', 'POST'])
@login_required
@admin_required
def new_institute_admin():
    institute = Institute()
    form = EditInstituteAdminForm(institute=institute)
    flash('Date format must be "YYYY-mm-dd".')
    if form.validate_on_submit():
        
        institute.institution_name = form.institution_name.data
        institute.institution_short = form.institution_short.data
        institute.main_contact_email = form.main_contact_email.data
        institute.main_contact_name = form.main_contact_name.data
        institute.institution_address = form.institution_address.data
        institute.research_group = form.research_group.data
        #institute.date_joined = form.email.data
        institute.department = form.department.data
        institute.country = form.country.data
        institute.website = form.website.data
        
        db.session.add(institute)
        db.session.commit()

        flash('The institute has been added')
        return redirect(url_for('admin.institutes_page'))

    return render_template('admin/institute_form.html', form=form)

@admin.route('/new_protocol', methods=['GET', 'POST'])
@login_required
@admin_required
def new_protocol_admin():
    protocol = DigitizationProtocol()
    form = EditProtocolAdminForm(protocol=protocol)
    if form.validate_on_submit():
        
        protocol.field_name = form.field_name.data
        protocol.name_in_csv = form.name_in_csv.data
        protocol.database_model = form.database_model.data
        protocol.field_description = form.field_description.data
        protocol.field_short_description = form.field_short_description.data

        
        db.session.add(protocol)
        db.session.commit()

        flash('The protocol entry has been added')
        return redirect(url_for('main.protocol_page'))

    return render_template('admin/protocol_form.html', form=form)

@admin.route('/edit_protocol/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_protocol_admin():
    protocol = DigitizationProtocol.query.get_or_404(id)
    form = EditProtocolAdminForm(protocol=protocol)
    if form.validate_on_submit():
        
        protocol.field_name = form.field_name.data
        protocol.name_in_csv = form.name_in_csv.data
        protocol.database_model = form.database_model.data
        protocol.field_description = form.field_description.data
        protocol.field_short_description = form.field_short_description.data

        db.session.add(protocol)
        db.session.commit()

        flash('The protocol entry has been edited')
        return redirect(url_for('main.protocol_page'))
    
    form.field_name.data = protocol.field_name 
    form.name_in_csv.data = protocol.name_in_csv
    form.database_model.data = protocol.database_model
    form.field_description.data = protocol.field_description
    form.field_short_description.data = protocol.field_short_description

    return render_template('admin/protocol_form.html', form=form)

