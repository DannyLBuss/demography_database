from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response, jsonify, send_file
from flask.ext.login import login_required, current_user
from flask.ext.sqlalchemy import get_debug_queries
from . import data_manage
from .. import db
from forms import SpeciesForm, TaxonomyForm, TraitForm, PopulationForm, PublicationForm, MatrixForm, VersionForm, DeleteForm, FixedForm, ContactsForm
from ..models import Permission, Role, User, \
                    IUCNStatus, OrganismType, GrowthFormRaunkiaer, ReproductiveRepetition, \
                    DicotMonoc, AngioGymno, SpandExGrowthType, SourceType, Database, Purpose, MissingData, ContentEmail, Ecoregion, Continent, InvasiveStatusStudy, InvasiveStatusElsewhere, StageTypeClass, \
                    TransitionType, MatrixComposition, StartSeason, EndSeason, StudiedSex, Captivity, Species, Taxonomy, Trait, \
                    Publication, AuthorContact, AdditionalSource, Population, Stage, StageType, Treatment, \
                    MatrixStage, MatrixValue, Matrix, Interval, Fixed, Small, CensusTiming, Status, PurposeEndangered, PurposeWeed, Institute, ChangeLogger, Version, DigitizationProtocol
from ..decorators import admin_required, permission_required, crossdomain
import re

import random
def gen_hex_code():
    r = lambda: random.randint(0,255)
    return('#%02X%02X%02X' % (r(),r(),r()))

# compadrino zone
@data_manage.route('/compadrino-zone')
@login_required
def compadrino_zone():
    assigned_pubs = Publication.query.join(Version).filter_by(entered_by_id = current_user.id)
    return render_template('data_manage/compadrino_zone.html',assigned_pubs = assigned_pubs)

# publication edit history
@data_manage.route('/useredits')
@login_required
def useredits():
    
    logged_changes = ChangeLogger.query.filter_by(user_id = current_user.id)
    return render_template('edit_history.html',logged_changes = logged_changes)

# Data management forms

@data_manage.route('/version/edit/<int:id>/', methods=['GET', 'POST'])
@login_required
def version_form(id):
    
    protocol = DigitizationProtocol.query.all()
    protocol_dict = {}
    for ocol in protocol:
        protocol_dict[ocol.name_in_csv] = ocol.field_description
    if current_user.role_id not in [1,3,4,6]:
        abort(404)
        
    if current_user.role_id not in [1,3,4,6]:
        abort(404)
    
    version = Version.query.filter_by(id=id).first_or_404()
    form = VersionForm()
    if form.validate_on_submit():
        version.checked = form.checked.data
        version.statuses = form.status.data
        version.checked_count = form.checked_count.data
        version.user = form.entered_by.data
        db.session.commit()
        
        flash('Status has been updated, please close this window and refresh the previous page')
        
    form.checked.data = version.checked
    form.status.data = version.statuses
    form.checked_count.data = version.checked_count
    form.entered_by.data= version.user
    
    return render_template('data_manage/version_form.html', form=form, version=version,protocol_dict = protocol_dict)


# editing species information #updated 25/1/17
# edit_or_new is a string that is either "edit" or "new"
# id is an integer that is the id of the object being edited, if a new object is being created id = 0
@data_manage.route('/species/<string:edit_or_new>/<int:id>/', methods=['GET', 'POST'])
@login_required
def species_form(id,edit_or_new):
    
    protocol = DigitizationProtocol.query.all()
    protocol_dict = {}
    for ocol in protocol:
        protocol_dict[ocol.name_in_csv] = ocol.field_description
    if current_user.role_id not in [1,3,4,6]:
        abort(404)
    
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
            # COPY CODE BLOCK
            species.add_to_logger(current_user,'species_accepted',species_old.species_accepted,form.species_accepted.data,'edit')
            species.add_to_logger(current_user,'species_common',species_old.species_common,form.species_common.data,'edit')
            species.add_to_logger(current_user,'iucn_status',species_old.iucn_status,form.iucn_status.data,'edit')
            species.add_to_logger(current_user,'species_iucn_taxonid',species_old.species_iucn_taxonid,form.species_iucn_taxonid.data,'edit')
            species.add_to_logger(current_user,'gbif_taxon_key',species_old.gbif_taxon_key,form.gbif_taxon_key.data,'edit')
            species.add_to_logger(current_user,'image_path',species_old.image_path,form.image_path.data,'edit')
            species.add_to_logger(current_user,'image_path2',species_old.image_path2,form.image_path2.data,'edit')
            #END COPY CODE BLOCK
        
        species.species_accepted = form.species_accepted.data 
        species.species_common = form.species_common.data
        species.iucn_status = form.iucn_status.data
        species.species_iucn_taxonid = form.species_iucn_taxonid.data #
        #species.invasive_status = form.invasive_status.data
        species.gbif_taxon_key = form.gbif_taxon_key.data
        species.image_path = form.image_path.data
        species.image_path2 = form.image_path2.data                     
        
        if edit_or_new == "new":
            db.session.add(species)
            db.session.flush()
#            db.session.commit()
            
            # COPY CODE BLOCK
            species.add_to_logger(current_user,'species_accepted',species_old.species_accepted,form.species_accepted.data,'edit')
            species.add_to_logger(current_user,'species_common',species_old.species_common,form.species_common.data,'edit')
            species.add_to_logger(current_user,'iucn_status',species_old.iucn_status,form.iucn_status.data,'edit')
            species.add_to_logger(current_user,'species_iucn_taxonid',species_old.species_iucn_taxonid,form.species_iucn_taxonid.data,'edit')
            species.add_to_logger(current_user,'gbif_taxon_key',species_old.gbif_taxon_key,form.gbif_taxon_key.data,'edit')
            species.add_to_logger(current_user,'image_path',species_old.image_path,form.image_path.data,'edit')
            species.add_to_logger(current_user,'image_path2',species_old.image_path2,form.image_path2.data,'edit')
            #END COPY CODE BLOCK
            
            #make associated version object
            version = Version()
            version.checked = 0
            version.checked_count = 0
            version.statuses = Status.query.filter_by(id=4).first()
            version.species_id = species.id
            db.session.add(version)
            db.session.flush()
            db.session.commit()
        
        species_id = str(species.id)
        flash('The species infomation has been updated.')
        return redirect("../species="+species_id+"/publications=all")
    
    form.species_accepted.data = species.species_accepted
    form.species_common.data = species.species_common
    form.iucn_status.data = species.iucn_status
    form.species_iucn_taxonid.data = species.species_iucn_taxonid #
    #form.invasive_status.data = species.invasive_status
    form.gbif_taxon_key.data = species.gbif_taxon_key
    form.image_path.data = species.image_path
    form.image_path2.data = species.image_path2
    
    return render_template('data_manage/species_form.html', form=form, species=species,protocol_dict = protocol_dict)

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
    protocol = DigitizationProtocol.query.all()
    protocol_dict = {}
    for ocol in protocol:
        protocol_dict[ocol.name_in_csv] = ocol.field_description
        
    if current_user.role_id not in [1,3,4,6]:
        abort(404)
    
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
            taxonomy.add_to_logger(current_user,'col_check_date',taxonomy_old.col_check_date,form.col_check_date.data,'edit')
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
        taxonomy.col_check_date = form.col_check_date.data 
        
        if edit_or_new == "new":
            taxonomy.species_id = species.id
            
            db.session.add(taxonomy)
            db.session.flush()
