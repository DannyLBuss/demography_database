from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response, jsonify
from flask.ext.login import login_required, current_user
from flask.ext.sqlalchemy import get_debug_queries
from . import data_manage
from .. import db
from forms import SpeciesForm, TaxonomyForm, TraitForm, PopulationForm, PublicationForm, StudyForm, MatrixForm
from ..models import Permission, Role, User, \
                    IUCNStatus, ESAStatus, OrganismType, GrowthFormRaunkiaer, ReproductiveRepetition, \
                    DicotMonoc, AngioGymno, SpandExGrowthType, SourceType, Database, Purpose, MissingData, ContentEmail, Ecoregion, Continent, InvasiveStatusStudy, InvasiveStatusElsewhere, StageTypeClass, \
                    TransitionType, MatrixComposition, StartSeason, EndSeason, StudiedSex, Captivity, Species, Taxonomy, Trait, \
                    Publication, Study, AuthorContact, AdditionalSource, Population, Stage, StageType, Treatment, \
                    MatrixStage, MatrixValue, Matrix, Interval, Fixed, Small, CensusTiming, Status, PurposeEndangered, PurposeWeed, Institute, ChangeLogger
from ..decorators import admin_required, permission_required, crossdomain

# Data management forms

# editing species information #updated 25/1/17
# edit_or_new is a string that is either "edit" or "new"
# id is an integer that is the id of the object being edited, if a new object is being created id = 0
@data_manage.route('/species/<string:edit_or_new>/<int:id>/', methods=['GET', 'POST'])
@login_required
def species_form(id,edit_or_new):
    
    if edit_or_new == "edit":
        species = Species.query.filter_by(id=id).first_or_404()
        species_old = Species.query.filter_by(id=id).first_or_404()
        form = SpeciesForm(species=species)
    else:
        species = Species()
        species_old = Species()
        form = SpeciesForm()

    if form.validate_on_submit():
        
        if edit_or_new == "edit":
            # PASTE CODE BLOCK
            species.add_to_logger(current_user,'species_accepted',species_old.species_accepted,form.species_accepted.data,'edit')
            species.add_to_logger(current_user,'species_common',species_old.species_common,form.species_common.data,'edit')
            species.add_to_logger(current_user,'iucn_status',species_old.iucn_status,form.iucn_status.data,'edit')
            species.add_to_logger(current_user,'esa_status',species_old.esa_status,form.esa_status.data,'edit')
            species.add_to_logger(current_user,'species_gisd_status',species_old.species_gisd_status,form.species_gisd_status.data,'edit')
            species.add_to_logger(current_user,'species_iucn_taxonid',species_old.species_iucn_taxonid,form.species_iucn_taxonid.data,'edit')
            species.add_to_logger(current_user,'species_iucn_population_assessed',species_old.species_iucn_population_assessed,form.species_iucn_population_assessed.data,'edit')
            species.add_to_logger(current_user,'invasive_status',species_old.invasive_status,form.invasive_status.data,'edit')
            species.add_to_logger(current_user,'gbif_taxon_key',species_old.gbif_taxon_key,form.gbif_taxon_key.data,'edit')
            species.add_to_logger(current_user,'image_path',species_old.image_path,form.image_path.data,'edit')
            species.add_to_logger(current_user,'image_path2',species_old.image_path2,form.image_path2.data,'edit')
            # END PAST CODE BLOCK
        
        species.species_accepted = form.species_accepted.data 
        species.species_common = form.species_common.data
        species.iucn_status = form.iucn_status.data
        species.esa_status = form.esa_status.data
        species.species_gisd_status = form.species_gisd_status.data #
        species.species_iucn_taxonid = form.species_iucn_taxonid.data #
        species.species_iucn_population_assessed = form.species_iucn_population_assessed.data #
        species.invasive_status = form.invasive_status.data
        species.gbif_taxon_key = form.gbif_taxon_key.data
        species.image_path = form.image_path.data
        species.image_path2 = form.image_path2.data                     
        
        if edit_or_new == "new":
            db.session.flush()
            db.session.add(species)
            db.session.commit()
            
            # COPY CODE BLOCK
            species.add_to_logger(current_user,'species_accepted',species_old.species_accepted,form.species_accepted.data,'edit')
            species.add_to_logger(current_user,'species_common',species_old.species_common,form.species_common.data,'edit')
            species.add_to_logger(current_user,'iucn_status',species_old.iucn_status,form.iucn_status.data,'edit')
            species.add_to_logger(current_user,'esa_status',species_old.esa_status,form.esa_status.data,'edit')
            species.add_to_logger(current_user,'species_gisd_status',species_old.species_gisd_status,form.species_gisd_status.data,'edit')
            species.add_to_logger(current_user,'species_iucn_taxonid',species_old.species_iucn_taxonid,form.species_iucn_taxonid.data,'edit')
            species.add_to_logger(current_user,'species_iucn_population_assessed',species_old.species_iucn_population_assessed,form.species_iucn_population_assessed.data,'edit')
            species.add_to_logger(current_user,'invasive_status',species_old.invasive_status,form.invasive_status.data,'edit')
            species.add_to_logger(current_user,'gbif_taxon_key',species_old.gbif_taxon_key,form.gbif_taxon_key.data,'edit')
            species.add_to_logger(current_user,'image_path',species_old.image_path,form.image_path.data,'edit')
            species.add_to_logger(current_user,'image_path2',species_old.image_path2,form.image_path2.data,'edit')
            #END COPY CODE BLOCK
            
        
        flash('The species infomation has been updated.')
        return redirect(url_for('main.species_page',id=species.id))
    
    form.species_accepted.data = species.species_accepted
    form.species_common.data = species.species_common
    form.iucn_status.data = species.iucn_status
    form.esa_status.data = species.esa_status
    form.species_gisd_status.data = species.species_gisd_status #
    form.species_iucn_taxonid.data = species.species_iucn_taxonid #
    form.species_iucn_population_assessed.data = species.species_iucn_population_assessed #
    form.invasive_status.data = species.invasive_status
    form.gbif_taxon_key.data = species.gbif_taxon_key
    form.image_path.data = species.image_path
    form.image_path2.data = species.image_path2
    
    return render_template('data_manage/generic_form.html', form=form, species=species)

