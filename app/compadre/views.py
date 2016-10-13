from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response, jsonify
from flask.ext.login import login_required, current_user
from flask.ext.sqlalchemy import get_debug_queries
from . import compadre
from .. import db
from forms import EntryForm, SpeciesForm, TaxonomyForm, TraitForm, PopulationForm, PublicationForm, StudyForm, MatrixForm
from ..models import Permission, Role, User, \
                    IUCNStatus, ESAStatus, GrowthType, GrowthFormRaunkiaer, ReproductiveRepetition, \
                    DicotMonoc, AngioGymno, DavesGrowthType, SourceType, Database, Purpose, MissingData, ContentEmail, Ecoregion, Continent, InvasiveStatusStudy, InvasiveStatusElsewhere, StageTypeClass, \
                    TransitionType, MatrixComposition, Season, StudiedSex, Captivity, Species, Taxonomy, Trait, \
                    Publication, Study, AuthorContact, AdditionalSource, Population, Stage, StageType, Treatment, TreatmentType, \
                    MatrixStage, MatrixValue, Matrix, Interval, Fixed, Small, CensusTiming, Status, PurposeEndangered, PurposeWeed
from ..decorators import admin_required, permission_required, crossdomain

'''Migration functions, etc.'''
# Function to determine similarity between string a and b
def similar(a, b):
    from difflib import SequenceMatcher
    return SequenceMatcher(None, a, b).ratio()

# Function to create Unique ID from FORM VALUES
def create_uid(form):
    import re
    species_accepted = form.species_accepted.data
    journal = form.pub_title.data
    year_pub = form.year.data
    authors = form.authors.data[:15]
    pop_name = form.name.data
    composite = MatrixComposition.query.get(form.matrix_composition.data)
    composite = composite.comp_name
    treatment = form.treatment.data

    start_year = form.matrix_start.data[-4:]
    observation = form.observations.data
    matrix_a_string = form.matrix_a_string.data

    print(species_accepted, journal, year_pub, authors, pop_name, composite, treatment, start_year, observation, matrix_a_string)
    uid_concat = '{}{}{}{}{}{}{}{}{}{}'.format(species_accepted, journal, year_pub, authors, pop_name, composite, treatment, start_year, observation, matrix_a_string)
    uid_lower = uid_concat.lower()
    uid = re.sub('[\W_]+', '', uid_lower)

    return uid

# Base function to check UID against other UIDS from FORM
def check_uid(form):
    # Query the database for species matching the species_accepted form value
    species_accepted = form.species_accepted.data
    species = Species.query.filter_by(species_accepted=species_accepted).first()
    uid = create_uid(form)
    similarity = [[], None]
    if species != None:
        similarity[0] = []
        for population in species.populations:
            for matrix in population.matrices:
                ratio = similar(uid, matrix.uid)

                if ratio == 1:
                    similarity[1] = matrix
                elif ratio > 0.90 and ratio < 100:
                    similarity[0].append(matrix)
                else:
                    pass
    else: 
        similarity = check_for_duplicate_single_view(uid)

    return similarity

# Base test function to check UID against other UIDS from FORM
def check_uid_test(form):
    # Query the database for species matching the species_accepted form value
    species_accepted = form.species_accepted.data
    species = Species.query.filter_by(species_accepted=species_accepted).first()
    uid = create_uid(form)
    similarity = {'exact' : [], 'similar' : []}

    if species != None:
        for population in species.populations:
            for matrix in population.matrices:
                ratio = similar(uid, matrix.uid)
                if ratio == 1:
                    similarity['exact'].append(matrix)
                elif ratio > 0.90 and ratio < 100:
                    similarity['similar'].append(matrix)
                else:
                    pass
    else: 
        similarity = check_for_duplicate_single_view(uid)

    return similarity

# Base function to check UID against other UIDS from UID
def check_for_duplicate_single_view(uid): 
    all_matrices = Matrix.query.all()
    similarity = {'exact' : [], 'similar' : []}
    for matrix in all_matrices:
        ratio = similar(matrix.uid, uid)
        if ratio == 1:
            similarity['exact'].append(matrix)
        elif ratio > 0.90 and ratio < 100:
            similarity['similar'].append(matrix)
        else:
            pass
    return similarity