#            db.session.commit()
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
            taxonomy.add_to_logger(current_user,'col_check_date',taxonomy_old.col_check_date,form.col_check_date.data,'edit')
            #END COPY CODE BLOCK
            
            #make associated version object
            version = Version()
            version.checked = 0
            version.checked_count = 0
            version.statuses = Status.query.filter_by(id=4).first()
            version.taxonomy_id = taxonomy.id
            db.session.add(version)
            db.session.flush()
            db.session.commit()
            
        species_id = str(species.id)
        flash('The taxonomy has been updated.')
        return redirect("../species="+species_id+"/publications=all") #url_for always gave me a build error
    
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
        form.col_check_date.data =  taxonomy.col_check_date

    #Actually rendering the page
    return render_template('data_manage/taxonomy_form.html', form=form, taxonomy = taxonomy, species=species,protocol_dict=protocol_dict)

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
    protocol = DigitizationProtocol.query.all()
    protocol_dict = {}
    for ocol in protocol:
        protocol_dict[ocol.name_in_csv] = ocol.field_description
    
    if current_user.role_id not in [1,3,4,6]:
        abort(404)
    
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
            
            trait.add_to_logger(current_user,'species_seedbank',trait_old.species_seedbank,form.species_seedbank.data,'edit')
            trait.add_to_logger(current_user,'species_clonality',trait_old.species_clonality,form.species_clonality.data,'edit')
            
            trait.add_to_logger(current_user,'species_seedbank_source',trait_old.species_seedbank_source,form.species_seedbank_source.data,'edit')
            trait.add_to_logger(current_user,'species_clonality_source',trait_old.species_clonality_source,form.species_clonality_source.data,'edit')
            trait.add_to_logger(current_user,'species_gisd_status',trait_old.species_gisd_status,form.species_gisd_status.data,'edit')
            # END CODE BLOCK
            
        trait.organism_type = form.organism_type.data
        trait.growth_form_raunkiaer = form.growth_form_raunkiaer.data
        trait.reproductive_repetition = form.reproductive_repetition.data
        trait.dicot_monoc = form.dicot_monoc.data
        trait.angio_gymno = form.angio_gymno.data
        trait.spand_ex_growth_types = form.spand_ex_growth_types.data
        trait.species_seedbank = form.species_seedbank.data
        trait.species_seedbank_source = form.species_seedbank_source.data
        trait.species_clonality = form.species_clonality.data
        trait.species_clonality_source = form.species_clonality_source.data
        trait.species_gisd_status = form.species_gisd_status.data
        
        if edit_or_new == "new":
            trait.species_id = species.id
            
            db.session.add(trait)
            db.session.flush()
#            db.session.commit()
            # COPY CODE BLOCK
            trait.add_to_logger(current_user,'organism_type',trait_old.organism_type,form.organism_type.data,'edit')
            trait.add_to_logger(current_user,'growth_form_raunkiaer',trait_old.growth_form_raunkiaer,form.growth_form_raunkiaer.data,'edit')
            trait.add_to_logger(current_user,'reproductive_repetition',trait_old.reproductive_repetition,form.reproductive_repetition.data,'edit')
            trait.add_to_logger(current_user,'dicot_monoc',trait_old.dicot_monoc,form.dicot_monoc.data,'edit')
            trait.add_to_logger(current_user,'angio_gymno',trait_old.angio_gymno,form.angio_gymno.data,'edit')
            trait.add_to_logger(current_user,'spand_ex_growth_types',trait_old.spand_ex_growth_types,form.spand_ex_growth_types.data,'edit')
            
            trait.add_to_logger(current_user,'species_seedbank',trait_old.species_seedbank,form.species_seedbank.data,'edit')
            trait.add_to_logger(current_user,'species_clonality',trait_old.species_clonality,form.species_clonality.data,'edit')
            
            trait.add_to_logger(current_user,'species_seedbank_source',trait_old.species_seedbank_source,form.species_seedbank_source.data,'edit')
            trait.add_to_logger(current_user,'species_clonality_source',trait_old.species_clonality_source,form.species_clonality_source.data,'edit')
            trait.add_to_logger(current_user,'species_gisd_status',trait_old.species_gisd_status,form.species_gisd_status.data,'edit')
            # END CODE BLOCK
            
            #make associated version object
            version = Version()
            version.checked = 0
            version.checked_count = 0
            version.statuses = Status.query.filter_by(id=4).first()
            version.trait_id = trait.id
            db.session.add(version)
            db.session.flush()
            db.session.commit()
        
        species_id = str(species.id)
        flash('The trait infomation has been updated.')
        return redirect("../species="+species_id+"/publications=all")
    
    
    
    form.organism_type.data = trait.organism_type
    form.growth_form_raunkiaer.data = trait.growth_form_raunkiaer
    form.reproductive_repetition.data = trait.reproductive_repetition
    form.dicot_monoc.data = trait.dicot_monoc
    form.angio_gymno.data = trait.angio_gymno
    form.spand_ex_growth_types.data = trait.spand_ex_growth_types
    form.species_seedbank.data = trait.species_seedbank
    form.species_clonality.data = trait.species_clonality
    form.species_gisd_status.data = trait.species_gisd_status
    form.species_seedbank_source.data = trait.species_seedbank_source
    form.species_clonality_source.data = trait.species_clonality_source
    
    return render_template('data_manage/trait_form.html', form=form, trait=trait,species = species,protocol_dict = protocol_dict)

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
def publication_form(id,edit_or_new):
    
    # GET PROTOCOL FOR THE FORM
    # THEN MUST BE MANUALLY FIELD BY FIELD TEMPLATED OUT IN THE FORM TEMPLATE
    protocol = DigitizationProtocol.query.all()
    protocol_dict = {}
    for ocol in protocol:
        protocol_dict[ocol.name_in_csv] = ocol.field_description 

    # DENY ACCESS IF NOT A ROLE WITH EDITING RIGHTS
    if current_user.role_id not in [1,3,4,6]:
        abort(404)
    
    # WHETHER EDIITNG AN EXISTING OBJECT OR CREATING A NEW ONE
    if edit_or_new == "edit":
        publication = Publication.query.filter_by(id=id).first_or_404()
        publication_old = Publication.query.filter_by(id=id).first_or_404()
        form = PublicationForm(publication=publication)
    else:
        publication = Publication()
        publication_old = Publication()
        form = PublicationForm()
    
    # WHEN YOU PRESS SUBMIT...
    if form.validate_on_submit():
        
        if edit_or_new == "edit":
            # CHANGE LOGGER, I AM SORRY THAT THIS IS NOT A GOOD IMPLEMENTATION
            # COPY CODE BLOCK
            publication.add_to_logger(current_user,'source_type',publication_old.source_type,form.source_type.data,'edit')
            publication.add_to_logger(current_user,'authors',publication_old.authors,form.authors.data,'edit')
            publication.add_to_logger(current_user,'editors',publication_old.editors,form.editors.data,'edit')
            publication.add_to_logger(current_user,'pub_title',publication_old.pub_title,form.pub_title.data,'edit')
            publication.add_to_logger(current_user,'year',publication_old.year,form.year.data,'edit')
            publication.add_to_logger(current_user,'volume',publication_old.volume,form.volume.data,'edit')
            publication.add_to_logger(current_user,'pages',publication_old.pages,form.pages.data,'edit')
            publication.add_to_logger(current_user,'publisher',publication_old.publisher,form.publisher.data,'edit')
            publication.add_to_logger(current_user,'city',publication_old.city,form.city.data,'edit')
            publication.add_to_logger(current_user,'country',publication_old.country,form.country.data,'edit')
            publication.add_to_logger(current_user,'institution',publication_old.institution,form.institution.data,'edit')
            publication.add_to_logger(current_user,'DOI_ISBN',publication_old.DOI_ISBN,form.DOI_ISBN.data,'edit')
            publication.add_to_logger(current_user,'journal_name',publication_old.journal_name,form.journal_name.data,'edit')
            #publication.add_to_logger(current_user,'purposes',publication_old.purposes,form.purposes.data,'edit')
            #publication.add_to_logger(current_user,'date_digitised',publication_old.date_digitised,form.date_digitised.data,'edit')
            publication.add_to_logger(current_user,'embargo',publication_old.embargo,form.embargo.data,'edit')
            publication.add_to_logger(current_user,'additional_source_string',publication_old.additional_source_string,form.additional_source_string.data,'edit')
            publication.add_to_logger(current_user,'study_notes',publication_old.study_notes,form.study_notes.data,'edit')
            # END CODE BLOCK
            
        publication.source_type = form.source_type.data
        publication.authors = form.authors.data 
        publication.editors = form.editors.data
        publication.pub_title = form.pub_title.data
        publication.year = form.year.data
        publication.volume = form.volume.data
        publication.pages = form.pages.data
        publication.publisher = form.publisher.data
        publication.city = form.city.data
        publication.country = form.country.data
        publication.institution = form.institution.data
        publication.DOI_ISBN = form.DOI_ISBN.data
        publication.journal_name = form.journal_name.data
        #publication.corresponding_author = form.corresponding_author.data
        #publication.email = form.email.data
        publication.purposes = form.purposes.data
        #publication.date_digitised = form.date_digitised.data
        publication.embargo = form.embargo.data
        publication.missing_data = form.missing_data.data
        publication.additional_source_string = form.additional_source_string.data
        publication.study_notes = form.study_notes.data
        db.session.flush()
        
        print(publication.purposes)
        
        if edit_or_new == "new":
            publication.colour = gen_hex_code()
            db.session.add(publication)
            db.session.flush()
