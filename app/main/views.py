from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response, jsonify
from flask.ext.login import login_required, current_user
from flask.ext.sqlalchemy import get_debug_queries
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm,\
    CommentForm
from .. import db
from ..models import Permission, Role, User, \
                    IUCNStatus, ESAStatus, TaxonomicStatus, GrowthType, GrowthFormRaunkiaer, ReproductiveRepetition, \
                    DicotMonoc, AngioGymno, SourceType, Database, Purpose, MissingData, ContentEmail, Ecoregion, Continent, StageTypeClass, \
                    TransitionType, MatrixComposition, Season, StudiedSex, Captivity, Species, Taxonomy, PlantTrait, \
                    Publication, Study, AuthorContact, AdditionalSource, Population, Stage, StageType, Treatment, TreatmentType, \
                    MatrixStage, MatrixValue, Matrix, Interval, Bussy, VectorAvailability, StageClassInfo, Small
from ..decorators import admin_required, permission_required


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['FLASKY_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n'
                % (query.statement, query.parameters, query.duration,
                   query.context))
    return response


@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'


@main.route('/', methods=['GET', 'POST'])
def index():
 
    return render_template('index.html')


@main.route('/meta-tables/')
# @login_required
def meta_tables_json():

    # Constructing dict for meta tables, ordering by main Class
    meta_tables = {"Species" : {"IUCNStatus" : [], "ESAStatus" : []}, "Taxonomy" : {"TaxonomicStatus" : []}, "PlantTrait" : {"GrowthType" : [], \
                   "GrowthFormRaunkiaer" : [], "ReproductiveRepetition" : [], "DicotMonoc" : [], "AngioGymno" : [] }, \
                   "Publication" : {"SourceType" : [], "Database" : [], "Purpose" : [], "MissingData" : [] }, \
                   "AuthorContact" : { "ContentEmail" : [] }, "Population" : {"Ecoregion" : [], "Continent" : [] }, \
                   "StageType" : { "StageTypeClass" : [] }, "MatrixValue" : { "TransitionType" : [] }, \
                   "Matrix" : {"MatrixComposition" : [], "Season" : [], "StudiedSex" : [], "Captivity" : []}, \
                   "Bussy" : { "VectorAvailability" : [],  "StageClassInfo": [], "Small": [] }}

    meta_tables["Species"]["IUCNStatus"].extend(IUCNStatus.query.all())
    meta_tables["Species"]["ESAStatus"].extend(ESAStatus.query.all())
    meta_tables["Taxonomy"]["TaxonomicStatus"].extend(TaxonomicStatus.query.all())
    meta_tables["PlantTrait"]["GrowthType"].extend(GrowthType.query.all())
    meta_tables["PlantTrait"]["GrowthFormRaunkiaer"].extend(GrowthFormRaunkiaer.query.all())
    meta_tables["PlantTrait"]["ReproductiveRepetition"].extend(ReproductiveRepetition.query.all())
    meta_tables["PlantTrait"]["DicotMonoc"].extend(DicotMonoc.query.all())
    meta_tables["PlantTrait"]["AngioGymno"].extend(AngioGymno.query.all())
    meta_tables["Publication"]["SourceType"].extend(SourceType.query.all())
    meta_tables["Publication"]["Database"].extend(Database.query.all())
    meta_tables["Publication"]["Purpose"].extend(Purpose.query.all())
    meta_tables["Publication"]["MissingData"].extend(MissingData.query.all())
    meta_tables["AuthorContact"]["ContentEmail"].extend(ContentEmail.query.all())
    meta_tables["Population"]["Ecoregion"].extend(Ecoregion.query.all())
    meta_tables["Population"]["Continent"].extend(Continent.query.all())
    meta_tables["StageType"]["StageTypeClass"].extend(StageTypeClass.query.all())
    meta_tables["MatrixValue"]["TransitionType"].extend(TransitionType.query.all())
    meta_tables["Matrix"]["MatrixComposition"].extend(MatrixComposition.query.all())
    meta_tables["Matrix"]["Season"].extend(Season.query.all())
    meta_tables["Matrix"]["StudiedSex"].extend(StudiedSex.query.all())
    meta_tables["Matrix"]["Captivity"].extend(Captivity.query.all())
    meta_tables["Bussy"]["VectorAvailability"].extend(VectorAvailability.query.all())
    meta_tables["Bussy"]["StageClassInfo"].extend(StageClassInfo.query.all())
    meta_tables["Bussy"]["Small"].extend(Small.query.all())


    print meta_tables

    return render_template('meta.html', meta=meta_tables)

@main.route('/data/')
# @login_required
def data():
    species = Species.query.all()

    return render_template('data.html', species=species)

@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()    
    return render_template('user.html', user=user)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
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
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)