from flask import render_template, jsonify, request, current_app, url_for, abort
from . import api
from .. import db
from flask.ext.login import login_user, logout_user, login_required, \
    current_user
from ..models import User, Species, Population, Taxonomy, Trait, Publication, Study, AuthorContact, AdditionalSource, Stage, StageType, Treatment, MatrixStage, MatrixValue, Matrix, Interval, Fixed, Institute, IUCNStatus, ESAStatus, OrganismType, ReproductiveRepetition, GrowthFormRaunkiaer, DicotMonoc, AngioGymno, SpandExGrowthType, SourceType, Database, MissingData, Purpose, ContentEmail, PurposeEndangered, PurposeWeed, Ecoregion, Continent, InvasiveStatusStudy
from ..decorators import admin_required, permission_required, crossdomain
from .errors import unauthorized, bad_request
import sqlalchemy.ext.declarative as declarative


def key_valid(key):
    users = User.query.all()
    hash = ''
    for user in users:
        if user.api_hash == key:
            hash = key
            request.api_key = key
        else:
            pass

    if hash == key:
        return True
    else:
        return False

@api.route('/')
def home():
    print request.cookies
    return render_template('api_1_0/index.html')

# API Routing for Meta Tables
# Institutes
@api.route('/<key>/query/institutes/<int:id>')
def get_institute(key, id):
    institute = Institute.query.get_or_404(id)
    if key_valid(key):
        return jsonify(institute.to_json(key))
    else:
        return unauthorized('Invalid credentials')

@api.route('/<key>/query/institutes/all')
def get_institutes(key):
    institutes = Institute.query.all()
    if key_valid(key):
        return jsonify({'institutes' : [institute.to_json(key) for institute in institutes]})
    else:
        return unauthorized('Invalid credentials')  

#IUCN Status
@api.route('/<key>/query/iucn-status/<int:id>')
def get_iucn_status(key, id):
    iucn_status = IUCNStatus.query.get_or_404(id)
    if key_valid(key):
        return jsonify(iucn_status.to_json(key))
    else:
        return unauthorized('Invalid credentials')

@api.route('/<key>/query/iucn-status/all')
def get_iucn_statuses(key):
    iucn_statuses = IUCNStatus.query.all()
    if key_valid(key):
        return jsonify({'iucn_statuses' : [iucn_status.to_json(key) for iucn_status in iucn_statuses]})
    else:
        return unauthorized('Invalid credentials')

#ESA Status
@api.route('/<key>/query/esa-status/<int:id>')
def get_esa_status(key, id):
    esa_status = ESAStatus.query.get_or_404(id)
    if key_valid(key):
        return jsonify(esa_status.to_json(key))
    else:
        return unauthorized('Invalid credentials')

@api.route('/<key>/query/esa-status/all')
def get_esa_statuses(key):
    esa_statuses = ESAStatus.query.all()
    if key_valid(key):
        return jsonify({'esa_statuses' : [esa_status.to_json(key) for esa_status in esa_statuses]})
    else:
        return unauthorized('Invalid credentials')

#Organism Type
@api.route('/<key>/query/organism-type/<int:id>')
def get_organism_type(key, id):
    organism_type = OrganismType.query.get_or_404(id)
    if key_valid(key):
        return jsonify(organism_type.to_json(key))
    else:
        return unauthorized('Invalid credentials')

@api.route('/<key>/query/organism-type/all')
def get_organism_types(key):
    organism_types = OrganismType.query.all()
    if key_valid(key):
        return jsonify({'organism_types' : [organism_type.to_json(key) for organism_type in organism_types]})
    else:
        return unauthorized
        ('Invalid credentials') 

#Growth Form Raunkiaer
@api.route('/<key>/query/growth-form/<int:id>')
def get_growth_form(key, id):
    growth_form = GrowthFormRaunkiaer.query.get_or_404(id)
    if key_valid(key):
        return jsonify(growth_form.to_json(key))
    else:
        return unauthorized('Invalid credentials')

@api.route('/<key>/query/growth-form/all')
def get_growth_forms(key):
    growth_forms = GrowthFormRaunkiaer.query.all()
    if key_valid(key):
        return jsonify({'growth_forms' : [growth_form.to_json(key) for growth_form in growth_forms]})
    else:
        return unauthorized('Invalid credentials') 

# ReproductiveRepetition
@api.route('/<key>/query/reproductive-repetition/<int:id>')
def get_reproductive_repetition(key, id):
    reproductive_repetition = ReproductiveRepetition.query.get_or_404(id)
    if key_valid(key):
        return jsonify(reproductive_repetition.to_json(key))
    else:
        return unauthorized('Invalid credentials')