#            db.session.commit()
            # COPY CODE BLOCK
            publication.add_to_logger(current_user,'source_type',publication_old.source_type,form.source_type.data,'edit')
            publication.add_to_logger(current_user,'authors',publication_old.authors,form.authors.data,'edit')
            publication.add_to_logger(current_user,'editors',publication_old.editors,form.editors.data,'edit')
            publication.add_to_logger(current_user,'pub_title',publication_old.pub_title,form.pub_title.data,'edit')
            publication.add_to_logger(current_user,'year',publication_old.year,form.year.data,'edit')
            publication.add_to_logger(current_user,'volume',publication_old.volume,form.volume.data,'edit')
            publication.add_to_logger(current_user,'pages',publication_old.pages,form.pages.data,'edit')
            publication.add_to_logger(current_user,'publisher',publication_old.publisher,form.publisher.data,'edit')
            publication.add_to_logger(current_user,'city',publication_old.city,form.city.data,'edit')
            publication.add_to_logger(current_user,'country',publication_old.country,form.country.data,'edit')
            publication.add_to_logger(current_user,'institution',publication_old.institution,form.institution.data,'edit')
            publication.add_to_logger(current_user,'DOI_ISBN',publication_old.DOI_ISBN,form.DOI_ISBN.data,'edit')
            publication.add_to_logger(current_user,'journal_name',publication_old.journal_name,form.journal_name.data,'edit')
            #publication.add_to_logger(current_user,'purposes',publication_old.purposes,form.purposes.data,'edit')
            #publication.add_to_logger(current_user,'date_digitised',publication_old.date_digitised,form.date_digitised.data,'edit')
            publication.add_to_logger(current_user,'embargo',publication_old.embargo,form.embargo.data,'edit')
            publication.add_to_logger(current_user,'additional_source_string',publication_old.additional_source_string,form.additional_source_string.data,'edit')
            publication.add_to_logger(current_user,'study_notes',publication_old.study_notes,form.study_notes.data,'edit')
            # END CODE BLOCK
            
            #make associated version object
            version = Version()
            version.checked = 0
            version.checked_count = 0
            version.statuses = Status.query.filter_by(id=4).first()
            version.publication_id = publication.id
            db.session.add(version)
            db.session.flush()
            db.session.commit()
            
        publication_id = str(publication.id)
            
        flash('The publication infomation has been updated.')
        return redirect("../species=all/publications="+publication_id)
    
    form.source_type.data = publication.source_type
    form.authors.data = publication.authors
    form.editors.data = publication.editors
    form.pub_title.data = publication.pub_title
    form.year.data = publication.year
    form.volume.data = publication.volume
    form.pages.data = publication.pages
    form.publisher.data = publication.publisher
    form.city.data = publication.city
    form.country.data = publication.country
    form.institution.data = publication.institution
    form.DOI_ISBN.data = publication.DOI_ISBN
    form.journal_name.data = publication.journal_name
    #form.corresponding_author.data = publication.corresponding_author
    #form.email.data = publication.email
    form.purposes.data = publication.purposes
    #form.date_digitised.data = publication.date_digitised
    form.embargo.data = publication.embargo
    form.missing_data.data = publication.missing_data
    form.additional_source_string.data = publication.additional_source_string
    form.study_notes.data = publication.study_notes
    
    
    return render_template('data_manage/publication_form.html', form=form, publication=publication,protocol_dict = protocol_dict)

# publication edit history
@data_manage.route('/publication/<int:id>/edit-history')
@login_required
def publication_edit_history(id):
    publication = Publication.query.filter_by(id=id).first_or_404()
    logged_changes = ChangeLogger.query.filter_by(object_type = "publication",object_id = id)
    return render_template('edit_history.html',publication = publication, logged_changes = logged_changes)

@data_manage.route('/population/new/publication=<int:id_pub>/choose_species', methods=['GET'])
@login_required
def choose_species(id_pub):
    if current_user.role_id not in [1,3,4,6]:
        abort(404)
        
    publication = Publication.query.get_or_404(id_pub)
    species = Species.query.all()
    
    return render_template('data_manage/choose_species.html',publication=publication,species=species)

# editing population infomation
# requires changlogger
@data_manage.route('/population/<string:edit_or_new>/<int:id>/species=<int:species_id>/publication=<int:publication_id>', methods=['GET', 'POST'])
@login_required
def population_form(id,edit_or_new,species_id,publication_id):
    if current_user.role_id not in [1,3,4,6]:
        abort(404)
        
    protocol = DigitizationProtocol.query.all()
    protocol_dict = {}
    for ocol in protocol:
        protocol_dict[ocol.name_in_csv] = ocol.field_description

    if edit_or_new == "edit":
        population = Population.query.get_or_404(id)
        population_old = Population.query.get_or_404(id)
        species = Species.query.get_or_404(species_id)
        publication = Publication.query.get_or_404(publication_id)
        form = PopulationForm(population=population)
    else:
        population = Population()
        population_old = Population()
        species = Species.query.get_or_404(species_id)
        publication = Publication.query.get_or_404(publication_id)
        form = PopulationForm()
    
    if form.validate_on_submit():
        
        # COPY CODE BLOCK
        population.add_to_logger(current_user,'species_author',population_old.species_author,form.species_author.data,'edit')
        population.add_to_logger(current_user,'population_name',population_old.population_name,form.population_name.data,'edit')
        population.add_to_logger(current_user,'ecoregion',population_old.ecoregion,form.ecoregion.data,'edit')
        population.add_to_logger(current_user,'invasive_status_study',population_old.invasive_status_study_id,form.invasive_status_study.data,'edit')
        population.add_to_logger(current_user,'invasive_status_elsewhere',population_old.invasive_status_elsewhere,form.invasive_status_elsewhere.data,'edit')
        population.add_to_logger(current_user,'country',population_old.country,form.country.data,'edit')
        population.add_to_logger(current_user,'population_nautical_miles',population_old.population_nautical_miles,form.population_nautical_miles.data,'edit')
        population.add_to_logger(current_user,'continent',population_old.continent,form.continent.data,'edit')
        population.add_to_logger(current_user,'lat_ns',population_old.lat_ns,form.lat_ns.data,'edit')
        population.add_to_logger(current_user,'lat_deg',population_old.lat_deg,form.lat_deg.data,'edit')
        population.add_to_logger(current_user,'lat_min',population_old.lat_min,form.lat_min.data,'edit')
        population.add_to_logger(current_user,'lat_sec',population_old.lat_sec,form.lat_sec.data,'edit')
        population.add_to_logger(current_user,'lon_ew',population_old.lon_ew,form.lon_ew.data,'edit')
        population.add_to_logger(current_user,'lon_deg',population_old.lon_deg,form.lon_deg.data,'edit')
        population.add_to_logger(current_user,'lon_min',population_old.lon_min,form.lon_min.data,'edit')
        population.add_to_logger(current_user,'lon_sec',population_old.lon_sec,form.lon_sec.data,'edit')
        population.add_to_logger(current_user,'altitude',population_old.altitude,form.altitude.data,'edit')
        population.add_to_logger(current_user,'within_site_replication',population_old.within_site_replication,form.within_site_replication.data,'edit')
        population.add_to_logger(current_user,'study_start',population_old.study_start,form.study_start.data,'edit')
        population.add_to_logger(current_user,'study_end',population_old.study_end,form.study_end.data,'edit')
        population.add_to_logger(current_user,'purpose_endangered',population_old.purpose_endangered,form.purpose_endangered.data,'edit')
        population.add_to_logger(current_user,'purpose_weed',population_old.purpose_weed,form.purpose_weed.data,'edit')
        population.add_to_logger(current_user,'database_source',population_old.database_source,form.database_source.data,'edit')
        population.add_to_logger(current_user,'database',population_old.database,form.database.data,'edit')
        # end block
        
        
        population.species_id = species_id
        population.publication_id = publication_id
        population.species_author = form.species_author.data
        population.population_name = form.population_name.data
        population.ecoregion = form.ecoregion.data
        population.invasive_status_study = form.invasive_status_study.data
        population.invasive_status_elsewhere = form.invasive_status_elsewhere.data
        population.country = form.country.data
        population.population_nautical_miles = form.population_nautical_miles.data
        population.continent = form.continent.data
        population.lat_ns = form.lat_ns.data
        population.lat_deg = form.lat_deg.data
        population.lat_min = form.lat_min.data
        population.lat_sec = form.lat_sec.data
        if population.lat_ns == "N":
            population.latitude = float(population.lat_deg) + float(population.lat_min)/60 + float(population.lat_sec)/3600
        if population.lat_ns == "S":
            population.latitude = -(float(population.lat_deg) + float(population.lat_min)/60 + float(population.lat_sec)/3600)
        population.lon_ew = form.lon_ew.data
        population.lon_deg = form.lon_deg.data
        population.lon_min = form.lon_min.data
        population.lon_sec = form.lon_sec.data
        if population.lon_ew == "E":
            population.longitude = float(population.lon_deg) + float(population.lon_min)/60 + float(population.lon_sec)/3600
        if population.lon_ew == "W":
            population.longitude = -(float(population.lon_deg) + float(population.lon_min)/60 + float(population.lon_sec)/3600)
        population.altitude = form.altitude.data
        #population.pop_size = form.pop_size.data
        population.within_site_replication = form.within_site_replication.data
        population.study_start = form.study_start.data
        population.study_end = form.study_end.data
        #population.study_duration = population.study_end - population.study_start
        population.purpose_endangered = form.purpose_endangered.data
        population.purpose_weed = form.purpose_weed.data
        population.database_source = form.database_source.data 
        population.database = form.database.data 
        flash('The population infomation has been updated.')
        
        if edit_or_new == "new":
            
            db.session.add(population)
            db.session.flush()
