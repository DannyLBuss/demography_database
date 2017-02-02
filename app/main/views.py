from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response, jsonify
from flask.ext.login import login_required, current_user
from flask.ext.sqlalchemy import get_debug_queries
from . import main
from .forms import EditProfileForm, EditProfileAdminForm

from ..data_manage.forms import SpeciesForm, TaxonomyForm, TraitForm, PopulationForm, MatrixForm, PublicationForm, StudyForm, DeleteForm

import random

from .. import db
from ..models import Permission, Role, User, \
                    IUCNStatus, ESAStatus, OrganismType, GrowthFormRaunkiaer, ReproductiveRepetition, \
                    DicotMonoc, AngioGymno, SpandExGrowthType, SourceType, Database, Purpose, MissingData, ContentEmail, Ecoregion, Continent, InvasiveStatusStudy, InvasiveStatusElsewhere, StageTypeClass, \
                    TransitionType, MatrixComposition, StartSeason, EndSeason, StudiedSex, Captivity, Species, Taxonomy, PurposeEndangered, PurposeWeed, Trait, \
                    Publication, Study, AuthorContact, AdditionalSource, Population, Stage, StageType, Treatment, \
                    MatrixStage, MatrixValue, Matrix, Interval, Fixed, Small, CensusTiming, Institute, Status, Version, ChangeLogger
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


#@main.route('/shutdown')
#def server_shutdown():
#    if not current_app.testing:
#        abort(404)
#    shutdown = request.environ.get('werkzeug.server.shutdown')
#    if not shutdown:
#        abort(500)
#    shutdown()
#    return 'Shutting down...'


@main.route('/', methods=['GET', 'POST'])
def index():
#    species = Species.query.filter_by(version_latest=1).filter(Species.image_path != None).all()
#    number = len(species)
#    species2 = []
#    for i in range(1,5):
#        random_int = random.randint(0,number-1)
#        s = species[random_int]
#        species2.append(s)
    return render_template('index.html') #,species2 = species2)


@main.route('/meta-tables/')
# @login_required
def meta_tables_json():

    # Constructing dict for meta tables, ordering by main Class
    meta_tables = {"User" : {"Institute" : []},
                   "Species" : {"IUCNStatus" : [], "ESAStatus" : []}, "Taxonomy" : {}, "Trait" : {"OrganismType" : [], \
                   "GrowthFormRaunkiaer" : [], "ReproductiveRepetition" : [], "DicotMonoc" : [], "AngioGymno" : [], "SpandExGrowthType" : [] }, \
                   "Publication" : {"SourceType" : [], "Database" : [], "Purpose" : [], "MissingData" : [] }, \
                   "AuthorContact" : { "ContentEmail" : [] }, "Population" : {"Ecoregion" : [], "Continent" : [] , "InvasiveStatusStudy" : [], "InvasiveStatusElsewhere" : []}, \
                   "StageType" : { "StageTypeClass" : [] }, "MatrixValue" : { "TransitionType" : [] }, \
                   "Matrix" : {"MatrixComposition" : [], "StartSeason" : [], "EndSeason" : [], "StudiedSex" : [], "Captivity" : []}, \
                   "Fixed" : { "Small": [], "CensusTiming" : [] },
                   "Study" : { "PurposeEndangered": [], "PurposeWeed" : []}}

    meta_tables["User"]["Institute"].extend(Institute.query.all())
    meta_tables["Species"]["IUCNStatus"].extend(IUCNStatus.query.all())
    meta_tables["Species"]["ESAStatus"].extend(ESAStatus.query.all())
    meta_tables["Trait"]["OrganismType"].extend(OrganismType.query.all())
    meta_tables["Trait"]["GrowthFormRaunkiaer"].extend(GrowthFormRaunkiaer.query.all())
    meta_tables["Trait"]["ReproductiveRepetition"].extend(ReproductiveRepetition.query.all())
    meta_tables["Trait"]["DicotMonoc"].extend(DicotMonoc.query.all())
    meta_tables["Trait"]["AngioGymno"].extend(AngioGymno.query.all())
    meta_tables["Trait"]["SpandExGrowthType"].extend(SpandExGrowthType.query.all())
    meta_tables["Publication"]["SourceType"].extend(SourceType.query.all())
    meta_tables["Publication"]["Database"].extend(Database.query.all())
    meta_tables["Publication"]["Purpose"].extend(Purpose.query.all())
    meta_tables["Publication"]["MissingData"].extend(MissingData.query.all())
    meta_tables["AuthorContact"]["ContentEmail"].extend(ContentEmail.query.all())
    meta_tables["Population"]["Ecoregion"].extend(Ecoregion.query.all())
    meta_tables["Population"]["Continent"].extend(Continent.query.all())
    meta_tables["Population"]["InvasiveStatusStudy"].extend(InvasiveStatusStudy.query.all())
    meta_tables["Population"]["InvasiveStatusElsewhere"].extend(InvasiveStatusElsewhere.query.all())
    meta_tables["StageType"]["StageTypeClass"].extend(StageTypeClass.query.all())
    meta_tables["MatrixValue"]["TransitionType"].extend(TransitionType.query.all())
    meta_tables["Matrix"]["MatrixComposition"].extend(MatrixComposition.query.all())
    meta_tables["Matrix"]["StartSeason"].extend(StartSeason.query.all())
    meta_tables["Matrix"]["EndSeason"].extend(EndSeason.query.all())
    meta_tables["Matrix"]["StudiedSex"].extend(StudiedSex.query.all())
    meta_tables["Matrix"]["Captivity"].extend(Captivity.query.all())
    meta_tables["Fixed"]["Small"].extend(Small.query.all())
    meta_tables["Fixed"]["CensusTiming"].extend(CensusTiming.query.all())
    meta_tables["Study"]["PurposeEndangered"].extend(PurposeEndangered.query.all())
    meta_tables["Study"]["PurposeWeed"].extend(PurposeWeed.query.all())

    print meta_tables

    return render_template('meta.html', meta=meta_tables)