@api.route('/<key>/query/reproductive-repetition/all')
def get_reproductive_repetitions(key):
    reproductive_repetitions = ReproductiveRepetition.query.all()
    if key_valid(key):
        return jsonify({'reproductive_repetitions' : [reproductive_repetition.to_json(key) for reproductive_repetition in reproductive_repetitions]})
    else:
        return unauthorized('Invalid credentials') 

#DicotMonoc
@api.route('/<key>/query/dicot-monoc/<int:id>')
def get_dicot_monoc(key, id):
    dicot_monoc = DicotMonoc.query.get_or_404(id)
    if key_valid(key):
        return jsonify(dicot_monoc.to_json(key))
    else:
        return unauthorized('Invalid credentials')

@api.route('/<key>/query/dicot-monoc/all')
def get_dicot_monocs(key):
    dicot_monocs = DicotMonoc.query.all()
    if key_valid(key):
        return jsonify({'dicot_monocs' : [dicot_monoc.to_json(key) for dicot_monoc in dicot_monocs]})
    else:
        return unauthorized('Invalid credentials') 


#AngioGymno
@api.route('/<key>/query/angio-gymno/<int:id>')
def get_angio_gymno(key, id):
    angio_gymno = AngioGymno.query.get_or_404(id)
    if key_valid(key):
        return jsonify(angio_gymno.to_json(key))
    else:
        return unauthorized('Invalid credentials')

@api.route('/<key>/query/angio-gymno/all')
def get_angio_gymnos(key):
    angio_gymnos = AngioGymno.query.all()
    if key_valid(key):
        return jsonify({'angio_gymnos' : [angio_gymno.to_json(key) for angio_gymno in angio_gymnos]})
    else:
        return unauthorized('Invalid credentials') 


#SpandExGrowthType
@api.route('/<key>/query/spandex-growth-type/<int:id>')
def get_spandex_growth_type(key, id):
    spandex_growth_type = SpandExGrowthType.query.get_or_404(id)
    if key_valid(key):
        return jsonify(spandex_growth_type.to_json(key))
    else:
        return unauthorized('Invalid credentials')

@api.route('/<key>/query/spandex-growth-type/all')
def get_spandex_growth_types(key):
    spandex_growth_types = SpandExGrowthType.query.all()
    if key_valid(key):
        return jsonify({'spandex_growth_types' : [spandex_growth_type.to_json(key) for spandex_growth_type in spandex_growth_types]})
    else:
        return unauthorized('Invalid credentials') 

''' Publications '''
#SourceType
@api.route('/<key>/query/source-type/<int:id>')
def get_source_type(key, id):
    source_type = SourceType.query.get_or_404(id)
    if key_valid(key):
        return jsonify(source_type.to_json(key))
    else:
        return unauthorized('Invalid credentials')

@api.route('/<key>/query/source-type/all')
def get_source_types(key):
    source_types = SourceType.query.all()
    if key_valid(key):
        return jsonify({'source_types' : [source_type.to_json(key) for source_type in source_types]})
    else:
        return unauthorized('Invalid credentials') 

#Database
@api.route('/<key>/query/database/<int:id>')
def get_database(key, id):
    database = Database.query.get_or_404(id)
    if key_valid(key):
        return jsonify(database.to_json(key))
    else:
        return unauthorized('Invalid credentials')

@api.route('/<key>/query/database/all')
def get_databases(key):
    databases = Database.query.all()
    if key_valid(key):
        return jsonify({'database' : [database.to_json(key) for database in databases]})
    else:
        return unauthorized('Invalid credentials') 

#Purpose
@api.route('/<key>/query/purpose/<int:id>')
def get_purpose(key, id):
    purpose = Purpose.query.get_or_404(id)
    if key_valid(key):
        return jsonify(purpose.to_json(key))
    else:
        return unauthorized('Invalid credentials')

@api.route('/<key>/query/purpose/all')
def get_purposes(key):
    purposes = Purpose.query.all()
    if key_valid(key):
        return jsonify({'purpose' : [purpose.to_json(key) for purpose in purposes]})
    else:
        return unauthorized('Invalid credentials') 


#Missing Data
@api.route('/<key>/query/missing-data/<int:id>')
def get_missing_data(key, id):
    missing_data = MissingData.query.get_or_404(id)
    if key_valid(key):
        return jsonify(missing_data.to_json(key))
    else:
        return unauthorized('Invalid credentials')