#            db.session.commit()
            
            # COPY CODE BLOCK
            population.add_to_logger(current_user,'species_author',population_old.species_author,form.species_author.data,'edit')
            population.add_to_logger(current_user,'population_name',population_old.population_name,form.population_name.data,'edit')
            population.add_to_logger(current_user,'ecoregion',population_old.ecoregion,form.ecoregion.data,'edit')
            population.add_to_logger(current_user,'invasive_status_study',population_old.invasive_status_study_id,form.invasive_status_study.data,'edit')
            population.add_to_logger(current_user,'invasive_status_elsewhere',population_old.invasive_status_elsewhere,form.invasive_status_elsewhere.data,'edit')
            population.add_to_logger(current_user,'country',population_old.country,form.country.data,'edit')
            population.add_to_logger(current_user,'population_nautical_miles',population_old.population_nautical_miles,form.population_nautical_miles.data,'edit')
            population.add_to_logger(current_user,'continent',population_old.continent,form.continent.data,'edit')
            population.add_to_logger(current_user,'lat_ns',population_old.lat_ns,form.lat_ns.data,'edit')
            population.add_to_logger(current_user,'lat_deg',population_old.lat_deg,form.lat_deg.data,'edit')
            population.add_to_logger(current_user,'lat_min',population_old.lat_min,form.lat_min.data,'edit')
            population.add_to_logger(current_user,'lat_sec',population_old.lat_sec,form.lat_sec.data,'edit')
            population.add_to_logger(current_user,'lon_ew',population_old.lon_ew,form.lon_ew.data,'edit')
            population.add_to_logger(current_user,'lon_deg',population_old.lon_deg,form.lon_deg.data,'edit')
            population.add_to_logger(current_user,'lon_min',population_old.lon_min,form.lon_min.data,'edit')
            population.add_to_logger(current_user,'lon_sec',population_old.lon_sec,form.lon_sec.data,'edit')
            population.add_to_logger(current_user,'altitude',population_old.altitude,form.altitude.data,'edit')
            population.add_to_logger(current_user,'within_site_replication',population_old.within_site_replication,form.within_site_replication.data,'edit')
            population.add_to_logger(current_user,'study_start',population_old.study_start,form.study_start.data,'edit')
            population.add_to_logger(current_user,'study_end',population_old.study_end,form.study_end.data,'edit')
            population.add_to_logger(current_user,'purpose_endangered',population_old.purpose_endangered,form.purpose_endangered.data,'edit')
            population.add_to_logger(current_user,'purpose_weed',population_old.purpose_weed,form.purpose_weed.data,'edit')
            population.add_to_logger(current_user,'database_source',population_old.database_source,form.database_source.data,'edit')
            population.add_to_logger(current_user,'database',population_old.database,form.database.data,'edit')
            # end block
            
            #make associated version object
            version = Version()
            version.checked = 0
            version.checked_count = 0
            version.statuses = Status.query.filter_by(id=4).first()
            version.population_id = population.id
            db.session.add(version)
            db.session.flush()
            db.session.commit()
        
        publication_id = str(publication.id)
        return redirect("../species=all/publications="+publication_id)
        
    form.species_author.data = population.species_author  
    form.population_name.data = population.population_name  
    form.ecoregion.data = population.ecoregion  
    form.invasive_status_study.data = population.invasive_status_studies
    form.invasive_status_elsewhere.data = population.invasive_status_elsewhere  
    form.country.data = population.country  
    form.population_nautical_miles.data = population.population_nautical_miles  
    form.continent.data = population.continent  
    form.lat_ns.data = population.lat_ns  
    form.lat_deg.data = population.lat_deg  
    form.lat_min.data = population.lat_min  
    form.lat_sec.data = population.lat_sec  
    form.lon_ew.data = population.lon_ew  
    form.lon_deg.data = population.lon_deg  
    form.lon_min.data = population.lon_min  
    form.lon_sec.data = population.lon_sec  
    form.altitude.data = population.altitude  
    #form.pop_size.data = population.pop_size 
    form.within_site_replication.data = population.within_site_replication
    form.study_start.data = population.study_start  
    form.study_end.data = population.study_end 
    form.purpose_endangered.data = population.purpose_endangered 
    form.purpose_weed.data = population.purpose_weed  
    form.database_source.data = population.database_source 
    form.database.data = population.database 
    
    species_author_populations = Population.query.filter_by(species_id=species.id).filter_by(publication_id=publication.id).all()

    return render_template('data_manage/population_form.html', form=form, population=population,species = species,publication = publication,species_author_populations = species_author_populations,protocol_dict = protocol_dict)

# population edit history
@data_manage.route('/population/<int:id>/edit-history')
@login_required
def population_edit_history(id):
    population = Population.query.get_or_404(id)
    logged_changes = ChangeLogger.query.filter_by(object_type = "population",object_id = id)
    return render_template('edit_history.html', population=population, logged_changes = logged_changes)

# editing matrix
# NEEDS UPDATE
@data_manage.route('/matrix/<string:edit_or_new>/<int:id>/population=<int:pop_id>', methods=['GET', 'POST'])
@login_required
def matrix_form(id,edit_or_new,pop_id):
    
    protocol = DigitizationProtocol.query.all()
    protocol_dict = {}
    for ocol in protocol:
        protocol_dict[ocol.name_in_csv] = ocol.field_description
        
    if current_user.role_id not in [1,3,4,6]:
        abort(404)
        
    if edit_or_new == "edit":
        matrix = Matrix.query.get_or_404(id)
        matrix_old = Matrix.query.get_or_404(id)
        population = Population.query.get_or_404(pop_id)
        species = Species.query.get_or_404(population.species_id)
        publication = Publication.query.get_or_404(population.publication_id)
        form = MatrixForm(matrix=matrix)
    else:
        matrix = Matrix()
        matrix_old = Matrix()
        population = Population.query.get_or_404(pop_id)
        species = Species.query.get_or_404(population.species_id)
        publication = Publication.query.get_or_404(population.publication_id)
        form = MatrixForm()
        
    publication_id = str(publication.id)
    
    if form.validate_on_submit():
        matrix.treatment = form.treatment.data
        matrix.matrix_split = form.matrix_split.data
        matrix.matrix_composition = form.matrix_composition.data
        matrix.n_intervals = form.n_intervals.data
        matrix.periodicity = form.periodicity.data
        matrix.matrix_criteria_size = form.matrix_criteria_size.data
        matrix.matrix_criteria_ontogeny = form.matrix_criteria_ontogeny.data
        matrix.matrix_criteria_age = form.matrix_criteria_age.data
        matrix.matrix_start_year = form.matrix_start_year.data
        matrix.matrix_start_month = form.matrix_start_month.data
        matrix.matrix_end_year = form.matrix_end_year.data
        matrix.matrix_end_month = form.matrix_end_month.data
        matrix.matrix_start_season_id = form.matrix_start_season.data
        matrix.matrix_end_season_id = form.matrix_end_season.data
        matrix.matrix_fec = form.matrix_fec.data
        matrix.matrix_a_string = form.matrix_a_string.data
        matrix.matrix_u_string = form.matrix_u_string.data
        matrix.matrix_f_string = form.matrix_f_string.data
        matrix.matrix_c_string = form.matrix_c_string.data
        matrix.class_author = form.class_author.data
        matrix.class_organized = form.class_organized.data
        matrix.class_number = form.class_number.data
        matrix.studied_sex = form.studied_sex.data
        matrix.captivities = form.captivity_id.data
        matrix.matrix_dimension = form.matrix_dimension.data
        matrix.observations = form.observations.data
        
        matrix.matrix_difficulty = form.matrix_difficulty.data
        matrix.matrix_complete = form.matrix_complete.data
        matrix.independence_origin = form.independence_origin.data
        matrix.independent = form.independent.data
        matrix.non_independence = form.non_independence.data
        matrix.non_independence_author = form.non_independence_author.data
        
        #matrix.survival_issue
        #matrix.irreducible
        #matrix.primitive
        #matrix.ergodic
        
        
        if edit_or_new == "new":
            matrix.population_id = population.id
            db.session.add(matrix)
            db.session.flush()