# species information edit history
@data_manage.route('/species/<int:id>/edit-history')
@login_required
def species_edit_history(id):
    species = Species.query.filter_by(id=id).first_or_404()
    logged_changes = ChangeLogger.query.filter_by(object_type = "species",object_id = id)
    return render_template('edit_history.html',species = species, logged_changes = logged_changes)

# editing taxonomy # updated 25/1/17
@data_manage.route('/taxonomy/<string:edit_or_new>/<int:id>/species=<int:species_id>', methods=['GET', 'POST'])
@login_required
def taxonomy_form(id,species_id,edit_or_new):
    
    if edit_or_new == "edit": # if you are editing, get taxonomy object and create form
        taxonomy = Taxonomy.query.get_or_404(id)
        taxonomy_old = Taxonomy.query.get_or_404(id)
        form = TaxonomyForm(taxonomy=taxonomy)
        species = Species.query.filter_by(id=species_id).first_or_404()
    else: # if you are creating new, create empty taxonomy object and create form
        taxonomy = Taxonomy()
        taxonomy_old = Taxonomy()
        form = TaxonomyForm()
        species = Species.query.filter_by(id=species_id).first_or_404()
    
    if form.validate_on_submit(): #what happens when you press submit
        if edit_or_new == "edit":
            # COPY CODE BLOCK
            taxonomy.add_to_logger(current_user,'authority',taxonomy_old.authority,form.authority.data,'edit')
            taxonomy.add_to_logger(current_user,'tpl_version',taxonomy_old.tpl_version,form.tpl_version.data,'edit')
            taxonomy.add_to_logger(current_user,'infraspecies_accepted',taxonomy_old.infraspecies_accepted,form.infraspecies_accepted.data,'edit')
            taxonomy.add_to_logger(current_user,'species_epithet_accepted',taxonomy_old.species_epithet_accepted,form.species_epithet_accepted.data,'edit')
            taxonomy.add_to_logger(current_user,'genus_accepted',taxonomy_old.genus_accepted,form.genus_accepted.data,'edit')
            taxonomy.add_to_logger(current_user,'genus',taxonomy_old.genus,form.genus.data,'edit')
            taxonomy.add_to_logger(current_user,'family',taxonomy_old.family,form.family.data,'edit')
            taxonomy.add_to_logger(current_user,'tax_order',taxonomy_old.tax_order,form.tax_order.data,'edit')
            taxonomy.add_to_logger(current_user,'tax_class',taxonomy_old.tax_class,form.tax_class.data,'edit')
            taxonomy.add_to_logger(current_user,'phylum',taxonomy_old.phylum,form.phylum.data,'edit')
            taxonomy.add_to_logger(current_user,'kingdom',taxonomy_old.kingdom,form.kingdom.data,'edit')
            taxonomy.add_to_logger(current_user,'col_check_ok',taxonomy_old.col_check_ok,form.col_check_ok.data,'edit')
            #taxonomy.add_to_logger(current_user,'col_check_date',taxonomy_old.col_check_date,form.col_check_date.data,'edit')
            #END COPY CODE BLOCK
            
        taxonomy.authority = form.authority.data
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
        taxonomy.col_check_ok = form.col_check_ok.data #
        #taxonomy.col_check_date = form.col_check_date.data #
        
        if edit_or_new == "new":
            taxonomy.species_id = species.id
            
            db.session.flush()
            db.session.add(taxonomy)
            db.session.commit()
            # COPY CODE BLOCK
            taxonomy.add_to_logger(current_user,'authority',taxonomy_old.authority,form.authority.data,'edit')
            taxonomy.add_to_logger(current_user,'tpl_version',taxonomy_old.tpl_version,form.tpl_version.data,'edit')
            taxonomy.add_to_logger(current_user,'infraspecies_accepted',taxonomy_old.infraspecies_accepted,form.infraspecies_accepted.data,'edit')
            taxonomy.add_to_logger(current_user,'species_epithet_accepted',taxonomy_old.species_epithet_accepted,form.species_epithet_accepted.data,'edit')
            taxonomy.add_to_logger(current_user,'genus_accepted',taxonomy_old.genus_accepted,form.genus_accepted.data,'edit')
            taxonomy.add_to_logger(current_user,'genus',taxonomy_old.genus,form.genus.data,'edit')
            taxonomy.add_to_logger(current_user,'family',taxonomy_old.family,form.family.data,'edit')
            taxonomy.add_to_logger(current_user,'tax_order',taxonomy_old.tax_order,form.tax_order.data,'edit')
            taxonomy.add_to_logger(current_user,'tax_class',taxonomy_old.tax_class,form.tax_class.data,'edit')
            taxonomy.add_to_logger(current_user,'phylum',taxonomy_old.phylum,form.phylum.data,'edit')
            taxonomy.add_to_logger(current_user,'kingdom',taxonomy_old.kingdom,form.kingdom.data,'edit')
            taxonomy.add_to_logger(current_user,'col_check_ok',taxonomy_old.col_check_ok,form.col_check_ok.data,'edit')
            #taxonomy.add_to_logger(current_user,'col_check_date',taxonomy_old.col_check_date,form.col_check_date.data,'edit')
            #END COPY CODE BLOCK            
            
        flash('The taxonomy has been updated.')
        return redirect(url_for('main.species_page',id=species.id))
    
    if edit_or_new == "edit": #if you are editing a taxonomy, you need to fill the form with the data already available
        form.authority.data = taxonomy.authority
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
        form.col_check_ok.data = taxonomy.col_check_ok
        #form.col_check_date.data = 

    #Actually rendering the page
    return render_template('data_manage/generic_form.html', form=form, taxonomy = taxonomy, species=species)

