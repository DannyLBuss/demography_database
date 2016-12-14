from flask import render_template, jsonify, request, current_app, url_for, abort
from . import api
from .. import db
from flask.ext.login import login_user, logout_user, login_required, \
    current_user
from ..models import User, Species, Population, Taxonomy, Trait, Publication, Study, AuthorContact, AdditionalSource, Stage, StageType, Treatment, MatrixStage, MatrixValue, Matrix, Interval, Fixed, Institute, IUCNStatus, ESAStatus, OrganismType, ReproductiveRepetition, GrowthFormRaunkiaer, DicotMonoc, AngioGymno, SpandExGrowthType, SourceType, Database, MissingData, Purpose, ContentEmail, PurposeEndangered, PurposeWeed, Ecoregion, Continent, InvasiveStatusStudy, InvasiveStatusElsewhere, StageTypeClass, TransitionType, MatrixComposition, StartSeason, EndSeason, StudiedSex, Captivity, Status, Version, CensusTiming
from ..decorators import admin_required, permission_required, crossdomain
from .errors import unauthorized, bad_request
import sqlalchemy
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

@api.route('/docs')
def docs():
    parent = ['species', 'publications', 'populations', 'studies', 'taxonomies', 'traits', 'additional_sources', 'users', 'matrices', 'stages','versions', 'statuses', 'databases', 'stages', 'matrix_stages', 'matrix_values', 'author_contacts', 'smalls', 'fixed', 'treatments']
    exclude = ['fixed', 'smalls', 'roles', 'matrix_stages', 'stages', 'matrix_values', 'users']
    classes, models, table_names = [], [], []
    for clazz in db.Model._decl_class_registry.values():
        try:
            # print(list(clazz.__table__.columns.keys()))
            table_names.append(clazz.__tablename__)
            classes.append(clazz)
        except:
            pass
    for table in db.metadata.tables.items():
        if table[0] in table_names:
            models.append(classes[table_names.index(table[0])])

    tables_columns = {}
    for model in models:
        if model.__tablename__ not in exclude and model.__tablename__ in parent:
            tables_columns[model.__tablename__] = {k:'' for k, v in model.__table__.columns.items()}
            for key in model.__table__.columns.keys():           
                if len(model.__table__.columns[key].foreign_keys) > 0:
                    table_relation = list(model.__table__.columns[key].foreign_keys)[0]._column_tokens
                    table_name = table_relation[1]
                    table_fk = table_relation[2]
                    # print table_name, table_fk
                    if table_name not in parent:
                        print table_name
                        for m in models:
                            if table_name == m.__tablename__:
                                identifying_variable = m.__table__.columns.items()[1][0]
                                model_queryset = [str(m) for m in m.query.all()]
                                tables_columns[model.__tablename__][table_name] = model_queryset if model_queryset > 0 else None
                                tables_columns[model.__tablename__].pop(key, None)
    
    print tables_columns                        
    schema = tables_columns
    return render_template('api_1_0/schema.html', tables=schema)

''' GLORY '''
@api.route('/<key>/query/<model>/<int:id>')
@crossdomain(origin='*')
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
        if model == m.__tablename__:
            class_ = m

    if class_:
        entry = class_.query.get_or_404(id)
        if key_valid(key): 
            try:          
                return jsonify(entry.to_json(key))
            except TypeError:
                return entry.to_json(key)

        else:
            unauthorized('Invalid credentials')
    else:
        return bad_request('Bad Request')

@api.route('/<key>/query/<model>/all')
@crossdomain(origin='*')
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
        if model == m.__tablename__:
            class_ = m

    if class_:
        entries = class_.query.all()
        if key_valid(key):
            try:
                return jsonify({model : [entry.to_json(key) for entry in entries]})
            except TypeError:
                return unauthorized('Invalid Permissions')
        else:
            return unauthorized('Invalid credentials')
    else:
        return bad_request('Bad Request')


''' Filtering '''
def Find(self, **kwargs):
    f = self.db_session.filter(kwargs).all()

