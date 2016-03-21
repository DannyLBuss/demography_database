from flask import render_template, jsonify, request, current_app, url_for
from . import api
from ..models import User, Species, Population, Taxonomy, PlantTrait, Publication, Study, AuthorContact, AdditionalSource, Stage, StageType, Treatment, TreatmentType, MatrixStage, MatrixValue, Matrix, Interval, Fixed
from ..decorators import admin_required, permission_required, crossdomain

@api.route('/')
def home():
    return render_template('api_1_0/index.html')

@api.route('/users/<int:id>')
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())


def fix_string(string):
    capitalised = string.capitalize()
    hypen_stripped = capitalised.replace("-", " ");
    return hypen_stripped

# Traversing via Species
# All Species
@api.route('/query/species/all')
@crossdomain(origin='*')
def get_all_species():
    all_species = Species.query.all()
    species = {'species' : []}
    for s in all_species:
        sp = s.to_json()
        species['species'].append(sp)

    print species
    return jsonify(species)

# Species by ID (not useful for client, useful for testing for now)
@api.route('/query/species/id=<int:id>')
@crossdomain(origin='*')
def get_species(id):
    species = Species.query.get_or_404(id)
    return jsonify(species.to_json())

# Go with name for protocol
@api.route('/query/species/name=<name>')
@crossdomain(origin='*')
def get_species_name(name):
    name = fix_string(name)
    species = Species.query.filter_by(species_accepted=name).first()
    return jsonify(species.to_json())

# Taxonomy of species
@api.route('/query/species/name=<name>/taxonomy')
@crossdomain(origin='*')
def get_species_taxonomy(name):
    name = fix_string(name)
    species = Species.query.filter_by(species_accepted=name).first()
    taxonomy = species.taxonomies[0]
    return jsonify(taxonomy.to_json())

@api.route('/query/species/name=<name>/plant-traits')
@crossdomain(origin='*')
def get_species_traits(name):
    name = fix_string(name)
    species = Species.query.filter_by(species_accepted=name).first()
    traits = species.plant_traits[0]
    return jsonify(traits.to_json())

# Show all populations of Species
@api.route('/query/species/name=<name>/populations')
@crossdomain(origin='*')
def get_species_populations(name):
    name = fix_string(name)
    species = Species.query.filter_by(species_accepted=name).first()
    all_populations = species.populations
    
    populations = {"populations" : []}
    for population in all_populations:
        pop = population.to_json()
        populations['populations'].append(pop)

    return jsonify(populations)

# Show all publications featuring this species
@api.route('/query/species/name=<name>/publication')
@crossdomain(origin='*')
def get_species_publication(name):
    name = fix_string(name)
    species = Species.query.filter_by(species_accepted=name).first()
    publication = species.taxonomies[0].publication
    return jsonify(publication.to_json())

# Show all matrices of this species
@api.route('/query/species/name=<name>/matrices')
@crossdomain(origin='*')
def get_species_matrices(name):
    name = fix_string(name)
    species = Species.query.filter_by(species_accepted=name).first()
    all_populations = species.populations
    
    matrices = {"matrices" : []}

    for population in all_populations:
        matrices_pop = population.study.matrices
        for matrix in matrices_pop:
            mat = matrix.to_json()
            matrices['matrices'].append(mat)

    return jsonify(matrices)


@api.route('/query/taxonomy/<int:id>')
@crossdomain(origin='*')
def get_taxonomy(id):
    taxonomy = Taxonomy.query.get_or_404(id)
    return jsonify(taxonomy.to_json())

@api.route('/query/planttrait/<int:id>')
@crossdomain(origin='*')
def get_planttrait(id):
    planttrait = PlantTrait.query.get_or_404(id)
    return jsonify(planttrait.to_json())

@api.route('/query/publication/<int:id>')
@crossdomain(origin='*')
def get_publication(id):
    publication = Publication.query.get_or_404(id)
    return jsonify(publication.to_json())

@api.route('/query/study/<int:id>')
@crossdomain(origin='*')
def get_study(id):
    study = Study.query.get_or_404(id)
    return jsonify(study.to_json())

# Not implemented yet
@api.route('/query/authorcontact/<int:id>')
@crossdomain(origin='*')
def get_authorcontact(id):
    authorcontact = AuthorContact.query.get_or_404(id)
    return jsonify(authorcontact.to_json())

# Not implemented yet
@api.route('/query/additionalsource/<int:id>')
@crossdomain(origin='*')
def get_additionalsource(id):
    additionalsource = AdditionalSource.query.get_or_404(id)
    return jsonify(additionalsource.to_json())

# Not implemented yet
@api.route('/query/stage/<int:id>')
@crossdomain(origin='*')
def get_stage(id):
    stage = Stage.query.get_or_404(id)
    return jsonify(stage.to_json())

# Not implemented yet
@api.route('/query/stagetype/<int:id>')
@crossdomain(origin='*')
def get_stagetype(id):
    stagetype = StageType.query.get_or_404(id)
    return jsonify(stagetype.to_json())

# Not implemented yet
@api.route('/query/treatment/<int:id>')
@crossdomain(origin='*')
def get_treatment(id):
    treatment = Treatment.query.get_or_404(id)
    return jsonify(treatment.to_json())

@api.route('/query/treatmenttype/<int:id>')
@crossdomain(origin='*')
def get_treatmenttype(id):
    treatmenttype = TreatmentType.query.get_or_404(id)
    return jsonify(treatmenttype.to_json())

# Not implemented yet
@api.route('/query/matrixstage/<int:id>')
@crossdomain(origin='*')
def get_matrixstage(id):
    matrixstage = MatrixStage.query.get_or_404(id)
    return jsonify(matrixstage.to_json())

# Not implemented yet
@api.route('/query/matrixvalue/<int:id>')
@crossdomain(origin='*')
def get_matrixvalue(id):
    matrixvalue = MatrixValue.query.get_or_404(id)
    return jsonify(matrixvalue.to_json())

@api.route('/query/matrix/<int:id>')
@crossdomain(origin='*')
def get_matrix(id):
    matrix = Matrix.query.get_or_404(id)
    return jsonify(matrix.to_json())

# Not implemented yet
@api.route('/query/interval/<int:id>')
@crossdomain(origin='*')
def get_interval(id):
    interval = Interval.query.get_or_404(id)
    return jsonify(interval.to_json())

# Not implemented yet
@api.route('/query/fixed/<int:id>')
@crossdomain(origin='*')
def get_fixed(id):
    fixed = Fixed.query.get_or_404(id)
    return jsonify(fixed.to_json())

@api.route('/query/population/<int:id>')
@crossdomain(origin='*')
def get_population(id):
    population = Population.query.get_or_404(id)
    return jsonify(population.to_json())