@data_manage.route('/taxonomy/<int:id>/edit-history')
@login_required
def taxonomy_edit_history(id):
    taxonomy = Taxonomy.query.get_or_404(id)
    species = Species.query.get_or_404(taxonomy.species_id)
    logged_changes = ChangeLogger.query.filter_by(object_type = "taxonomy",object_id = id)
    return render_template('edit_history.html',taxonomy=taxonomy, species = species, logged_changes = logged_changes)

# editing traits
@data_manage.route('/traits/<string:edit_or_new>/<int:id>/species=<int:species_id>', methods=['GET', 'POST'])
@login_required
def trait_form(id,edit_or_new,species_id):
    
    if edit_or_new == "edit": # if you are editing, get trait object and create form
        trait = Trait.query.get_or_404(id)
        trait_old = Trait.query.get_or_404(id)
        form = TraitForm(trait=trait)
        species = Species.query.filter_by(id=species_id).first_or_404()
    else: # if you are creating new, create empty trait object and create form
        trait = Trait()
        trait_old = Trait()
        form = TraitForm()
        species = Species.query.filter_by(id=species_id).first_or_404()
        
    if form.validate_on_submit():
        if edit_or_new == "edit":
            # COPY CODE BLOCK
            trait.add_to_logger(current_user,'organism_type',trait_old.organism_type,form.organism_type.data,'edit')
            trait.add_to_logger(current_user,'growth_form_raunkiaer',trait_old.growth_form_raunkiaer,form.growth_form_raunkiaer.data,'edit')
            trait.add_to_logger(current_user,'reproductive_repetition',trait_old.reproductive_repetition,form.reproductive_repetition.data,'edit')
            trait.add_to_logger(current_user,'dicot_monoc',trait_old.dicot_monoc,form.dicot_monoc.data,'edit')
            trait.add_to_logger(current_user,'angio_gymno',trait_old.angio_gymno,form.angio_gymno.data,'edit')
            trait.add_to_logger(current_user,'spand_ex_growth_types',trait_old.spand_ex_growth_types,form.spand_ex_growth_types.data,'edit')
            # END CODE BLOCK
            
        trait.organism_type = form.organism_type.data
        trait.growth_form_raunkiaer = form.growth_form_raunkiaer.data
        trait.reproductive_repetition = form.reproductive_repetition.data
        trait.dicot_monoc = form.dicot_monoc.data
        trait.angio_gymno = form.angio_gymno.data
        trait.spand_ex_growth_types = form.spand_ex_growth_types.data
        
        if edit_or_new == "new":
            trait.species_id = species.id
            
            db.session.flush()
            db.session.add(trait)
            db.session.commit()
            # COPY CODE BLOCK
            trait.add_to_logger(current_user,'organism_type',trait_old.organism_type,form.organism_type.data,'edit')
            trait.add_to_logger(current_user,'growth_form_raunkiaer',trait_old.growth_form_raunkiaer,form.growth_form_raunkiaer.data,'edit')
            trait.add_to_logger(current_user,'reproductive_repetition',trait_old.reproductive_repetition,form.reproductive_repetition.data,'edit')
            trait.add_to_logger(current_user,'dicot_monoc',trait_old.dicot_monoc,form.dicot_monoc.data,'edit')
            trait.add_to_logger(current_user,'angio_gymno',trait_old.angio_gymno,form.angio_gymno.data,'edit')
            trait.add_to_logger(current_user,'spand_ex_growth_types',trait_old.spand_ex_growth_types,form.spand_ex_growth_types.data,'edit')
            # END CODE BLOCK
        
        flash('The trait infomation has been updated.')
        return redirect(url_for('main.species_page',id=species.id))
    
    
    
    form.organism_type.data = trait.organism_type
    form.growth_form_raunkiaer.data = trait.growth_form_raunkiaer
    form.reproductive_repetition.data = trait.reproductive_repetition
    form.dicot_monoc.data = trait.dicot_monoc
    form.angio_gymno.data = trait.angio_gymno
    form.spand_ex_growth_types.data = trait.spand_ex_growth_types
    
    return render_template('data_manage/generic_form.html', form=form, trait=trait,species = species)