@api.route('/<key>/query/<model>/<filters>/all')
@crossdomain(origin='*')
def get_filtered_entries(key, model, filters):
    class_ = False

    kwargs = {}

    terms = filters.split('&')

    for term in terms:
        params = term.split('=')
        kwargs[params[0]] = params[1]
    
    classes, models, table_names = [], [], []
    for clazz in db.Model._decl_class_registry.values():
        try:
            # print(list(clazz.__table__.columns.keys()))
            table_names.append(clazz.__tablename__)
            classes.append(clazz)
        except:
            pass
    for table in db.metadata.tables.items():
        if table[0] in table_names:
            models.append(classes[table_names.index(table[0])])

    for m in models:
        if model == m.__tablename__:
            class_ = m
            # print list(class_.__table__.columns.keys())

    if class_:
        '''Filtering by Meta Table'''
        # Keeping keys from original that align with existing table columns within the parent model
        new_kwargs = {key: value for key, value in kwargs.items() if key in list(class_.__table__.columns.keys())}
        # Storing those that don't match up exactly - these will generally be the foreign keys, although it'll catch typos too
        second = {key: value for key, value in kwargs.items() if key not in list(class_.__table__.columns.keys())}      
        # Manually adding _id as per the syntax of the database schema, as models can't be passed through the URL, but strings can
        relationships = {key+'_id' : value for key, value in second.items() if key+'_id' in list(class_.__table__.columns.keys())}
        #Empty dict for foreign key tables
        fk_tables = {}

        # Getting the actual table names of the meta table options, keeping the value in the dict
        for k, v in relationships.items():
            table_name = list(list(class_.__table__.columns[k].foreign_keys)[0]._column_tokens)[1]
            fk_tables[table_name] = v

        #Iterating through models and fk_tables to match fk_keys table name to actual model object
        for m in models:
            for k, v in fk_tables.items():
                if k == m.__tablename__:  
                    # Grabbing a list of all of the column names                          
                    column_names_list = list(m.__table__.columns.values())
                    column_names = [col.key for col in column_names_list]
                    for name in column_names:
                        # Creating a key word argument to pass through to the query filter, of the column name and the original fk_key value.
                        # Trying each column with the value, to cover names, IDS, code names, etc....
                        kwargs = {name:v}
                        # If a model query matches the parameters
                        if m.query.filter_by(**kwargs).first() != None:
                            fk_model = m.query.filter_by(**kwargs).first()
                            # Grab the model ID
                            fk_model_id = fk_model.id
                            # Go back and loop through the relationships dict to find if substring matches to the original _id column name of the parent model
                            # Add to new_kwargs with the model ID
                            new_kwargs[[ke for ke, va in relationships.items() if k[:-1] in ke][0]] = fk_model_id

        entries = class_.query.filter_by(**new_kwargs).all()
        if key_valid(key):
            try:
                return jsonify({model : [entry.to_json(key) for entry in entries]})
            except TypeError:
                return unauthorized('Invalid Permissions')
        else:
            return unauthorized('Invalid credentials')
    else:
        return bad_request('Bad Request')

# ''' Users '''

# @api.route('/<key>/query/users/<int:id>')
# def get_user(key, id):
#     user = User.query.get_or_404(id)
#     if key_valid(key):
#         return jsonify(user.to_json(key))
#     else:
#         return unauthorized('Invalid credentials')

# def fix_string(string):
#     capitalised = string.capitalize()
#     hypen_stripped = capitalised.replace("-", " ");
#     return hypen_stripped

# # Traversing via Species
# # All Species
# # Not working, hmm
# @api.route('/<key>/query/species/all')
# @crossdomain(origin='*')
# def get_all_species(key):
#     all_species = Species.query.all()
#     species = {'species' : []}
#     for s in all_species:
#         sp = s.to_json(key)
#         species['species'].append(sp)

#     if key_valid(key):
#         return jsonify(species)
#     else:
#         return unauthorized('Invalid credentials')

# # Species by ID (not useful for client, useful for testing for now)
# @api.route('/<key>/query/species/id=<int:id>')
# @crossdomain(origin='*')
# def get_species(key, id):
#     species = Species.query.get_or_404(id)
#     if key_valid(key):
#         return jsonify(species.to_json(key))
#     else:
#         return unauthorized('Invalid credentials')

