from flask import jsonify, request, current_app, url_for
from . import api
from ..models import User, Species, Population, Taxonomy, PlantTrait, Publication, Study, AuthorContact, AdditionalSource, Stage, StageType, Treatment, TreatmentType, MatrixStage, MatrixValue, Matrix, Interval, Bussy
from ..decorators import admin_required, permission_required, crossdomain


@api.route('/users/<int:id>')
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())

@api.route('/query/species')
@crossdomain(origin='*')
def get_all_species():
    all_species = Species.query.all()
    species = {'species' : []}
    for s in all_species:
        sp = s.to_json()
        species['species'].append(sp)

    print species
    return jsonify(species)

@api.route('/query/species/<int:id>')
def get_species(id):
    species = Species.query.get_or_404(id)
    return jsonify(species.to_json())

@api.route('/query/species-name/<name>')
def get_species_name(name):
    species = Species.query.filter_by(species_accepted=name).first()
    return jsonify(species.to_json())

@api.route('/query/taxonomy/<int:id>')
def get_taxonomy(id):
    taxonomy = Taxonomy.query.get_or_404(id)
    return jsonify(taxonomy.to_json())

@api.route('/query/planttrait/<int:id>')
def get_planttrait(id):
    planttrait = PlantTrait.query.get_or_404(id)
    return jsonify(planttrait.to_json())

@api.route('/query/publication/<int:id>')
def get_publication(id):
    publication = Publication.query.get_or_404(id)
    return jsonify(publication.to_json())

@api.route('/query/study/<int:id>')
def get_study(id):
    study = Study.query.get_or_404(id)
    return jsonify(study.to_json())

# Not implemented yet
@api.route('/query/authorcontact/<int:id>')
def get_authorcontact(id):
    authorcontact = AuthorContact.query.get_or_404(id)
    return jsonify(authorcontact.to_json())

# Not implemented yet
@api.route('/query/additionalsource/<int:id>')
def get_additionalsource(id):
    additionalsource = AdditionalSource.query.get_or_404(id)
    return jsonify(additionalsource.to_json())

# Not implemented yet
@api.route('/query/stage/<int:id>')
def get_stage(id):
    stage = Stage.query.get_or_404(id)
    return jsonify(stage.to_json())

# Not implemented yet
@api.route('/query/stagetype/<int:id>')
def get_stagetype(id):
    stagetype = StageType.query.get_or_404(id)
    return jsonify(stagetype.to_json())

# Not implemented yet
@api.route('/query/treatment/<int:id>')
def get_treatment(id):
    treatment = Treatment.query.get_or_404(id)
    return jsonify(treatment.to_json())

@api.route('/query/treatmenttype/<int:id>')
def get_treatmenttype(id):
    treatmenttype = TreatmentType.query.get_or_404(id)
    return jsonify(treatmenttype.to_json())

# Not implemented yet
@api.route('/query/matrixstage/<int:id>')
def get_matrixstage(id):
    matrixstage = MatrixStage.query.get_or_404(id)
    return jsonify(matrixstage.to_json())

# Not implemented yet
@api.route('/query/matrixvalue/<int:id>')
def get_matrixvalue(id):
    matrixvalue = MatrixValue.query.get_or_404(id)
    return jsonify(matrixvalue.to_json())

@api.route('/query/matrix/<int:id>')
def get_matrix(id):
    matrix = Matrix.query.get_or_404(id)
    return jsonify(matrix.to_json())

# Not implemented yet
@api.route('/query/interval/<int:id>')
def get_interval(id):
    interval = Interval.query.get_or_404(id)
    return jsonify(interval.to_json())

# Not implemented yet
@api.route('/query/bussy/<int:id>')
def get_bussy(id):
    bussy = Bussy.query.get_or_404(id)
    return jsonify(bussy.to_json())

@api.route('/query/population/<int:id>')
def get_population(id):
    population = Population.query.get_or_404(id)
    return jsonify(population.to_json())