@api.route('/<key>/query/missing-data/all')
def get_missing_datas(key):
    missing_datas = MissingData.query.all()
    if key_valid(key):
        return jsonify({'missing_data' : [missing_data.to_json(key) for missing_data in missing_datas]})
    else:
        return unauthorized('Invalid credentials') 


#Content Email
@api.route('/<key>/query/content-email/<int:id>')
def get_content_email(key, id):
    content_email = ContentEmail.query.get_or_404(id)
    if key_valid(key):
        return jsonify(content_email.to_json(key))
    else:
        return unauthorized('Invalid credentials')

@api.route('/<key>/query/content-email/all')
def get_content_emails(key):
    content_emails = ContentEmail.query.all()
    if key_valid(key):
        return jsonify({'content_email' : [content_email.to_json(key) for content_email in content_emails]})
    else:
        return unauthorized('Invalid credentials') 


#Purpose Endangered
@api.route('/<key>/query/purpose-endangered/<int:id>')
def get_purpose_endangered(key, id):
    purpose_endangered = PurposeEndangered.query.get_or_404(id)
    if key_valid(key):
        return jsonify(purpose_endangered.to_json(key))
    else:
        return unauthorized('Invalid credentials')

@api.route('/<key>/query/purpose-endangered/all')
def get_purpose_endangereds(key):
    purpose_endangereds = PurposeEndangered.query.all()
    if key_valid(key):
        return jsonify({'purpose_endangered' : [purpose_endangered.to_json(key) for purpose_endangered in purpose_endangereds]})
    else:
        return unauthorized('Invalid credentials') 

#Purpose Weed
@api.route('/<key>/query/purpose-weed/<int:id>')
def get_purpose_weed(key, id):
    purpose_weed = PurposeWeed.query.get_or_404(id)
    if key_valid(key):
        return jsonify(purpose_weed.to_json(key))
    else:
        return unauthorized('Invalid credentials')

@api.route('/<key>/query/purpose-weed/all')
def get_purpose_weeds(key):
    purpose_weeds = PurposeWeed.query.all()
    if key_valid(key):
        return jsonify({'purpose_weed' : [purpose_weed.to_json(key) for purpose_weed in purpose_weeds]})
    else:
        return unauthorized('Invalid credentials') 


''' Population '''
#Ecoregion
@api.route('/<key>/query/ecoregion/<int:id>')
def get_ecoregion(key, id):
    ecoregion = Ecoregion.query.get_or_404(id)
    if key_valid(key):
        return jsonify(ecoregion.to_json(key))
    else:
        return unauthorized('Invalid credentials')

@api.route('/<key>/query/ecoregion/all')
def get_ecoregions(key):
    ecoregions = Ecoregion.query.all()
    if key_valid(key):
        return jsonify({'ecoregion' : [ecoregion.to_json(key) for ecoregion in ecoregions]})
    else:
        return unauthorized('Invalid credentials') 


#Continent
# @api.route('/<key>/query/continent/<int:id>')
# def get_continent(key, id):
#     continent = Continent.query.get_or_404(id)
#     if key_valid(key):
#         return jsonify(continent.to_json(key))
#     else:
#         return unauthorized('Invalid credentials')

# @api.route('/<key>/query/continent/all')
# def get_continents(key):
#     continents = Continent.query.all()
#     if key_valid(key):
#         return jsonify({'continent' : [continent.to_json(key) for continent in continents]})
#     else:
#         return unauthorized('Invalid credentials') 



''' GLORY '''
@api.route('/<key>/query/<model>/<int:id>')
def get_one_entry(key, id, model):
    class_ = False
    
    classes, models, table_names = [], [], []
    for clazz in db.Model._decl_class_registry.values():
        try:
            table_names.append(clazz.__tablename__)
            classes.append(clazz)
        except:
            pass
    for table in db.metadata.tables.items():
        if table[0] in table_names:
            models.append(classes[table_names.index(table[0])])

    for m in models:
        print model
        print m.__tablename__
        if model == m.__tablename__:
            class_ = m

    if class_:
        entry = class_.query.get_or_404(1)
        if key_valid(key):
            return jsonify(entry.to_json(key))
        else:
            return unauthorized('Invalid credentials')
    else:
        return bad_request('Bad Request')

@api.route('/<key>/query/<model>/all')
def get_all_entries(key, model):
    class_ = False
    
    classes, models, table_names = [], [], []
    for clazz in db.Model._decl_class_registry.values():
        try:
            table_names.append(clazz.__tablename__)
            classes.append(clazz)
        except:
            pass
    for table in db.metadata.tables.items():
        if table[0] in table_names:
            models.append(classes[table_names.index(table[0])])

    for m in models:
        print model
        print m.__tablename__
        if model == m.__tablename__:
            class_ = m

    if class_:
        entries = class_.query.all()
        if key_valid(key):
            return jsonify({model : [entry.to_json(key) for entry in entries]})
        else:
            return unauthorized('Invalid credentials')
    else:
        return bad_request('Bad Request')