# # Go with name for protocol
# @api.route('/<key>/query/species/name=<name>')
# @crossdomain(origin='*')
# def get_species_name(key, name):
#     name = fix_string(name)
#     species = Species.query.filter_by(species_accepted=name).first()
#     if key_valid(key):
#         return jsonify(species.to_json(key))
#     else:
#         return unauthorized('Invalid credentials')

# # Taxonomy of species
# @api.route('/<key>/query/species/name=<name>/taxonomy')
# @crossdomain(origin='*')
# def get_species_taxonomy(key, name):
#     name = fix_string(name)
#     species = Species.query.filter_by(species_accepted=name).first()
#     taxonomy = species.taxonomies[0]
#     if key_valid(key):
#         return jsonify(taxonomy.to_json(key))
#     else:
#         return unauthorized('Invalid credentials')

# @api.route('/<key>/query/species/name=<name>/traits')
# @crossdomain(origin='*')
# def get_species_traits(key, name):
#     name = fix_string(name)
#     species = Species.query.filter_by(species_accepted=name).first()
#     traits = species.traitss[0]
#     if key_valid(key):
#         return jsonify(traits.to_json(key))
#     else:
#         return unauthorized('Invalid credentials')

# # Show all populations of Species
# @api.route('/<key>/query/species/name=<name>/populations')
# @crossdomain(origin='*')
# def get_species_populations(key, name):
#     name = fix_string(name)
#     species = Species.query.filter_by(species_accepted=name).first()
#     all_populations = species.populations
    
#     populations = {"populations" : []}
#     for population in all_populations:
#         pop = population.to_json(key)
#         populations['populations'].append(pop)
#     if key_valid(key):
#         return jsonify(populations)
#     else:
#         return unauthorized('Invalid credentials')

# # Show all publications featuring this species
# @api.route('/<key>/query/species/name=<name>/publication')
# @crossdomain(origin='*')
# def get_species_publication(key, name):
#     name = fix_string(name)
#     species = Species.query.filter_by(species_accepted=name).first()
#     publication = species.taxonomies[0].publication
#     if key_valid(key):
#         return jsonify(publication.to_json(key))
#     else:
#         return unauthorized('Invalid credentials')

# # Show all matrices of this species
# @api.route('/<key>/query/species/name=<name>/matrices')
# @crossdomain(origin='*')
# def get_species_matrices(key, name):
#     name = fix_string(name)
#     species = Species.query.filter_by(species_accepted=name).first()
#     all_populations = species.populations
    
#     matrices = {"matrices" : []}

#     for population in all_populations:
#         matrices_pop = population.study.matrices
#         for matrix in matrices_pop:
#             mat = matrix.to_json(key)
#             matrices['matrices'].append(mat)
#     if key_valid(key):
#         return jsonify(matrices)
#     else:
#         return unauthorized('Invalid credentials')


# @api.route('/<key>/query/taxonomy/<int:id>')
# @crossdomain(origin='*')
# def get_taxonomy(key, id):
#     taxonomy = Taxonomy.query.get_or_404(id)    
#     if key_valid(key):
#         return jsonify(taxonomy.to_json(key))
#     else:
#         return unauthorized('Invalid credentials')


# @api.route('/<key>/query/trait/<int:id>')
# @crossdomain(origin='*')
# def get_trait(key, id):
#     trait = Trait.query.get_or_404(id)    
#     if key_valid(key):
#         return jsonify(trait.to_json(key))
#     else:
#         return unauthorized('Invalid credentials')

# @api.route('/<key>/query/publication/<int:id>')
# @crossdomain(origin='*')
# def get_publication(key, id):
#     publication = Publication.query.get_or_404(id)
#     if key_valid(key):
#         return jsonify(publication.to_json(key))
#     else:
#         return unauthorized('Invalid credentials')

# @api.route('/<key>/query/study/<int:id>')
# @crossdomain(origin='*')
# def get_study(key, id):
#     study = Study.query.get_or_404(id)
#     if key_valid(key):
#         return jsonify(study.to_json(key))
#     else:
#         return unauthorized('Invalid credentials')