# traits edit history
@data_manage.route('/traits/<int:id>/edit-history')
@login_required
def trait_edit_history(id):
    trait = Trait.query.get_or_404(id)
    species = Species.query.get_or_404(trait.species_id)
    logged_changes = ChangeLogger.query.filter_by(object_type = "trait",object_id = id)
    return render_template('edit_history.html',trait=trait, species = species, logged_changes = logged_changes)

# editing publication
@data_manage.route('/publication/<string:edit_or_new>/<int:id>', methods=['GET', 'POST'])
@login_required
def publication_form(id):
    if edit_or_new == "edit":
        publicication = Publication.query.filter_by(id=id).first_or_404()
        publication_old = Publication.query.filter_by(id=id).first_or_404()
        form = PublicationForm(publication=publication)
    else:
        publication = Publication()
        publication_old = Publication()
        form = PublicationForm()
    
    if form.validate_on_submit():
        
        #if edit_or_new == "edit":
            # COPY CODE BLOCK
            # END CODE BLOCK
            
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
        
        if edit_or_new == "new":
            
            db.session.flush()
            db.session.add(publication)
            db.session.commit()
            # COPY CODE BLOCK
            # END CODE BLOCK
            
        flash('The publication infomation has been updated.')
        return redirect(url_for('.publication_page',id=id))
    
    form.source_type.data = publication.source_type
    form.authors.data = publication.authors
    form.editors.data = publication.editors
    form.pub_title.data = publication.pub_title
    form.journal_book_conf.data = publication.journal_book_conf
    form.year.data = publication.year
    form.volume.data = publication.volume
    form.pages.data = publication.pages
    form.publisher.data = publication.publisher
    form.city.data = publication.city
    form.country.data = publication.country
    form.institution.data = publication.institution
    form.DOI_ISBN.data = publication.DOI_ISBN
    form.pub_name.data = publication.name
    form.corresponding_author.data = publication.corresponding_author
    form.email.data = publication.email
    form.purposes.data = publication.purposes_id
    form.embargo.data = publication.embargo
    form.missing_data.data = publication.missing_data
    form.additional_source_string.data = publication.additional_source_string
    
    return render_template('data_manage/publication_form.html', form=form, publication=publication)