# return concetenated, cleansed UID string from dictionary
def return_con(obj):
    import re, string
    joined =''.join([value for key, value in obj.items()])
    lower = joined.lower()
    stripped = lower.replace(' ', '')
    alphanumeric = re.sub('[\W_]+', '', stripped)

    return alphanumeric

# create the UID here - takes in an object, takes the values it requires, returns the cleansed version as a string
def create_id_string(dict):
    new_dict = {
    "species_accepted" : dict["species_accepted"], #
    "journal" : dict['journal'], #
    "year_pub" : dict["year"], #
    "authors" : dict["authors"][:15], #
    "name" : dict["name"], #
    "matrix_composite" : dict['matrix_composition_id'], #
    "matrix_treatment" : dict['treatment_id'], #
    "matrix_start_year" : dict['matrix_start_year'], #
    "observation" : dict['observations'], #
    "matrix_a_string" : dict['matrix_a_string'] #
    }
    return return_con(new_dict)

# determines the similary between two values
def similar(a, b):
    from difflib import SequenceMatcher
    return SequenceMatcher(None, a, b).ratio()

# this is to check one object against all others, returning jsonified similar records above 96% similarity
def check_for_duplicate_single(obj):
    uid_string = create_id_string(obj)    
    all_matrices = Matrix.query.all()
    similar = []
    for matrix in all_matrices:
        ratio = similar(matrix.uid, uid_string)
        if ratio > 0.90:
            similar.append(matrix)

    return jsonify(similar)

# build an Entry using the data from the sanitised object, submitting to database
def add_to_classes(data):
    from ..conversion.models import Taxonomy, Publication, Population, Trait, Matrix, Study, Entry
    
    matrix = Matrix(data['treatment_id'], data['matrix_split'], data['matrix_composition_id'], data['survival_issue'], data['periodicity'], data['matrix_criteria_size'], \
        data['matrix_criteria_ontogeny'], data['matrix_criteria_age'], data['matrix_start_month'], data['matrix_start_year'], data['matrix_end_month'], data['matrix_end_year'], \
        data['matrix_start_season_id'], data['matrix_end_season_id'], data['matrix_fec'], data['matrix_a_string'], data['matrix_class_string'], data['studied_sex_id'], \
        data['captivity_id'], data['matrix_dimension'], data['observations'])
    study = Study(data['study_duration'], data['study_start'], data['study_end'])
    tax = Taxonomy(data['species_author'], data['species_accepted'], data['authority'], data['tpl_version'], data['taxonomic_status_id'], data['infraspecies_accepted'], data['species_epithet_accepted'], \
        data['genus_accepted'], data['genus'], data['family'], data['tax_order'], data['tax_class'], data['phylum'], data['kingdom'])
    pop = Population(data['species_author'], data['name'], data['geometries_lat_min'], data['geometries_lon_deg'], data['geometries_lat_ns'], data['geometries_lat_we'], \
        data['geometries_lat_sec'], data['geometries_lon_sec'], data['geometries_lon_min'], data['geometries_lat_deg'], data['geometries_altitude'], data['ecoregion_id'], \
        data['country'], data['continent_id'], matrix)
    trait = Trait(data['growth_type_id'], data['dicot_monoc_id'], data['angio_gymno_id'])
    pub = Publication(data['authors'], data['year'], data['DOI_ISBN'], data['additional_source_string'], tax, pop, trait, study, data['pub_name'])

    entry = Entry(pub, study, pop, tax, trait, matrix)
    
    return entry.submit_to_database()