# # Not implemented yet
# @api.route('/<key>/query/authorcontact/<int:id>')
# @crossdomain(origin='*')
# def get_authorcontact(key, id):
#     authorcontact = AuthorContact.query.get_or_404(id)
#     if key_valid(key):
#         return jsonify(authorcontact.to_json(key))
#     else:
#         return unauthorized('Invalid credentials')

# # Not implemented yet
# @api.route('/<key>/query/additionalsource/<int:id>')
# @crossdomain(origin='*')
# def get_additionalsource(key, id):
#     additionalsource = AdditionalSource.query.get_or_404(id)
#     if key_valid(key):
#         return jsonify(additionalsource.to_json(key))
#     else:
#         return unauthorized('Invalid credentials')

# # Not implemented yet
# @api.route('/<key>/query/stage/<int:id>')
# @crossdomain(origin='*')
# def get_stage(key, id):
#     stage = Stage.query.get_or_404(id)
#     if key_valid(key):
#         return jsonify(stage.to_json(key))
#     else:
#         return unauthorized('Invalid credentials')

# # Not implemented yet
# @api.route('/<key>/query/stagetype/<int:id>')
# @crossdomain(origin='*')
# def get_stagetype(key, id):
#     stagetype = StageType.query.get_or_404(id)
#     if key_valid(key):
#         return jsonify(stagetype.to_json(key))
#     else:
#         return unauthorized('Invalid credentials')

# # Not implemented yet
# @api.route('/<key>/query/treatment/<int:id>')
# @crossdomain(origin='*')
# def get_treatment(key, id):
#     treatment = Treatment.query.get_or_404(id)    
#     if key_valid(key):
#         return jsonify(treatment.to_json(key))
#     else:
#         return unauthorized('Invalid credentials')

# @api.route('/<key>/query/treatmenttype/<int:id>')
# @crossdomain(origin='*')
# def get_treatmenttype(key, id):
#     treatmenttype = TreatmentType.query.get_or_404(id)    
#     if key_valid(key):
#         return jsonify(treatmenttype.to_json(key))
#     else:
#         return unauthorized('Invalid credentials')

# # Not implemented yet
# @api.route('/<key>/query/matrixstage/<int:id>')
# @crossdomain(origin='*')
# def get_matrixstage(key, id):
#     matrixstage = MatrixStage.query.get_or_404(id)
#     if key_valid(key):
#         return jsonify(matrixstage.to_json(key))
#     else:
#         return unauthorized('Invalid credentials')

# # Not implemented yet
# @api.route('/<key>/query/matrixvalue/<int:id>')
# @crossdomain(origin='*')
# def get_matrixvalue(key, id):
#     matrixvalue = MatrixValue.query.get_or_404(id)    
#     if key_valid(key):
#         return jsonify(matrixvalue.to_json(key))
#     else:
#         return unauthorized('Invalid credentials')

# @api.route('/<key>/query/matrix/<int:id>')
# @crossdomain(origin='*')
# def get_matrix(key, id):
#     matrix = Matrix.query.get_or_404(id)
#     if key_valid(key):
#         return jsonify(matrix.to_json(key))
#     else:
#         return unauthorized('Invalid credentials')

# # Not implemented yet
# @api.route('/<key>/query/interval/<int:id>')
# @crossdomain(origin='*')
# def get_interval(key, id):
#     interval = Interval.query.get_or_404(id)
#     if key_valid(key):
#         return jsonify(interval.to_json(key))
#     else:
#         return unauthorized('Invalid credentials')


# # Not implemented yet
# @api.route('/<key>/query/fixed/<int:id>')
# @crossdomain(origin='*')
# def get_fixed(key, id):
#     fixed = Fixed.query.get_or_404(id)
#     if key_valid(key):
#         return jsonify(fixed.to_json(key))
#     else:
#         return unauthorized('Invalid credentials')

# @api.route('/<key>/query/population/<int:id>')
# @crossdomain(origin='*')
# def get_population(key, id):
#     population = Population.query.get_or_404(id)
#     if key_valid(key):
#         return jsonify(population.to_json(key))
#     else:
#         return unauthorized('Invalid credentials'