#            db.session.commit()
            
            
            #make associated version object
            version = Version()
            version.checked = 0
            version.checked_count = 0
            version.statuses = Status.query.filter_by(id=4).first()
            version.matrix_id = matrix.id
            db.session.add(version)
            db.session.flush()
#            db.session.commit()
            
            # make fixed object
            fixed = Fixed()
            fixed.matrix_id = matrix.id
            print fixed
            db.session.add(fixed)
            db.session.flush()
#            db.session.commit()
            
            # make a version for the fixed object...
            version = Version()
            version.checked = 0
            version.checked_count = 0
            version.statuses = Status.query.filter_by(id=4).first()
            version.fixed_id = fixed.id
            db.session.add(version)
            db.session.flush()
            db.session.commit()
        
        flash('The matrix infomation has been updated.')
        return redirect("../species=all/publications="+publication_id)
        
    form.treatment.data = matrix.treatment
    form.matrix_split.data = matrix.matrix_split
    form.matrix_composition.data = matrix.matrix_composition
    form.n_intervals.data = matrix.n_intervals
    form.periodicity.data = matrix.periodicity
    form.matrix_criteria_size.data = matrix.matrix_criteria_size
    form.matrix_criteria_ontogeny.data = matrix.matrix_criteria_ontogeny
    form.matrix_criteria_age.data = matrix.matrix_criteria_age
    form.matrix_start_year.data = matrix.matrix_start_year
    form.matrix_start_month.data = matrix.matrix_start_month
    form.matrix_end_year.data = matrix.matrix_end_year
    form.matrix_end_month.data = matrix.matrix_end_month
    form.matrix_start_season.data = matrix.matrix_start_season_id
    form.matrix_end_season.data = matrix.matrix_end_season_id
    form.matrix_fec.data = matrix.matrix_fec
    form.matrix_dimension.data = matrix.matrix_dimension
    form.matrix_a_string.data = matrix.matrix_a_string
    form.matrix_u_string.data = matrix.matrix_u_string
    form.matrix_f_string.data = matrix.matrix_f_string
    form.matrix_c_string.data = matrix.matrix_c_string
    form.class_author.data = matrix.class_author
    form.class_organized.data = matrix.class_organized
    form.class_number.data = matrix.class_number
    form.studied_sex.data = matrix.studied_sex
    form.captivity_id.data = matrix.captivities
    form.observations.data = matrix.observations
    
    form.matrix_difficulty.data = matrix.matrix_difficulty
    form.matrix_complete.data = matrix.matrix_complete
    form.independence_origin.data = matrix.independence_origin
    form.independent.data = matrix.independent
    form.non_independence.data = matrix.non_independence
    form.non_independence_author.data = matrix.non_independence_author
    
    return render_template('data_manage/matrix_form.html', form=form, matrix=matrix,population=population,species = species,protocol_dict = protocol_dict)

# matrix edit history
@data_manage.route('/matrix/<int:id>/edit-history')
@login_required
def matrix_edit_history(id):
    matrix = Matrix.query.get_or_404(id)
    return render_template('edit_history.html', matrix= matrix)

@data_manage.route('/fixed/<string:edit_or_new>/<int:id>/matrix=<int:matrix_id>', methods=['GET', 'POST'])
@login_required
def fixed_form(id,edit_or_new,matrix_id):
    if current_user.role_id not in [1,3,4,6]:
        abort(404)
        
    protocol = DigitizationProtocol.query.all()
    protocol_dict = {}
    for ocol in protocol:
        protocol_dict[ocol.name_in_csv] = ocol.field_description

    if edit_or_new == "edit":
        fixed = Fixed.query.get_or_404(id)
        fixed_old = Fixed.query.get_or_404(id)
        matrix = Matrix.query.get_or_404(matrix_id)
        form = FixedForm(fixed=fixed)
    else:
        fixed = Fixed()
        fixed_old = Fixed()
        matrix = Matrix.query.get_or_404(matrix_id)
        form = FixedForm(fixed=fixed)
       
    publication = Publication.query.get_or_404(matrix.population.publication.id)
    publication_id = str(publication.id)
    
    if form.validate_on_submit():
        fixed.vector_str = form.vector_str.data
        fixed.vector_present = form.vector_present.data
        fixed.total_pop_no = form.total_pop_no.data
        fixed.smalls = form.smalls.data
        fixed.census_timing_id = form.census_timing.data
        fixed.private = form.private.data
        fixed.vectors_includes_na = form.vectors_includes_na.data
        fixed.vectors_proportional = form.vectors_proportional.data
        fixed.vector_class_names = form.vector_class_names.data
        fixed.seed_stage_error = form.seed_stage_error.data
        
        
        if edit_or_new == "new":
            #make associated version object
            version = Version()
            version.checked = 0
            version.checked_count = 0
            version.statuses = Status.query.filter_by(id=4).first()
            version.fixed_id = fixed.id
            db.session.add(version)
            db.session.flush()
            db.session.commit()
        flash('The SPAND_EX data has been updated.')
        return redirect("../species=all/publications="+publication_id)

    form.vector_str.data = fixed.vector_str
    form.vector_present.data =  fixed.vector_present
    form.total_pop_no.data =  fixed.total_pop_no
    form.smalls.data =  fixed.smalls
    form.census_timing.data =  fixed.census_timing_id
    form.private.data =  fixed.private
    form.vectors_includes_na.data =  fixed.vectors_includes_na
    form.vectors_proportional.data =  fixed.vectors_proportional
    form.vector_class_names.data =  fixed.vector_class_names
    form.seed_stage_error.data =  fixed.seed_stage_error
        
    return render_template('data_manage/fixed_form.html', form=form, matrix=matrix,fixed = fixed,publicaton = publication,protocol_dict=protocol_dict)

@data_manage.route('/contact/<string:edit_or_new>/<int:id>/publication=<int:publication_id>', methods=['GET', 'POST'])
@login_required
def contacts_form(id,edit_or_new,publication_id):
    if current_user.role_id not in [1,3,4,6]:
        abort(404)
        
    protocol = DigitizationProtocol.query.all()
    protocol_dict = {}
    for ocol in protocol:
        protocol_dict[ocol.name_in_csv] = ocol.field_description
        
    if edit_or_new == "edit":
        contact = AuthorContact.query.get_or_404(id)
        contact_old = AuthorContact.query.get_or_404(id)
        publication = Publication.query.get_or_404(publication_id)
        form = ContactsForm(contact=contact)
    else:
        contact = AuthorContact()
        contact_old = AuthorContact()
        publication = Publication.query.get_or_404(publication_id)
        form = ContactsForm(contact=contact)
        
    publication_id = str(publication.id)
        
        
    if form.validate_on_submit():
        contact.corresponding_author = form.corresponding_author.data
        contact.corresponding_author_email = form.corresponding_author_email.data
        contact.date_contacted = form.date_contacted.data
        contact.date_contacted_again = form.date_contacted_again.data
        contact.extra_content_email = form.extra_content_email.data
        contact.correspondence_email_content = form.correspondence_email_content.data
        contact.author_reply = form.author_reply.data
        contact.user = form.contacting_user.data
        contact.publication_id = publication_id
        
        db.session.add(contact)
        db.session.flush()
        db.session.commit()
        flash('The contact has been updated.')
        return redirect("../species=all/publications="+publication_id)
        
    form.corresponding_author.data = contact.corresponding_author 
    form.corresponding_author_email.data= contact.corresponding_author_email
    form.date_contacted.data= contact.date_contacted
    form.date_contacted_again.data= contact.date_contacted_again
    form.extra_content_email.data= contact.extra_content_email
    form.correspondence_email_content.data= contact.correspondence_email_content
    form.author_reply.data= contact.author_reply
    form.contacting_user.data = contact.user
    
    
    return render_template('data_manage/generic_form.html', form=form, contact=contact,publicaton = publication,protocol_dict=protocol_dict)