# now defunct 'display all data' page
@main.route('/data/')
# @login_required
def data():
    species = Species.query.all()

    return render_template('data.html', species=species)

### TABLE PAGES
# the big table of species
#doesn't work at the moment...
@main.route('/species-table/')
# @login_required
def species_table():
    # species = Species.query.all()
    species = Species.query.all()
    return render_template('species_table_template.html', species=species)

# the big table of publications
@main.route('/publications-table/')
# @login_required
def publications_table():
    publications = Publication.query.all()
    return render_template('publications_table_template.html', publications=publications)

###############################################################################################################################
### OVERVIEW PAGES
# species overview page
@main.route('/species/<int:id>/overview')
# @login_required
def species_page(id):
    #get species
    species = Species.query.filter_by(id=id).first_or_404()
    print(species) #check
    
    #get taxonomy
    taxonomy = Taxonomy.query.filter_by(species_id=species.id).first()
    print(taxonomy) #check
    
    #get traits
    trait = Trait.query.filter_by(species_id=species.id).first()
    print(trait) #check
    
    # querying studies returns a weird thing so I have to do this first
    all_studies = Study.query.filter_by(species_id=species.id)
    
    # generate empty lists to store studies and publications
    studies = []
    publications = []
    for study in all_studies:
        studies.append(study)
        publications.append(Publication.query.filter_by(id=study.publication_id).first())
    # remove duplicates in publications
    publications = list(set(publications))
    
    print(studies) # check
    print(publications) #check
    
    #get populations
    populations = []
    for study in studies:
        populations_temp = (Population.query.filter_by(study_id=study.id))
        for populations_i in populations_temp:
            populations.append(populations_i)
    print(populations)
    
    #get matrices
    matrices = []
    for population in populations:
        matrices_temp = Matrix.query.filter_by(population_id=population.id)
        for matrices_i in matrices_temp:
            matrices.append(matrices_i)
    print(matrices)
    
    return render_template('species_template.html',species = species, taxonomy = taxonomy, trait = trait, publications = publications, studies = studies, populations = populations, matrices = matrices)

# publication overview page
# NEEDS UPDATE OR MERGER INTO SPECIES OVERVIEW TEMPLATE
@main.route('/publication/<int:id>')
# @login_required
def publication_page(id):
    publication = Publication.query.filter_by(id=id).first_or_404()
    return render_template('source_template.html',publication = publication)

# Taxonomic explorer
# NEEDS FIX AT SPECIES LEVEL
# DOES NOT WORK IN FIREFOX
@main.route('/explorer/<taxon_level>/<taxon>')
# @login_required
def explorer(taxon_level,taxon):
    if taxon_level == "life":
        taxon_list = Taxonomy.query.all()
        next_taxon_level = "kingdom"
        tax_pos = 0
    elif taxon_level == "kingdom":
        taxon_list = Taxonomy.query.filter_by(kingdom=taxon)
        next_taxon_level = "phylum"
        tax_pos = 1
    elif taxon_level == "phylum":
        taxon_list = Taxonomy.query.filter_by(phylum=taxon)
        next_taxon_level = "class" 
        tax_pos = 2
    elif taxon_level == "class":
        taxon_list = Taxonomy.query.filter_by(tax_class=taxon)
        next_taxon_level = "order"
        tax_pos = 3
    elif taxon_level == "order":
        taxon_list = Taxonomy.query.filter_by(tax_order=taxon)
        next_taxon_level = "family"
        tax_pos = 4
    elif taxon_level == "family":
        taxon_list = Taxonomy.query.filter_by(family=taxon)
        next_taxon_level = "Species"
        tax_pos = 5
    
    
    return render_template('explorer_template.html',taxon=taxon,taxon_list = taxon_list,taxon_level=taxon_level,next_taxon_level=next_taxon_level, tax_pos = tax_pos)

# contribute
@main.route('/contribute-data')
def contribute_data():
    return render_template('contribute_data.html')

#education
@main.route('/education')
def education():
    return render_template('about/education.html')

# education ppm
@main.route('/education_ppm')
def education_ppm():
    return render_template('education_pages/education_matrix_modelling.html')