# publication edit history
@data_manage.route('/publication/<int:id>/edit-history')
@login_required
def publication_edit_history(id):
    publication = Publication.query.filter_by(id=id).first_or_404()
    logged_changes = ChangeLogger.query.filter_by(object_type = "publication",object_id = id)
    return render_template('edit_history.html',publication = publication, logged_changes = logged_changes)

# editing population infomation
# NEEDS UPDATE
@data_manage.route('/population/<string:edit_or_new>/<int:id>', methods=['GET', 'POST'])
@login_required
def population_form(id):
    population = Population.query.get_or_404(id)
    species = Species.query.get_or_404(population.species_id)
    form = PopulationForm(population=population)
    
    if form.validate_on_submit():
        population.name = form.name.data
        population.ecoregion = form.ecoregion.data
        population.country = form.country.data
        population.continent = form.continent.data
        population.latitude = form.latitude.data
        population.longitude = form.longitude.data
        population.altitude = form.altitude.data
        flash('The population infomation has been updated.')
        return redirect(url_for('.species_page',id=species.id))
        
    form.name.data = population.name
    form.ecoregion.data = population.ecoregion
    form.country.data = population.country
    form.continent.data = population.continent
    form.latitude.data = population.latitude
    form.longitude.data = population.longitude
    form.altitude.data = population.altitude
    
    return render_template('data_manage/generic_form.html', form=form, population=population,species = species)

# population edit history
@data_manage.route('/population/<int:id>/edit-history')
@login_required
def population_edit_history(id):
    population = Population.query.get_or_404(id)
    return render_template('edit_history.html', population=population)

