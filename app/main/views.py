from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response, jsonify
from flask.ext.login import login_required, current_user
from flask.ext.sqlalchemy import get_debug_queries
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm, CommentForm
from ..compadre.forms import SpeciesForm, TaxonomyForm, PlantTraitForm, PopulationForm
from .. import db
from ..models import Permission, Role, User, \
                    IUCNStatus, ESAStatus, TaxonomicStatus, GrowthType, GrowthFormRaunkiaer, ReproductiveRepetition, \
                    DicotMonoc, AngioGymno, SourceType, Database, Purpose, MissingData, ContentEmail, Ecoregion, Continent, StageTypeClass, \
                    TransitionType, MatrixComposition, Season, StudiedSex, Captivity, Species, Taxonomy, PlantTrait, \
                    Publication, Study, AuthorContact, AdditionalSource, Population, Stage, StageType, Treatment, TreatmentType, \
                    MatrixStage, MatrixValue, Matrix, Interval, Fixed, VectorAvailability, StageClassInfo, Small
from ..decorators import admin_required, permission_required, crossdomain


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
                   "Fixed" : { "VectorAvailability" : [],  "StageClassInfo": [], "Small": [] }}

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
    meta_tables["Fixed"]["VectorAvailability"].extend(VectorAvailability.query.all())
    meta_tables["Fixed"]["StageClassInfo"].extend(StageClassInfo.query.all())
    meta_tables["Fixed"]["Small"].extend(Small.query.all())


    print meta_tables

    return render_template('meta.html', meta=meta_tables)

@main.route('/data/')
# @login_required
def data():
    species = Species.query.all()

    return render_template('data.html', species=species)

@main.route('/matrix/<species_id>/<pop_id>/<mat_id>')
def matrix(species_id,pop_id,mat_id):
    species = Species.query.filter_by(id=species_id).first_or_404()
    population = Population.query.filter_by(id=pop_id).first_or_404()
    matrix = Matrix.query.filter_by(id=mat_id).first_or_404()
    return render_template('matrix.html', species=species, population=population, matrix=matrix)

@main.route('/species-table/')
# @login_required
def species_table():
    species = Species.query.all()
    return render_template('species_table_template.html', species=species)

@main.route('/publications-table/')
# @login_required
def publications_table():
    publications = Publication.query.all()
    return render_template('publications_table_template.html', publications=publications)

@main.route('/species/<int:id>/overview')
# @login_required
def species_page(id):
    species = Species.query.filter_by(id=id).first_or_404()
    return render_template('species_template.html',species = species)

@main.route('/publication/<int:id>')
# @login_required
def publication_page(id):
    publication = Publication.query.filter_by(id=id).first_or_404()
    return render_template('source_template.html',publication = publication)

# SPECIES/TAXONOMY/TRAIT FORMS
@main.route('/species/<int:id>/edit', methods=['GET', 'POST'])
def species_form(id):
    species = Species.query.get_or_404(id)
    form = SpeciesForm(species=species)

    if form.validate_on_submit():
        species.species_accepted = form.species_accepted.data
        species.iucn_status = form.iucn_status.data
        species.esa_status = form.esa_status.data
        species.invasive_status = form.invasive_status.data

        species.save_as_version()
        species_name = species.species_accepted
        flash('The species infomation has been updated.')
        return redirect(url_for('.species_page',id=id))
    
    form.species_accepted.data = species.species_accepted
    form.iucn_status.udata = species.iucn_status
    form.esa_status.data = species.esa_status
    form.invasive_status.data = species.invasive_status
    
    return render_template('species_form.html', form=form, species=species)

@main.route('/taxonomy/<int:id>/edit', methods=['GET', 'POST'])
def taxonomy_form(id):
    taxonomy = Taxonomy.query.get_or_404(id)
    species = Species.query.get_or_404(taxonomy.species_id)
    form = TaxonomyForm(taxonomy=taxonomy)
    
    if form.validate_on_submit():
        taxonomy.species_author = form.species_author.data
        taxonomy.authority = form.authority.data
        taxonomy.taxonomic_status = form.taxonomic_status.data
        taxonomy.tpl_version = form.tpl_version.data
        taxonomy.infraspecies_accepted = form.infraspecies_accepted.data
        taxonomy.species_epithet_accepted = form.species_epithet_accepted.data 
        taxonomy.genus_accepted = form.genus_accepted.data
        taxonomy.genus = form.genus.data
        taxonomy.family = form.family.data
        taxonomy.tax_order = form.tax_order.data
        taxonomy.tax_class = form.tax_class.data
        taxonomy.phylum = form.phylum.data
        taxonomy.kingdom = form.kingdom.data
        flash('The taxonomy has been updated.')
        species_name = species.species_accepted
        return redirect(url_for('.species_page',id=id))
    
    form.species_author.data = taxonomy.species_author
    form.authority.data = taxonomy.authority
    form.taxonomic_status.data = taxonomy.taxonomic_status
    form.tpl_version.data = taxonomy.tpl_version
    form.infraspecies_accepted.data = taxonomy.infraspecies_accepted
    form.species_epithet_accepted.data = taxonomy.species_epithet_accepted
    form.genus_accepted.data = taxonomy.genus_accepted
    form.genus.data = taxonomy.genus
    form.family.data = taxonomy.family
    form.tax_order.data = taxonomy.tax_order
    form.tax_class.data = taxonomy.tax_class
    form.phylum.data = taxonomy.phylum
    form.kingdom.data = taxonomy.kingdom

    return render_template('species_form.html', form=form, taxonomy=taxonomy,species = species)

@main.route('/traits/<int:id>/edit', methods=['GET', 'POST'])
def trait_form(id):
    planttrait = PlantTrait.query.get_or_404(id)
    species = Species.query.get_or_404(planttrait.species_id)
    form = PlantTraitForm(planttrait=planttrait)
    
    if form.validate_on_submit():
        planttrait.max_height = form.max_height.data
        planttrait.growth_type = form.growth_type.data
        planttrait.growth_form_raunkiaer = form.growth_form_raunkiaer.data
        planttrait.reproductive_repetition = form.reproductive_repetition.data
        planttrait.dicot_monoc = form.dicot_monoc.data
        planttrait.angio_gymno = form.angio_gymno.data
        flash('The plant trait infomation has been updated.')
        species_name = species.species_accepted
        return redirect(url_for('.species_page',species_name=species_name))
    
    form.max_height.data = planttrait.max_height
    form.growth_type.data = planttrait.growth_type
    form.growth_form_raunkiaer.data = planttrait.growth_form_raunkiaer
    form.reproductive_repetition.data = planttrait.reproductive_repetition
    form.dicot_monoc.data = planttrait.dicot_monoc
    form.angio_gymno.data = planttrait.angio_gymno
    return render_template('species_form.html', form=form, planttrait=planttrait,species = species)

@main.route('/population/<int:id>/edit', methods=['GET', 'POST'])
def population_form(id):
    population = Population.query.get_or_404(id)
    species = Species.query.get_or_404(population.species_id)
    form = PopulationForm(population=population)
    
    return render_template('species_form.html', form=form, population=population,species = species)


# end of forms

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