#news
@main.route('/news')
def news():
    return render_template('about/news.html')

#team
@main.route('/team')
def team():
    return render_template('about/team.html')

#faqs
@main.route('/FAQs')
def FAQs():
    return render_template('about/FAQs.html')

#history
@main.route('/history')
def history():
    return render_template('about/history.html')

# funding
@main.route('/funding')
def funding():
    return render_template('about/funding.html')

#publications
@main.route('/publications')
def publications():
    return render_template('about/publications.html')

###############################################################################################################################
### NEW DATA INPUT FORMS

@main.route('/species/new', methods=['GET', 'POST'])
def species_new_form():
    form = SpeciesForm()
    if form.validate_on_submit():
        species = Species()
        
        species.species_accepted = form.species_accepted.data
        species.species_common = form.species_common.data
        species.iucn_status = form.iucn_status.data
        species.esa_status = form.esa_status.data
        species.invasive_status = form.invasive_status.data
        species.gbif_taxon_key = form.gbif_taxon_key.data
        species.image_path = form.image_path.data
        species.image_path2 = form.image_path2.data
        
        db.session.add(species)
        db.session.commit()

        return redirect(url_for('.species_page',id=species.id))
    
    return render_template('data_entry/generic_form.html', form=form)

@main.route('/taxonomy/new/species=<int:id_sp>', methods=['GET', 'POST'])
def taxonomy_new_form(id_sp):
    species = Species.query.get_or_404(id_sp)
    form = TaxonomyForm()
    
    if form.validate_on_submit():
        taxonomy = Taxonomy()
        taxonomy.species_id = species.id
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
        
        db.session.add(taxonomy)
        db.session.commit()
        
        return redirect(url_for('.species_page',id=id_sp))
    
    return render_template('data_entry/generic_form.html', form=form,species = species)

@main.route('/traits/new/species=<int:id_sp>', methods=['GET', 'POST'])
def trait_new_form(id_sp):
    species = Species.query.get_or_404(id_sp)
    form = TraitForm()
    
    if form.validate_on_submit():
        Trait = Trait()
        trait.species_id = species.id
        
        trait.max_height = form.max_height.data
        trait.organism_type = form.organism_type.data
        trait.growth_form_raunkiaer = form.growth_form_raunkiaer.data
        trait.reproductive_repetition = form.reproductive_repetition.data
        trait.dicot_monoc = form.dicot_monoc.data
        trait.angio_gymno = form.angio_gymno.data
        return redirect(url_for('.species_page',id=id_sp))
    
    return render_template('data_entry/generic_form.html', form=form,species = species)

@main.route('/publication/new', methods=['GET', 'POST'])
def new_publication_form():
    form = PublicationForm()
    
    if form.validate_on_submit():
        publication = Publication()
        
        publication.source_type = form.source_type.data
        publication.authors = form.authors.data 
        publication.editors = form.editors.data
        publication.pub_title = form.pub_title.data
        publication.journal_book_conf = form.journal_book_conf.data
        publication.year = form.year.data
        publication.volume = form.volume.data
        publication.pages = form.pages.data
        publication.publisher = form.publisher.data
        publication.city = form.city.data
        publication.country = form.country.data
        publication.institution = form.institution.data
        publication.DOI_ISBN = form.DOI_ISBN.data
        publication.name = form.pub_name.data
        publication.corresponding_author = form.corresponding_author.data
        publication.email = form.email.data
        publication.purposes_id = form.purposes.data
        publication.embargo = form.embargo.data
        publication.missing_data = form.missing_data.data
        publication.additional_source_string = form.additional_source_string.data  
        
        db.session.add(publication)
        db.session.commit()
        
        return redirect(url_for('.publication_page',id=publication.id))
    
    return render_template('data_entry/publication_form.html',form=form)

@main.route('/population/new/publication=<int:id_pub>/choose_species', methods=['GET'])
def choose_species(id_pub):
    publication = Publication.query.get_or_404(id_pub)
    species = Species.query.all()
    
    return render_template('data_entry/choose_species.html',publication=publication,species=species)
    
@main.route('/population/new/publication=<int:id_pub>/species=<int:id_sp>', methods=['GET', 'POST'])
def population_new_form(id_pub,id_sp):
    publication = Publication.query.get_or_404(id_pub)
    species = Species.query.get_or_404(id_sp)
    form = PopulationForm()
    
    if form.validate_on_submit():
        population = Population()
        population.publication_id = id_pub
        population.species_id = id_sp
        
        population.name = form.name.data
        population.ecoregion = form.ecoregion.data
        population.country = form.country.data
        population.continent = form.continent.data
        population.latitude = form.latitude.data
        population.longitude = form.longitude.data
        population.altitude = form.altitude.data
        
        db.session.add(population)
        db.session.commit()
        
        return redirect(url_for('.publication_page',id=id_pub))
    
    return render_template('data_entry/generic_form.html', form=form, publication=publication, species=species)

# USER + PROFILE PAGES
# User
@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()    
    return render_template('user.html', user=user)

# edit profile
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

# edit a different profile as admin
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