''' Users '''

@api.route('/<key>/query/users/<int:id>')
def get_user(key, id):
    user = User.query.get_or_404(id)
    if key_valid(key):
        return jsonify(user.to_json(key))
    else:
        return unauthorized('Invalid credentials')

def fix_string(string):
    capitalised = string.capitalize()
    hypen_stripped = capitalised.replace("-", " ");
    return hypen_stripped

# Traversing via Species
# All Species
# Not working, hmm
@api.route('/<key>/query/species/all')
@crossdomain(origin='*')
def get_all_species(key):
    all_species = Species.query.all()
    species = {'species' : []}
    for s in all_species:
        sp = s.to_json(key)
        species['species'].append(sp)

    if key_valid(key):
        return jsonify(species)
    else:
        return unauthorized('Invalid credentials')

# Species by ID (not useful for client, useful for testing for now)
@api.route('/<key>/query/species/id=<int:id>')
@crossdomain(origin='*')
def get_species(key, id):
    species = Species.query.get_or_404(id)
    if key_valid(key):
        return jsonify(species.to_json(key))
    else:
        return unauthorized('Invalid credentials')

# Go with name for protocol
@api.route('/<key>/query/species/name=<name>')
@crossdomain(origin='*')
def get_species_name(key, name):
    name = fix_string(name)
    species = Species.query.filter_by(species_accepted=name).first()
    if key_valid(key):
        return jsonify(species.to_json(key))
    else:
        return unauthorized('Invalid credentials')

# Taxonomy of species
@api.route('/<key>/query/species/name=<name>/taxonomy')
@crossdomain(origin='*')
def get_species_taxonomy(key, name):
    name = fix_string(name)
    species = Species.query.filter_by(species_accepted=name).first()
    taxonomy = species.taxonomies[0]
    if key_valid(key):
        return jsonify(taxonomy.to_json(key))
    else:
        return unauthorized('Invalid credentials')

@api.route('/<key>/query/species/name=<name>/traits')
@crossdomain(origin='*')
def get_species_traits(key, name):
    name = fix_string(name)
    species = Species.query.filter_by(species_accepted=name).first()
    traits = species.traitss[0]
    if key_valid(key):
        return jsonify(traits.to_json(key))
    else:
        return unauthorized('Invalid credentials')

# Show all populations of Species
@api.route('/<key>/query/species/name=<name>/populations')
@crossdomain(origin='*')
def get_species_populations(key, name):
    name = fix_string(name)
    species = Species.query.filter_by(species_accepted=name).first()
    all_populations = species.populations
    
    populations = {"populations" : []}
    for population in all_populations:
        pop = population.to_json(key)
        populations['populations'].append(pop)
    if key_valid(key):
        return jsonify(populations)
    else:
        return unauthorized('Invalid credentials')

# Show all publications featuring this species
@api.route('/<key>/query/species/name=<name>/publication')
@crossdomain(origin='*')
def get_species_publication(key, name):
    name = fix_string(name)
    species = Species.query.filter_by(species_accepted=name).first()
    publication = species.taxonomies[0].publication
    if key_valid(key):
        return jsonify(publication.to_json(key))
    else:
        return unauthorized('Invalid credentials')

# Show all matrices of this species
@api.route('/<key>/query/species/name=<name>/matrices')
@crossdomain(origin='*')
def get_species_matrices(key, name):
    name = fix_string(name)
    species = Species.query.filter_by(species_accepted=name).first()
    all_populations = species.populations
    
    matrices = {"matrices" : []}

    for population in all_populations:
        matrices_pop = population.study.matrices
        for matrix in matrices_pop:
            mat = matrix.to_json(key)
            matrices['matrices'].append(mat)
    if key_valid(key):
        return jsonify(matrices)
    else:
        return unauthorized('Invalid credentials')


@api.route('/<key>/query/taxonomy/<int:id>')
@crossdomain(origin='*')
def get_taxonomy(key, id):
    taxonomy = Taxonomy.query.get_or_404(id)    
    if key_valid(key):
        return jsonify(taxonomy.to_json(key))
    else:
        return unauthorized('Invalid credentials')