## delete things
@data_manage.route('/delete/<thing_to_delete>/<int:id_obj>', methods=['GET', 'POST'])
@login_required
def delete_object(thing_to_delete,id_obj):
    form = DeleteForm()
    
    # only specific roles can delete
    if current_user.role_id not in [1,3,4,6]:
        abort(404)
    
    can_delete = False
    
    ## check if it can be deleted
    if thing_to_delete == "species":
        species = Species.query.get_or_404(id_obj)
        if len(species.populations) == 0:
            can_delete = True
    
    if thing_to_delete == "publication":
        publication = Publication.query.get_or_404(id_obj)
        if len(publication.populations) == 0:
            can_delete = True
            
    if thing_to_delete == "population":
        population = Population.query.get_or_404(id_obj)
        if len(population.matrices) == 0:
            can_delete = True
        
    if thing_to_delete == "matrix":
        matrix = Matrix.query.get_or_404(id_obj)
        can_delete = True
        
    if thing_to_delete == "contact":
        contact = AuthorContact.query.get_or_404(id_obj)
        can_delete = True
        
    
    # delete stuff
    if form.validate_on_submit() and thing_to_delete == "species" and can_delete == True:
        taxonomy = Taxonomy.query.filter_by(id = species.id)
        trait = Trait.query.filter_by(id = species.id)
        version = Version.query.filter_by(species_id = species.id)
        db.session.delete(species)
        for tax in taxonomy:
            db.session.delete(tax)
        for tra in trait:
            db.session.delete(tra)
        for ver in version:
            db.session.delete(ver)
        db.session.flush()
        db.session.commit()
        flash('The species (+taxonomy and traits) has been deleted')
        return redirect(url_for('.compadrino_zone'))

    if form.validate_on_submit() and thing_to_delete == "publication" and can_delete == True:
        version = Version.query.filter_by(publication_id = publication.id)
        for ver in version:
            db.session.delete(ver)
        db.session.delete(publication)
        db.session.flush()
        db.session.commit()
        flash('The publication has been deleted')
        return redirect(url_for('.compadrino_zone'))
    
    if form.validate_on_submit() and thing_to_delete == "population" and can_delete == True:
        version = Version.query.filter_by(population_id = population.id)
        publication_id = str(population.publication.id)
        for ver in version:
            db.session.delete(ver)
        db.session.delete(population)
        db.session.flush()
        db.session.commit()
        flash('The population has been deleted')
        return redirect("../species=all/publications="+publication_id)
    
    if form.validate_on_submit() and thing_to_delete == "contact" and can_delete == True:
        publication_id = str(contact.publication.id)
        db.session.delete(contact)
        db.session.flush()
        db.session.commit()
        flash('The contact has been deleted')
        return redirect("../species=all/publications="+publication_id)
    
    if form.validate_on_submit() and thing_to_delete == "matrix" and can_delete == True:
        version = Version.query.filter_by(matrix_id = matrix.id)
        publication_id = str(matrix.population.publication.id)
        for ver in version:
            db.session.delete(ver)
        fixed = Fixed.query.filter_by(id = matrix.id)
        for fix in fixed:
            for vers in fix.version:
                db.session.delete(vers)
            db.session.delete(fix)
        db.session.delete(matrix)
        db.session.flush()
        db.session.commit()
        flash('The matrix has been deleted')
        return redirect("../species=all/publications="+publication_id)
    
    return render_template('data_manage/delete_confirm.html', form=form,can_delete = can_delete,obj_type = thing_to_delete)
        

@data_manage.route('/meta-tables/')
@login_required
def meta_tables_json():

    # Constructing dict for meta tables, ordering by main Class
    meta_tables = {"User" : {"Institute" : []},
                   "Species" : {"IUCNStatus" : [], "ESAStatus" : []}, "Taxonomy" : {}, "Trait" : {"OrganismType" : [], \
                   "GrowthFormRaunkiaer" : [], "ReproductiveRepetition" : [], "DicotMonoc" : [], "AngioGymno" : [], "SpandExGrowthType" : [] }, \
                   "Publication" : {"SourceType" : [], "Database" : [], "Purpose" : [], "MissingData" : [] }, \
                   "AuthorContact" : { "ContentEmail" : [] }, "Population" : {"Ecoregion" : [], "Continent" : [] , "InvasiveStatusStudy" : [], "InvasiveStatusElsewhere" : [], "PurposeEndangered": [], "PurposeWeed" : []}, \
                   "StageType" : { "StageTypeClass" : [] }, "MatrixValue" : { "TransitionType" : [] }, \
                   "Matrix" : {"MatrixComposition" : [], "StartSeason" : [], "EndSeason" : [], "StudiedSex" : [], "Captivity" : []}, \
                   "Fixed" : { "Small": [], "CensusTiming" : [] }}

    meta_tables["User"]["Institute"].extend(Institute.query.all())
    meta_tables["Species"]["IUCNStatus"].extend(IUCNStatus.query.all())
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
    meta_tables["Population"]["PurposeEndangered"].extend(PurposeEndangered.query.all())
    meta_tables["Population"]["PurposeWeed"].extend(PurposeWeed.query.all())
    meta_tables["StageType"]["StageTypeClass"].extend(StageTypeClass.query.all())
    meta_tables["MatrixValue"]["TransitionType"].extend(TransitionType.query.all())
    meta_tables["Matrix"]["MatrixComposition"].extend(MatrixComposition.query.all())
    meta_tables["Matrix"]["StartSeason"].extend(StartSeason.query.all())
    meta_tables["Matrix"]["EndSeason"].extend(EndSeason.query.all())
    meta_tables["Matrix"]["StudiedSex"].extend(StudiedSex.query.all())
    meta_tables["Matrix"]["Captivity"].extend(Captivity.query.all())
    meta_tables["Fixed"]["Small"].extend(Small.query.all())
    meta_tables["Fixed"]["CensusTiming"].extend(CensusTiming.query.all())
    

    print meta_tables

    return render_template('meta.html', meta=meta_tables)