# Convert CSV headers
def convert_all_headers(dict):
    new_dict = {}
    new_dict['additional_source_string'] = dict['AdditionalSource']
    new_dict['matrix_end_season_id'] = dict['MatrixEndSeason']
    new_dict['growth_type_id'] = dict['GrowthType']
    new_dict['geometries_lat_sec'] = dict['LatSec']
    new_dict['study_duration'] = dict['StudyDuration']
    new_dict['matrix_values_c'] = dict['matrixC']
    new_dict['geometries_lat_we'] = dict['LonWE']
    new_dict['journal'] = dict['Journal']
    new_dict['infraspecies_accepted'] = dict['InfraspecificAccepted']
    new_dict['matrix_values_a'] = dict['matrixA']
    new_dict['matrix_a_string'] = dict['matrixA']
    new_dict['matrix_start_year'] = dict['MatrixStartYear']
    new_dict['kingdom'] = dict['Kingdom']
    new_dict['DOI_ISBN'] = dict['DOI.ISBN']
    new_dict['genus'] = dict['Genus']
    new_dict['species_epithet_accepted'] = dict['SpeciesEpithetAccepted']
    new_dict['name'] = dict['MatrixPopulation']
    new_dict['geometries_lat_ns'] = dict['LatNS']
    new_dict['number_populations'] = dict['NumberPopulations']
    new_dict['matrix_fec'] = dict['MatrixFec']
    new_dict['matrix_criteria_size'] = dict['CriteriaSize']
    new_dict['geometries_lon_min'] = dict['LonMin']
    new_dict['matrix_start_month'] = dict['MatrixStartMonth']
    new_dict['authors'] = dict['Authors']
    new_dict['geometries_lon_sec'] = dict['LonSec']
    new_dict['matrix_dimension'] = dict['MatrixDimension']
    new_dict['geometries_altitude'] = dict['Altitude']
    new_dict['geometries_lat_min'] = dict['LatMin']
    new_dict['observations'] = dict['Observation']
    new_dict['study_start'] = dict['StudyStart']
    new_dict['country'] = dict['Country']
    new_dict['survival_issue'] = dict['SurvivalIssue']
    new_dict['geometries_lat_deg'] = dict['LatDeg']
    new_dict['dicot_monoc_id'] = dict['DicotMonoc']
    new_dict['angio_gymno_id'] = dict['AngioGymno']
    new_dict['matrix_criteria_ontogeny'] = dict['CriteriaOntogeny']
    new_dict['year'] = dict['YearPublication']
    new_dict['species_accepted'] = dict['SpeciesAccepted']
    new_dict['periodicity'] = dict['AnnualPeriodicity']
    new_dict['matrix_end_year'] = dict['MatrixEndYear']
    new_dict['tax_order'] = dict['Order']
    new_dict['studied_sex_id'] = dict['StudiedSex']
    new_dict['geometries_lon_deg'] = dict['LonDeg']
    new_dict['genus_accepted'] = dict['GenusAccepted']
    new_dict['family'] = dict['Family']
    new_dict['matrix_end_month'] = dict['MatrixEndMonth']
    new_dict['matrix_composition_id'] = dict['MatrixComposite']
    new_dict['matrix_values_a'] = dict['matrixF']
    new_dict['matrix_start_season_id'] = dict['MatrixStartSeason']
    new_dict['populations_name'] = dict['MatrixPopulation']
    new_dict['species_author'] = dict['SpeciesAuthor']
    new_dict['tax_class'] = dict['Class']
    new_dict['continent_id'] = dict['Continent']
    new_dict['treatment_id'] = dict['MatrixTreatment']
    new_dict['matrix_class_string'] = dict['classnames']
    new_dict['phylum'] = dict['Phylum']
    new_dict['tpl_version'] = dict['TPLVersion']
    new_dict['matrix_criteria_age'] = dict['CriteriaAge']
    new_dict['study_end'] = dict['StudyEnd']
    new_dict['captivity_id'] = dict['MatrixCaptivity']
    new_dict['ecoregion_id'] = dict['Ecoregion']
    new_dict['matrix_values_a'] = dict['matrixU']
    new_dict['authority'] = dict['Authority']
    new_dict['matrix_split'] = dict['MatrixSplit']

    return new_dict
'''End Migration functions, etc.'''

'''Routing webpages'''
# This blueprint handles the validation, error checking and duplicates. Basically ensuring that the database runs smoothly.
@compadre.route('/', methods=['GET', 'POST'])
def homepage():
    form = EntryForm()
    similar = None
    exact = None

    if form.validate_on_submit():
        similarity = check_uid_test(form)

        print "Similarity", similarity
        if len(similarity['exact']) > 0:
            exact = similarity['exact']
        else: 
            exact = None

        if len(similarity['similar']) > 0:
            similar = similarity['similar']
        else:
            similar = None        

    return render_template('test.html', form=form, similar=similar, exact=exact)

''' End Routing '''