@api.route('/<key>/query/trait/<int:id>')
@crossdomain(origin='*')
def get_trait(key, id):
    trait = Trait.query.get_or_404(id)    
    if key_valid(key):
        return jsonify(trait.to_json(key))
    else:
        return unauthorized('Invalid credentials')

@api.route('/<key>/query/publication/<int:id>')
@crossdomain(origin='*')
def get_publication(key, id):
    publication = Publication.query.get_or_404(id)
    if key_valid(key):
        return jsonify(publication.to_json(key))
    else:
        return unauthorized('Invalid credentials')

@api.route('/<key>/query/study/<int:id>')
@crossdomain(origin='*')
def get_study(key, id):
    study = Study.query.get_or_404(id)
    if key_valid(key):
        return jsonify(study.to_json(key))
    else:
        return unauthorized('Invalid credentials')

# Not implemented yet
@api.route('/<key>/query/authorcontact/<int:id>')
@crossdomain(origin='*')
def get_authorcontact(key, id):
    authorcontact = AuthorContact.query.get_or_404(id)
    if key_valid(key):
        return jsonify(authorcontact.to_json(key))
    else:
        return unauthorized('Invalid credentials')

# Not implemented yet
@api.route('/<key>/query/additionalsource/<int:id>')
@crossdomain(origin='*')
def get_additionalsource(key, id):
    additionalsource = AdditionalSource.query.get_or_404(id)
    if key_valid(key):
        return jsonify(additionalsource.to_json(key))
    else:
        return unauthorized('Invalid credentials')

# Not implemented yet
@api.route('/<key>/query/stage/<int:id>')
@crossdomain(origin='*')
def get_stage(key, id):
    stage = Stage.query.get_or_404(id)
    if key_valid(key):
        return jsonify(stage.to_json(key))
    else:
        return unauthorized('Invalid credentials')

# Not implemented yet
@api.route('/<key>/query/stagetype/<int:id>')
@crossdomain(origin='*')
def get_stagetype(key, id):
    stagetype = StageType.query.get_or_404(id)
    if key_valid(key):
        return jsonify(stagetype.to_json(key))
    else:
        return unauthorized('Invalid credentials')

# Not implemented yet
@api.route('/<key>/query/treatment/<int:id>')
@crossdomain(origin='*')
def get_treatment(key, id):
    treatment = Treatment.query.get_or_404(id)    
    if key_valid(key):
        return jsonify(treatment.to_json(key))
    else:
        return unauthorized('Invalid credentials')

@api.route('/<key>/query/treatmenttype/<int:id>')
@crossdomain(origin='*')
def get_treatmenttype(key, id):
    treatmenttype = TreatmentType.query.get_or_404(id)    
    if key_valid(key):
        return jsonify(treatmenttype.to_json(key))
    else:
        return unauthorized('Invalid credentials')

# Not implemented yet
@api.route('/<key>/query/matrixstage/<int:id>')
@crossdomain(origin='*')
def get_matrixstage(key, id):
    matrixstage = MatrixStage.query.get_or_404(id)
    if key_valid(key):
        return jsonify(matrixstage.to_json(key))
    else:
        return unauthorized('Invalid credentials')

# Not implemented yet
@api.route('/<key>/query/matrixvalue/<int:id>')
@crossdomain(origin='*')
def get_matrixvalue(key, id):
    matrixvalue = MatrixValue.query.get_or_404(id)    
    if key_valid(key):
        return jsonify(matrixvalue.to_json(key))
    else:
        return unauthorized('Invalid credentials')

@api.route('/<key>/query/matrix/<int:id>')
@crossdomain(origin='*')
def get_matrix(key, id):
    matrix = Matrix.query.get_or_404(id)
    if key_valid(key):
        return jsonify(matrix.to_json(key))
    else:
        return unauthorized('Invalid credentials')

# Not implemented yet
@api.route('/<key>/query/interval/<int:id>')
@crossdomain(origin='*')
def get_interval(key, id):
    interval = Interval.query.get_or_404(id)
    if key_valid(key):
        return jsonify(interval.to_json(key))
    else:
        return unauthorized('Invalid credentials')


# Not implemented yet
@api.route('/<key>/query/fixed/<int:id>')
@crossdomain(origin='*')
def get_fixed(key, id):
    fixed = Fixed.query.get_or_404(id)
    if key_valid(key):
        return jsonify(fixed.to_json(key))
    else:
        return unauthorized('Invalid credentials')

@api.route('/<key>/query/population/<int:id>')
@crossdomain(origin='*')
def get_population(key, id):
    population = Population.query.get_or_404(id)
    if key_valid(key):
        return jsonify(population.to_json(key))
    else:
        return unauthorized('Invalid credentials')