# CSV EXPORT, for general users
@data_manage.route('/export/database.csv')
def csv_export():   
    import csv 
    
    # First, grab all matrices, as these will be each 'row'
    all_matrices = Matrix.query.all()
    
    #function to merge dictionaries to a super dictionary
    def merge_dicts(*dict_args):
        result = {}
        for dictionary in dict_args:
            result.update(dictionary)
        return result
            
    w_file = open('app/static/downloads/database.csv','w')

    #looping through rows
    for i, matrix in enumerate(all_matrices):
        
        # Grab all of the parent objects
        matrix = matrix
        if matrix.fixed:
            fixed = matrix.fixed[0]
        population = matrix.population
        publication = population.publication
        species = population.species
        traits = species.trait[0]
        taxonomy = species.taxonomy[0]

        

        # Merge all of them to one single dict, as dict
        entry = merge_dicts(vars(species), vars(taxonomy), vars(traits), vars(publication), vars(population), vars(matrix),  vars(fixed))
        #convert fields to string fields to remove unicode and prevent datetime splitting up
        entry["date_digitised"] = str(entry["date_digitised"])
        entry["col_check_date"] = str(entry["col_check_date"])
        entry["class_author"] = str(entry["class_author"])
        entry["publisher"] = str(entry["publisher"])
        entry["volume"] = str(entry["volume"])
        entry["pub_title"] = str(entry["pub_title"])
        entry["authors"] = str(entry["authors"])
        entry["authors"] = str(entry["authors"].replace(";"," "))
        entry["authors"] = str(entry["authors"].replace(","," "))
        entry["id"] = str(entry["id"])
        entry["pages"] = str(entry["pages"])
        entry["col_check_date"] = str(entry["col_check_date"])
        entry["tax_order"] = str(entry["tax_order"])
        entry["family"] = str(entry["family"])
        entry["phylum"] = str(entry["phylum"])
        entry["species_accepted"] = str(entry["species_accepted"])
        entry["species_common"] = str(entry["species_common"])
        entry["tax_class"] = str(entry["tax_class"])
        entry["kingdom"] = str(entry["kingdom"])
        entry["genus"] = str(entry["genus"])
        entry["species_id"] = str(entry["species_id"])
        entry["matrix_criteria_size"] = str(entry["matrix_criteria_size"])
        entry["matrix_criteria_age"] = str(entry["matrix_criteria_age"])
        entry["matrix_criteria_ontogeny"] = str(entry["matrix_criteria_ontogeny"])
        entry["class_organized"] = str(entry["class_organized"])
        entry["class_author"] = str(entry["class_organized"])
        entry["class_number"] = str(entry["class_number"])
        entry["matrix_criteria_ontogeny"] = str(entry["matrix_criteria_ontogeny"])
        entry["matrix_start_season_id"] = str( entry["matrix_start_season_id"])
        season_find_and_replace = {'1':'Spring','2':'Summer','3':'Autumn','4':'Winter'}
        season_replace = season_find_and_replace.keys()
        for season in entry["matrix_start_season_id"]:
            if season in season_replace:
                s = season_replace.index(season)
                entry["matrix_start_season_id"] = season_find_and_replace[season_replace[s]]

        entry["study_start"] = str( entry["study_start"])
        entry["journal_name"] = str( entry["journal_name"])
        entry["dicot_monoc_id"] = str( entry["dicot_monoc_id"])
        dicot_find_and_replace = {'1':'Eudicot','2':'Monocot','3':'NA'}
        dicot_replace = dicot_find_and_replace.keys()
        for dicot in entry["dicot_monoc_id"]:
            if dicot in dicot_replace:
                d = dicot_replace.index(dicot)
                entry["dicot_monoc_id"] = dicot_find_and_replace[dicot_replace[d]]

        entry["matrix_dimension"] = str( entry["matrix_dimension"])
        entry["matrix_end_season_id"] = str( entry["matrix_end_season_id"])
        for seas in entry["matrix_end_season_id"]:
            if seas in season_replace:
                r = season_replace.index(seas)
                entry["matrix_end_season_id"] = season_find_and_replace[season_replace[r]]

        entry["angio_gymno_id"] = str( entry["angio_gymno_id"])
        ang_find_and_replace = {'1':'Angiosperm','2':'Gymnosperm','3':'NA'}
        ang_replace = ang_find_and_replace.keys()
        for ang in entry["angio_gymno_id"]:
            if ang in ang_replace:
                a = ang_replace.index(ang)
                entry["angio_gymno_id"] = ang_find_and_replace[ang_replace[a]]

        entry["continent_id"] = str( entry["continent_id"])
        cont_find_and_replace = {'1':'Africa','2':'Asia','3':'Europe','4':'N America','5':'S America','6':'Antartica','7':'Oceania'}
        cont_replace = cont_find_and_replace.keys()
        for cont in entry["continent_id"]:
            if cont in cont_replace:
                c = cont_replace.index(cont)
                entry["continent_id"] = cont_find_and_replace[cont_replace[c]]

        entry["matrix_composition_id"] = str( entry["matrix_composition_id"])
        comp_f_r = {'1':'Individual','2':'Mean','3':'Pooled','4':'Spatial Mean','5':'Temporal Mean','6':'Spatial-Temporal Mean'}
        repeats = comp_f_r.keys()
        for values in entry["matrix_composition_id"]:
            if values in repeats:
                ind = repeats.index(values)
                entry["matrix_composition_id"] = comp_f_r[repeats[ind]]

        entry["study_end"] = str( entry["study_end"])
        entry["species_author"] = str( entry["species_author"])
        entry["organism_type_id"] = str(entry["organism_type_id"])
        entry["pages"] = str(entry["pages"])
        entry["matrix_f_string"] = str(entry["matrix_f_string"])
        entry["matrix_a_string"] = str(entry["matrix_a_string"])
        entry["matrix_c_string"] = str(entry["matrix_c_string"])
        entry["matrix_u_string"] = str(entry["matrix_u_string"])
        entry["within_site_replication"] = str(entry["within_site_replication"])
        entry["studied_sex_id"] = str(entry["studied_sex_id"])
        sex_find_and_replace = {'1':'M','2':'F','3':'H','4':'M/F','5':'A'}
        sex_replace = sex_find_and_replace.keys()
        for sex in entry["studied_sex_id"]:
            if sex in sex_replace:
                sx = sex_replace.index(sex)
                entry["studied_sex_id"] = sex_find_and_replace[sex_replace[sx]]

        entry["matrix_start_month"] = str(entry["matrix_start_month"])
        month_find_and_replace = {'1':'January','2':'February','3':'March','4':'April','5':'May','6':'June','7':'July','8':'August','9':'September','10':'October','11':'November','12':'December'}
        month_replace = month_find_and_replace.keys()
        for month in entry["matrix_start_month"]:
            if month in month_replace:
                i = month_replace.index(month)
                entry["matrix_start_month"] = month_find_and_replace[month_replace[i]]

        entry["matrix_start_year"] = str(entry["matrix_start_year"])

        entry["matrix_end_month"] = str(entry["matrix_end_month"])
        for mon in entry["matrix_end_month"]:
            if mon in month_replace:
                j = month_replace.index(mon)
                entry["matrix_end_month"] = month_find_and_replace[month_replace[j]]

        entry["matrix_end_year"] = str(entry["matrix_end_year"])
        entry["captivity_id"] = str(entry["captivity_id"])
        cap_find_and_replace = {'1':'W','2':'C','3':'CW'}
        cap_replace = cap_find_and_replace.keys()
        for cap in entry["captivity_id"]:
            if cap in cap_replace:
                cp = cap_replace.index(cap)
                entry["captivity_id"] = cap_find_and_replace[cap_replace[cp]]

        entry["id"] = str(entry["id"])
        entry["matrix_id"] = str(entry["matrix_id"])
        entry["publication_id"] = str(entry["publication_id"])
        entry["number_populations"] = str(entry["number_populations"])
        entry["population_name"] = str(entry["population_name"])
        entry["study_duration"] = str(entry["study_duration"])
        entry["ecoregion_id"] = str(entry["ecoregion_id"])
        entry["DOI_ISBN"] = str(entry["DOI_ISBN"])
        entry["spand_ex_growth_type_id"] = str(entry["spand_ex_growth_type_id"])

        #find and replace organism type ID with word strings for user ease
        org_find_and_replace = {'1':'Tree','2':'Shrub','3':'Closed Perennial','4':'Open Perennial','5':'Monocarpic','6':'Algae','7':'NA'}
        replace = org_find_and_replace.keys()
        for val in entry["spand_ex_growth_type_id"]:
            if val in replace:
                index = replace.index(val)
                entry["spand_ex_growth_type_id"] = org_find_and_replace[replace[index]]

        entry["treatment_id"] = str(entry["treatment_id"])
        treatment_f_r = {'1':'Unmanipulated','2':'Herbicide','3':'Grazing','4':'Shading','5':'Competition','6':'Density/Seed Predation','7':'Flooded Area'}
        rep = treatment_f_r.keys()
        for vals in entry["treatment_id"]:
            if vals in rep:
                indexs = rep.index(vals)
                entry["treatment_id"] = treatment_f_r[rep[indexs]]
       #print entry["treatment_id"]

        del entry["non_independence"]
        del entry["publications_protocol_id"]
        del entry["taxonomy"]
        del entry["invasive_status_study_id"]
        del entry["invasive_status_elsewhere_id"]
        del entry["image_path"]
        del entry["_sa_instance_state"]
        del entry["species_iucn_taxonid"]
        del entry["species_epithet_accepted"]
        del entry["image_path2"]
        del entry["authority"]
        del entry["col_check_ok"]
        del entry["iucn_status_id"]
        del entry["col_check_date"]
        del entry["tpl_version"]
        del entry["infraspecies_accepted"]
        del entry["growth_form_raunkiaer_id"]
        del entry["species_clonality"]
        del entry["species_seedbank"]
        del entry["lat_deg"]
        del entry["species_seedbank_source"]
        del entry["species_clonality_source"]
        del entry["lon_deg"]
        del entry["lat_sec"]
        del entry["lat_min"]
        del entry["lat_ns"]
        del entry["lon_sec"]
        del entry["lon_min"]
        del entry["lon_ew"]
        del entry["purpose_endangered_id"]
        del entry["purpose_weed_id"]
        del entry["species_gisd_status"]
        del entry["trait"]
        del entry["publication"]
        del entry["institution"]
        del entry["latitude"]
        del entry["vector_class_names"]
        del entry["study_notes"]
        del entry["embargo"]
        del entry["country"]
        del entry["source_type_id"]
        del entry["colour"]
        del entry["additional_source_string"]
        del entry["journal_book_conf"]
        del entry["city"]
        del entry["altitude"]
        del entry["matrix_complete"]
        del entry["observations"]
        del entry["population"]
        del entry["total_pop_no"]
        del entry["matrix_irreducible"]
        del entry["matrix_ergodic"]
        del entry["matrix_difficulty"]
        del entry["longitude"]
        del entry["non_independence_author"]
        del entry["independence_origin"]
        del entry["fixed"]
        del entry["uid"]
        del entry["vector_present"]
        del entry["vectors_proportional"]
        del entry["vectors_includes_na"]
        del entry["vector_str"]
        del entry["n_intervals"]
        del entry["matrix_primitive"]
        del entry["population_id"]
        del entry["matrix_lambda"]
        del entry["census_timing_id"]
        del entry["database_source_id"]
        del entry["gbif_taxon_key"]
        del entry["species"]
        del entry["independent"]
        del entry["small_id"]
        del entry["private"]
        del entry["database_id"]
        del entry["seed_stage_error"]

        #Need to work out what to do with treatment ID - input as string also? 

        #If this is the first matrix, construct the headers too
        if i == 0:
            #get all the headings from entry - the super dict
            headings = [key for key in entry.keys()]
            headings = str(headings)
            w_file.write(headings[1:-1] + '\n')
            
        entry = str(entry.values())
        
        ## cleaning - still needs to be done:
        # remove quotes from strings
        #[<taxonomy 1l="">] to 1
        # study purposes
        
        w_file.write(entry[1:-1] + '\n')
                     
    flash ('Demography Database CSV created successfully')
    # #add page with button to return to publications table or download publications                 
    return render_template('data_manage/download_database_csv.html')