# edting study infomation
# NEEDS UPDATE, possible merge into population
@data_manage.route('/study/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def study_form(id):
    study = Study.query.get_or_404(id)
    publication = study.publication_id
    form = StudyForm(study=study)
    
    if form.validate_on_submit():
        study.study_duration = form.study_duration.data
        study.study_start = form.study_start.data
        study.study_end = form.study_end.data
        flash('The study infomation has been updated.')
        return redirect(url_for('.publication_page',id=species.id))
        
    form.study_duration.data = study.study_duration
    form.study_start.data = study.study_start
    form.study_end.data = study.study_end
    
    return render_template('data_manage/generic_form.html', form=form, study=study)

# study edit history
@data_manage.route('/study/<int:id>/edit-history')
@login_required
def study_edit_history(id):
    study = Study.query.get_or_404(id)
    return render_template('edit_history.html', study=study)

# editing matrix
# NEEDS UPDATE
@data_manage.route('/matrix/<string:edit_or_new>/<int:id>', methods=['GET', 'POST'])
@login_required
def matrix_form(id):
    matrix = Matrix.query.get_or_404(id)
    population = Population.query.get_or_404(matrix.population_id)
    species = Species.query.get_or_404(population.species_id)
    form = MatrixForm(matrix=matrix)
    
    if form.validate_on_submit():
        matrix.treatment = form.treatment.data
        matrix.matrix_split = form.matrix_split.data
        matrix.matrix_composition = form.matrix_composition.data
        matrix.survival_issue = form.survival_issue.data
        matrix.n_intervals = form.n_intervals.data
        matrix.periodicity = form.periodicity.data
        matrix.matrix_criteria_size = form.matrix_criteria_size.data
        matrix.matrix_criteria_ontogeny = form.matrix_criteria_ontogeny.data
        matrix.matrix_criteria_age = form.matrix_criteria_age.data
        matrix.matrix_start = form.matrix_start.data
        matrix.matrix_end = form.matrix_end.data
        matrix.matrix_start_season_id = form.matrix_start_season_id.data
        matrix.matrix_end_season_id = form.matrix_end_season_id.data
        matrix.matrix_fec = form.matrix_fec.data
        matrix.matrix_a_string = form.matrix_a_string.data
        matrix.matrix_u_string = form.matrix_u_string.data
        matrix.matrix_f_string = form.matrix_f_string.data
        matrix.matrix_c_string = form.matrix_c_string.data
        matrix.matrix_class_string = form.matrix_class_string.data
        matrix.n_plots = form.n_plots.data
        matrix.plot_size = form.plot_size.data
        matrix.n_individuals = form.n_individuals.data
        matrix.studied_sex = form.studied_sex.data
        matrix.captivity_id = form.captivity_id.data
        matrix.matrix_dimension = form.matrix_dimension.data
        matrix.observations = form.observations.data
        flash('The matrix infomation has been updated.')
        return redirect(url_for('.species_page',id=species.id))
        
    form.treatment.data = matrix.treatment.treatment_name
    form.matrix_split.data = matrix.matrix_split
    form.matrix_composition.data = matrix.matrix_composition
    form.survival_issue.data = matrix.survival_issue
    form.n_intervals.data = matrix.n_intervals
    form.periodicity.data = matrix.periodicity
    form.matrix_criteria_size.data = matrix.matrix_criteria_size
    form.matrix_criteria_ontogeny.data = matrix.matrix_criteria_ontogeny
    form.matrix_criteria_age.data = matrix.matrix_criteria_age
    form.matrix_start.data = matrix.matrix_start
    form.matrix_end.data = matrix.matrix_end 
    form.matrix_start_season_id.data = matrix.matrix_start_season_id
    form.matrix_end_season_id.data = matrix.matrix_end_season_id 
    form.matrix_fec.data = matrix.matrix_fec
    form.matrix_dimension.data = matrix.matrix_dimension
    form.matrix_a_string.data = matrix.matrix_a_string
    form.matrix_u_string.data = matrix.matrix_u_string
    form.matrix_f_string.data = matrix.matrix_f_string
    form.matrix_c_string.data = matrix.matrix_c_string
    form.matrix_class_string.data = matrix.matrix_class_string
    form.n_plots.data = matrix.n_plots
    form.plot_size.data = matrix.plot_size 
    form.n_individuals.data = matrix.n_individuals
    form.studied_sex.data = matrix.studied_sex
    form.captivity_id.data = matrix.captivity_id
    form.observations.data = matrix.observations
    
    return render_template('data_manage/matrix_form.html', form=form, matrix=matrix,population=population,species = species)

# matrix edit history
@data_manage.route('/matrix/<int:id>/edit-history')
@login_required
def matrix_edit_history(id):
    matrix = Matrix.query.get_or_404(id)
    return render_template('edit_history.html', matrix= matrix)

# delete things
@data_manage.route('/delete/<thing_to_delete>/<int:id_obj>', methods=['GET', 'POST'])
@login_required
def delete_object(thing_to_delete,id_obj):
    form = DeleteForm()
    
    if thing_to_delete == "population":
        population = Population.query.get_or_404(id_obj)
        
    if thing_to_delete == "species":
        species = Species.query.get_or_404(id_obj)
        populations = Population.query.filter_by(species_id=id_obj)
        taxonomy = Taxonomy(species_id=id_obj)
        traits = Traits(species_id=id_obj)
    
    if thing_to_delete == "publication":
        publication = Publication.query.get_or_404(id_obj)
        populations = Population.query.filter_by(publication_id=id_obj)
        
    if thing_to_delete == "matrix":
        matrix = Matrix.query.get_or_404(id_obj)
        
        
    if form.validate_on_submit() and thing_to_delete == "population":
        db.session.delete(population)
        db.session.commit()
        flash('The population has been deleted')
        return redirect(url_for('.publication_page',id=population.publication_id))
    
    if form.validate_on_submit() and thing_to_delete == "species":
        db.session.delete(species)
        for p in populations:
            db.session.delete(p)
        db.session.commit()
        flash('The species has been deleted')
        return redirect(url_for('.species_table'))
    
    if form.validate_on_submit() and thing_to_delete == "publication":
        db.session.delete(publication)
        for p in populations:
            db.session.delete(p)
        db.session.commit()
        flash('The publication has been deleted')
        return redirect(url_for('.publications_table'))
    
    if form.validate_on_submit() and thing_to_delete == "matrix":
        db.session.delete(matrix)
        db.session.commit()
        flash('The matrix has been deleted')
        return redirect(url_for('.publication_page',id=matrix.publication_id))
    
    return render_template('data_manage/delete_confirm.html', form=form)

# CSV EXPORT, work in progress
@data_manage.route('/export/csv')
def csv_export(): 
    import csv      
    # First, grab all matrices, as these will be each 'row'
    all_matrices = Matrix.query.all()

    # Use this function to merge
    def merge_dicts(*dict_args):
        result = {}
        for dictionary in dict_args:
            result.update(dictionary)
        return result

    for i, matrix in enumerate(all_matrices):
        # Grab all of the parent objects
        matrix = matrix
        fixed = matrix.fixed[0]
        population = matrix.population
        publication = population.publication
        study = population.study
        species = population.species
        traits = species.traits[0]
        taxonomy = species.taxonomies[0]
        version = matrix.version

        # Merge all of them to one single dict, as dicts
        entry = merge_dicts(vars(species), vars(taxonomy), vars(traits), vars(publication), vars(study), vars(population), vars(matrix),  vars(fixed), vars(version))

        #If this is the first matrix, construct the headers too
        if i == 0:
            headings = [key for key in entry.keys()]
            with open('export_test.csv', 'wb') as outcsv:
                writer = csv.DictWriter(outcsv, fieldnames=headings)
                writer.writeheader()
        
                writer.writerow(entry)

    return "Hello"













