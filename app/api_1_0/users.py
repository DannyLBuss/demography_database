from flask import render_template, jsonify, request, current_app, url_for, abort
from . import api
from flask.ext.login import login_user, logout_user, login_required, \
    current_user
from ..models import User, Species, Population, Taxonomy, Trait, Publication, Study, AuthorContact, AdditionalSource, Stage, StageType, Treatment, MatrixStage, MatrixValue, Matrix, Interval, Fixed, Institute, IUCNStatus, ESAStatus
from ..decorators import admin_required, permission_required, crossdomain
from .errors import unauthorized


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