@data_manage.route('/export/species.csv')
def species_csv_export():  
    import csv 
    
    # First, grab all matrices, as these will be each 'row'
    all_species = Species.query.all()
    
    #function to merge dictionaries to a super dictionary
    def merge_dicts(*dict_args):
        result = {}
        for dictionary in dict_args:
            result.update(dictionary)
        return result
            
    w_file = open('app/static/downloads/species.csv','w')

    #looping through rows
    for i, species in enumerate(all_species):
        
        # Grab all of the parent objects
        species = species
        taxonomy = species.taxonomy[0]
        trait = species.trait[0]
        
        # Merge all of them to one single dict, as dict
        entry = merge_dicts(vars(species), vars(taxonomy), vars(trait))
        #convert unicode and datetime fields to string to remove random characters
        entry["col_check_date"] = str(entry["col_check_date"])
        entry["tax_order"] = str(entry["tax_order"])
        entry["family"] = str(entry["family"])
        entry["phylum"] = str(entry["phylum"])
        entry["species_accepted"] = str(entry["species_accepted"])
        entry["species_common"] = str(entry["species_common"])
        entry["tax_class"] = str(entry["tax_class"])
        entry["kingdom"] = str(entry["kingdom"])
        entry["genus"] = str(entry["genus"])
        entry["species_id"] = str(entry["species_id"])
        entry["spand_ex_growth_type_id"] = str(entry["spand_ex_growth_type_id"])

        #find and replace organism type ID with word strings for user ease
        org_find_and_replace = {'1':'Tree','2':'Shrub','3':'Closed Perennial','4':'Open Perennial','5':'Monocarpic','6':'Algae','7':'NA'}
        replace = org_find_and_replace.keys()
        for val in entry["spand_ex_growth_type_id"]:
            if val in replace:
                index = replace.index(val)
                entry["spand_ex_growth_type_id"] = org_find_and_replace[replace[index]]

        print entry["spand_ex_growth_type_id"]
        
        #delete fields normal users don't need to see
        del entry["gbif_taxon_key"]
        del entry["iucn_status_id"]
        del entry["image_path"]
        del entry["_sa_instance_state"]
        del entry["genus_accepted"]
        del entry["taxonomy"]
        del entry["species_iucn_taxonid"]
        del entry["species_epithet_accepted"]
        del entry["image_path2"]
        del entry["authority"]
        del entry["col_check_ok"]
        del entry["id"]
        del entry["col_check_date"]
        del entry["tpl_version"]
        del entry["infraspecies_accepted"]
        del entry["growth_form_raunkiaer_id"]
        del entry["species_clonality"]
        del entry["species_seedbank"]
        del entry["species_seedbank_source"]
        del entry["species_clonality_source"]
        del entry["reproductive_repetition_id"]
        del entry["organism_type_id"]
        del entry["species_gisd_status"]
        del entry["trait"]
        del entry["dicot_monoc_id"]
        del entry["angio_gymno_id"]


        #If this is the first matrix, construct the headers too
        if i == 0:
            #get all the headings from entry - the super dict
            headings = [key for key in entry.keys()]
            headings = str(headings)
            w_file.write(headings[1:-1] + '\n')
            
        entry = str(entry.values())
        
        w_file.write(entry[1:-1] + "\n")

    flash ('species list created successfully')
    # #add page with button to return to publications table or download publications                 
    return render_template('data_manage/download_species.html')

@data_manage.route('/export/publications.csv')
def publication_csv_export():  
    import csv 

# First, grab all matrices, as these will be each 'row'
    all_publications = Publication.query.all()

    #function to merge dictionaries to a super dictionary
    def merge_dicts(*dict_args):
        result = {}
        for dictionary in dict_args:
            result.update(dictionary)
        return result
            
    w_file = open('app/static/downloads/publications.csv','w')

    #looping through rows
    for i, publication in enumerate(all_publications):
        
        # Grab all of the parent objects
        publication = publication
        
        # Merge all of them to one single dict, as dict
        entry = merge_dicts(vars(publication))

        #turn fields into text strings
        entry["date_digitised"] = str(entry["date_digitised"])
        entry["publisher"] = str(entry["publisher"])
        entry["volume"] = str(entry["volume"])
        entry["pub_title"] = str(entry["pub_title"])
        entry["authors"] = str(entry["authors"])
        entry["id"] = str(entry["id"])
        entry["pages"] = str(entry["pages"])
        entry["DOI_ISBN"] = str(entry["DOI_ISBN"])

        #remove ; between authors so that csv doesn't split them up
        entry["authors"] = str(entry["authors"].replace(";"," "))
        entry["authors"] = str(entry["authors"].replace(","," "))

        #renove fields normal users don't need
        del entry["_sa_instance_state"]
        del entry["institution"]
        del entry["publications_protocol_id"]
        del entry["study_notes"]
        del entry["embargo"]
        del entry["country"]
        del entry["source_type_id"]
        del entry["colour"]
        del entry["additional_source_string"]
        del entry["journal_book_conf"]
        del entry["city"]

        #If this is the first matrix, construct the headers too
        if i == 0:
            #get all the headings from entry - the super dict
            headings = [key for key in entry.keys()]
            headings = str(headings)
            w_file.write(headings[1:-1] + '\n')
            
        entry = str(entry.values())
        # cleaning needed to be added here
        
        w_file.write(entry[1:-1] + '\n')
        
    flash ('publication list created successfully')
    # #add page with button to return to publications table or download publications                 
    return render_template('data_manage/download_pubs.html')

#button for publications download
#Need to change the directory to the server pwd when I upload to server!!
@data_manage.route('/download-pubs/', methods=['GET', 'POST'])
def download_pubs():
#server
    file_name = '/var/www/html/demography-database/app/static/downloads/publications.csv'
#local
#    file_name = '/Users/daniellebuss/Sites/demography_database/app/static/downloads/publications.csv'
    return send_file(file_name, as_attachment=True, mimetype='text/plain')

#button for species download
#Need to change the directory to the server pwd when I upload to server!!
@data_manage.route('/download-species/', methods=['GET', 'POST'])
def download_species():
#server
    file_name = '/var/www/html/demography-database/app/static/downloads/species.csv'
#local
#    file_name = '/Users/daniellebuss/Sites/demography_database/app/static/downloads/species.csv'
    return send_file(file_name, as_attachment=True, mimetype='text/plain')

#button for all csv download
#Need to change the directory to the server pwd when I upload to server!!
@data_manage.route('/download-database/', methods=['GET', 'POST'])
def download_database():
#server
    file_name = '/var/www/html/demography-database/app/static/downloads/database.csv'
#local
    # file_name = '/Users/daniellebuss/Sites/demography_database/app/static/downloads/database.csv'
    return send_file(file_name, as_attachment=True, mimetype='text/plain')

@data_manage.route('/591514wdjfgw43qrt34r4w5r274rrollback')
def rollback():  
    db.session.rollback()
    return ("Rollback successful")

@data_manage.route('/591514wdjfgw43qrt34r4w5r274rrollbackerror')
def rollbackerror():  
    Session.rollback()
    return ("Rollback successful")






