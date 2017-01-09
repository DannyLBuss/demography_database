#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import os, csv
COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

if os.path.exists('.env'):
    print('Importing environment from .env...')
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]

from app import create_app, db
from app.models import User, Role, Permission, \
    IUCNStatus, ESAStatus, OrganismType, GrowthFormRaunkiaer, ReproductiveRepetition, \
    DicotMonoc, AngioGymno, SpandExGrowthType, SourceType, Database, Purpose, MissingData, ContentEmail, Ecoregion, Continent, InvasiveStatusStudy, InvasiveStatusElsewhere, StageTypeClass, \
    TransitionType, MatrixComposition, StartSeason, StudiedSex, Captivity, Species, Taxonomy, Trait, \
    Publication, Study, AuthorContact, AdditionalSource, Population, Stage, StageType, Treatment, \
    MatrixStage, MatrixValue, Matrix, Interval, Fixed, Small, CensusTiming, Status, PurposeEndangered, PurposeWeed, Version, Institute, EndSeason
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role,
                Permission=Permission, IUCNStatus=IUCNStatus, ESAStatus=ESAStatus, Species=Species, \
                Taxonomy=Taxonomy, OrganismType=OrganismType, GrowthFormRaunkiaer=GrowthFormRaunkiaer, \
                ReproductiveRepetition=ReproductiveRepetition, DicotMonoc=DicotMonoc, AngioGymno=AngioGymno, SpandExGrowthType=SpandExGrowthType, Trait=Trait, \
                Publication=Publication, SourceType=SourceType, Database=Database, Purpose=Purpose, MissingData=MissingData, \
                AuthorContact=AuthorContact, ContentEmail=ContentEmail, Population=Population, Ecoregion=Ecoregion, Continent=Continent, \
                StageType=StageType, StageTypeClass=StageTypeClass, TransitionType=TransitionType, MatrixValue=MatrixValue, \
                MatrixComposition=MatrixComposition, StartSeason=StartSeason, StudiedSex=StudiedSex, Captivity=Captivity, MatrixStage=MatrixStage,\
                Matrix=Matrix, Interval=Interval, Fixed=Fixed, Small=Small, CensusTiming=CensusTiming, Study=Study, Status=Status, InvasiveStatusStudy=InvasiveStatusStudy, InvasiveStatusElsewhere=InvasiveStatusElsewhere, \
                PurposeEndangered=PurposeEndangered, PurposeWeed=PurposeWeed, Version=Version, Institute=Institute, EndSeason=EndSeason)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test(coverage=False):
    """Run the unit tests."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()


@manager.command
def profile(length=25, profile_dir=None):
    """Start the application under the code profiler."""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
                                      profile_dir=profile_dir)
    app.run()

def UnicodeDictReader(utf8_data, **kwargs):
    csv_reader = csv.DictReader(utf8_data, **kwargs)
    for row in csv_reader:
        yield {key: unicode(value, 'latin-1') for key, value in row.iteritems()}


@manager.command
def csv_migrate():
    import csv

    input_file = UnicodeDictReader(open("app/compadre/compadreFlat3.csv", "rU"))

    all_deets = []   

    for i, row in enumerate(input_file):
        if i > 6235:                      
            data = convert_all_headers(row)
            entry = add_to_classes(data)
            all_deets.append(entry)
            submit(entry)
    return 


def versions_to_nil(array):
    for x in array:
        if x.version is None:
            x.version = 0
            x.version_of_id = x.id
            
            db.session.add(x)
            db.session.commit()

@manager.command
def version_null_to_0():
    print "Setting ALL null versions to 0"

    print "Resetting Species..."
    versions_to_nil(Species.query.all())

    print "Resetting Taxonomy..."
    versions_to_nil(Taxonomy.query.all())
    
    print "Resetting Matrix..."
    versions_to_nil(Matrix.query.all())

    print "Resetting Study..."
    versions_to_nil(Study.query.all())

    print "Resetting Publication..."
    versions_to_nil(Publication.query.all())

    print "Resetting Trait..."
    versions_to_nil(Trait.query.all())

    print "Resetting Population..."
    versions_to_nil(Population.query.all())

    print "Resetting AuthorContact..."
    versions_to_nil(AuthorContact.query.all())

    print "Resetting Stage..."
    versions_to_nil(Stage.query.all())

    print "Resetting StageType..."
    versions_to_nil(StageType.query.all())

    print "Resetting MatrixStage..."
    versions_to_nil(MatrixStage.query.all())



@manager.command
def delete_table_data():
    response = raw_input("Are you sure you want to delete all data? (y/n): ")

    if response == "y":
        Taxonomy.query.delete()
        Matrix.query.delete()
        Population.query.delete()
        Study.query.delete()    
        Publication.query.delete()    
        Trait.query.delete()
        Species.query.delete()
        Version.query.delete()
        db.session.commit()
        print "All data has been removed"
    elif response == "n":
        print "Table data not deleted"
        pass
    else:
        print("Valid response required (y/n)")
    return    


# This can be padded out for future stuff...
def coerce_boolean(string):
    true = ['Yes', 'Divided']
    false = ['No', 'Undivided']

    if string in true:
        return True
    elif string in false:
        return False


def return_con(obj):
    import re, string
    joined =''.join([value for key, value in obj.items()])
    lower = joined.lower()
    stripped = lower.replace(' ', '')
    alphanumeric = re.sub('[\W_]+', '', stripped)

    return alphanumeric

def create_id_string(dict):
    new_dict = {
    "species_accepted" : dict["species_accepted"], #
    "journal" : dict['journal'], #
    "year_pub" : dict["year"], #
    "authors" : dict["authors"][:15], #first15 (if > 15, add character to end >)
    "name" : dict["name"], #
    "matrix_composite" : dict['matrix_composition_id'], #
    "matrix_treatment" : dict['treatment_id'], #
    "matrix_start_year" : dict['matrix_start_year'], #
    "observation" : dict['observations'], #
    "matrix_a_string" : dict['matrix_a_string'] #
    }
    return return_con(new_dict)

def similar(a, b):
    from difflib import SequenceMatcher
    return SequenceMatcher(None, a, b).ratio()


def generate_uid(species, publication, population, matrix):
    import re

    species_accepted = species.species_accepted
    journal = publication.name
    year_pub = publication.year

    try:
        authors = publication.authors[:15].encode('utf-8')
    except:
        authors = ''

    try:
        pop_name = population.name.encode('utf-8')[:15]
    except:
        pop_name = ''
    
    try:
        composite = matrix.matrix_composition.comp_name
    except AttributeError:
        composite = ''

    try:
        start_year = matrix.matrix_start_year
    except TypeError:
        start_year = ''

    import time
    timestamp = time.time()
    
    uid_concat = '{}{}{}{}{}{}{}{}'.format(species_accepted, journal, year_pub, authors, pop_name, composite, start_year, timestamp)
    uid_lower = uid_concat.lower()
    uid = re.sub('[\W_]+', '', uid_lower)
    return uid

@manager.command
def submit_new(data):
    species = Species.query.filter_by(species_accepted=data["species_accepted"]).first()

    if species == None:
        species = Species(species_accepted=data["species_accepted"])        
        species.gbif_taxon_key = data["species_gbif_taxon_key"]
        species.species_author = data["species_author"]
        species.species_accepted = data["species_accepted"]        
        species.species_esa_status = ESAStatus.query.filter_by(status_code=data["species_esa_status_id"]).first()        
        species.species_common = data["species_common"]
        species.species_iucn_status = IUCNStatus.query.filter_by(status_code=data["species_iucn_status_id"]).first()

        db.session.add(species)
        db.session.commit()

        ''' Species Version '''
        species_version = Version()
        species_version.version_number = 0
        species_version.species = species
        db.session.add(species_version) 
        db.session.commit()  
        species_version.version_of_id = species_version.id
        species_version.checked = True
        species_version.checked_count = 1
        species_version.statuses = Status.query.filter_by(status_name="Green").first()
        species_version.user = User.query.filter_by(username="admin").first()
        species_version.database = Database.query.filter_by(database_name="COMPADRE 4").first()
        species.version_latest = 1
        species.version_original = 1

        db.session.add(species_version)
        db.session.commit()

    ''' Publication '''    
    if data["publication_DOI_ISBN"] == None:
        publication = Publication.query.filter_by(authors=data["publication_authors"]).filter_by(year=data["publication_year"]).filter_by(name=data["publication_journal_name"]).first()
    else: 
        publication = Publication.query.filter_by(DOI_ISBN=data["publication_DOI_ISBN"]).first()    
    if publication == None:
        publication = Publication()
        publication.authors = data["publication_authors"]
        publication.year = data["publication_year"]
        publication.DOI_ISBN = data["publication_DOI_ISBN"]
        publication.additional_source_string = data["publication_additional_source_string"]
        publication.name = data["publication_journal_name"]

        db.session.add(publication)
        db.session.commit()

        ''' Publication Version '''
        publication_version = Version()
        publication_version.version_number = 0
        publication_version.publication = publication
        db.session.add(publication_version) 
        db.session.commit()  
        publication_version.version_of_id = publication_version.id
        publication_version.checked = True
        publication_version.checked_count = 1
        publication_version.statuses = Status.query.filter_by(status_name="Green").first()
        publication_version.user = User.query.filter_by(username="admin").first()
        publication_version.database = Database.query.filter_by(database_name="COMPADRE 4").first()
        publication.version_latest = 1
        publication.version_original = 1

        db.session.add(publication_version)
        db.session.commit()

    ''' Trait '''
    spand_ex_growth_type = SpandExGrowthType.query.filter_by(type_name=data["trait_spand_ex_growth_type_id"]).first()
    dicot_monoc = DicotMonoc.query.filter_by(dicot_monoc_name=data["trait_dicot_monoc_id"]).first()
    growth_form_raunkiaer = GrowthFormRaunkiaer.query.filter_by(form_name=data["trait_growth_form_raunkiaer_id"]).first()
    organism_type = OrganismType.query.filter_by(type_name=data["trait_organism_type_id"]).first()
    angio_gymno = AngioGymno.query.filter_by(angio_gymno_name=data["trait_angio_gymno_id"]).first()

    trait = Trait.query.filter_by(species_id=species.id).first()

    if trait == None:
        trait = Trait()
        trait.species_id = species.id
        trait.organism_type = organism_type
        trait.dicot_monoc = dicot_monoc
        trait.angio_gymno = angio_gymno
        trait.spand_ex_growth_type = spand_ex_growth_type
        trait.growth_form_raunkiaer = growth_form_raunkiaer

        db.session.add(trait)
        db.session.commit()

        ''' Trait Version '''
        trait_version = Version()
        trait_version.version_number = 0
        trait_version.trait = trait
        db.session.add(trait_version) 
        db.session.commit()  
        trait_version.version_of_id = trait_version.id
        trait_version.checked = True
        trait_version.checked_count = 1
        trait_version.statuses = Status.query.filter_by(status_name="Green").first()
        trait_version.user = User.query.filter_by(username="admin").first()
        trait_version.database = Database.query.filter_by(database_name="COMPADRE 4").first()
        trait.version_latest = 1
        trait.version_original = 1

        db.session.add(trait_version)
        db.session.commit()

    ''' Study '''
    # What if all none? Will they be grouped together?
    purpose_endangered = PurposeEndangered.query.filter_by(purpose_name=data["study_purpose_endangered_id"]).first()
    purpose_weed = PurposeWeed.query.filter_by(purpose_name="study_purpose_weed_id").first()

    study = Study.query.filter_by(publication_id=publication.id, study_start=data["study_start"], study_end=data["study_end"]).first()
    if study == None:
        study = Study()
        study.study_duration = data["study_duration"]
        study.study_start = data["study_start"]
        study.study_end = data["study_end"]
        study.publication_id = publication.id
        study.number_populations = data["study_number_populations"]

        db.session.add(study)
        db.session.commit()

        ''' Study Version '''
        study_version = Version()
        study_version.version_number = 0
        study_version.study = study
        db.session.add(study_version) 
        db.session.commit()  
        study_version.version_of_id = study_version.id
        study_version.checked = True
        study_version.checked_count = 1
        study_version.statuses = Status.query.filter_by(status_name="Green").first()
        study_version.user = User.query.filter_by(username="admin").first()
        study_version.database = Database.query.filter_by(database_name="COMPADRE 4").first()
        study.version_latest = 1
        study.version_original = 1

        db.session.add(study_version)
        db.session.commit()


    ''' Population '''
    invasive_status_study = InvasiveStatusStudy.query.filter_by(status_name=data["population_invasive_status_study_id"]).first()
    invasive_status_elsewhere = InvasiveStatusStudy.query.filter_by(status_name=data["population_invasive_status_elsewhere_id"]).first()
    ecoregion = Ecoregion.query.filter_by(ecoregion_code=data["population_ecoregion_id"]).first()
    continent = Continent.query.filter_by(continent_name=data["population_continent_id"]).first()

    pop = Population.query.filter_by(name=data["population_name"], species_id=species.id, publication_id=publication.id).first()



    if pop == None:
        pop = Population()
        pop.species_author = data["species_author"]
        pop.name = data["population_name"]
        pop.species_id = species.id
        pop.publication_id = publication.id
        pop.study_id = study.id

        pop.longitude = data["population_longitude"]
        pop.latitude = data["population_latitude"]
        pop.altitude = data["population_altitude"]
        pop.pop_size = data["population_pop_size"]
        pop.country = data["population_country"]

        pop.invasive_status_study = invasive_status_study
        pop.invasive_status_elsewhere = invasive_status_elsewhere
        pop.ecoregion = ecoregion
        pop.continent = continent

        db.session.add(pop)
        db.session.commit()

        ''' Population Version '''
        population_version = Version()
        population_version.version_number = 0
        population_version.population = pop
        db.session.add(population_version) 
        db.session.commit()  
        population_version.version_of_id = population_version.id
        population_version.checked = True
        population_version.checked_count = 1
        population_version.statuses = Status.query.filter_by(status_name="Green").first()
        population_version.user = User.query.filter_by(username="admin").first()
        population_version.database = Database.query.filter_by(database_name="COMPADRE 4").first()
        pop.version_latest = 1
        pop.version_original = 1


        db.session.add(population_version)
        db.session.commit()

    ''' Taxonomy '''
    tax = Taxonomy.query.filter_by(species_id=species.id).first()
    if tax == None:
        tax = Taxonomy()
        tax.species_author = species.species_author
        tax.species_accepted = species.species_accepted
        tax.authority = None
        tax.tpl_version = None
        tax.infraspecies_accepted = None
        tax.species_epithet_accepted = None
        tax.genus_accepted = data["taxonomy_genus_accepted"]
        tax.genus = data["taxonomy_genus"]
        tax.family = data["taxonomy_family"]
        tax.tax_order = data["taxonomy_order"]
        tax.tax_class = data["taxonomy_class"]
        tax.phylum = data["taxonomy_phylum"]
        tax.kingdom = data["taxonomy_kingdom"]
        tax.species = species
        tax.publication = publication
        tax.col_check_date = data["taxonomy_col_check_date"]
        tax.col_check_ok = data["taxonomy_col_check_ok"]

        db.session.add(tax)
        db.session.commit()

        ''' Taxonomy Version '''
        taxonomy_version = Version()
        taxonomy_version.version_number = 0
        taxonomy_version.taxonomy = tax
        db.session.add(taxonomy_version) 
        db.session.commit()  
        taxonomy_version.version_of_id = taxonomy_version.id
        taxonomy_version.checked = True
        taxonomy_version.checked_count = 1
        taxonomy_version.statuses = Status.query.filter_by(status_name="Green").first()
        taxonomy_version.user = User.query.filter_by(username="admin").first()
        taxonomy_version.database = Database.query.filter_by(database_name="COMPADRE 4").first()
        tax.version_latest = 1
        tax.version_original = 1

        db.session.add(taxonomy_version)
        db.session.commit()

    ''' Matrix '''
    matrix = Matrix()
    treatment = Treatment.query.filter_by(treatment_name=data["matrix_treatment_id"]).first()
    
    if treatment == None:
        treatment = Treatment(treatment_name=data["matrix_treatment_id"])
    
    matrix.treatment = treatment
    matrix.matrix_split = data["matrix_split"]
    
    composition = MatrixComposition.query.filter_by(comp_name=data["matrix_composition_id"]).first()
    

    matrix.matrix_composition = composition

    
    matrix.survival_issue = data["matrix_survival_issue"]    
    matrix.periodicity = data["matrix_periodicity"]
    matrix.matrix_criteria_size = data["matrix_criteria_size"]
    matrix.matrix_criteria_ontogeny = coerce_boolean(data["matrix_criteria_ontogeny"])
    matrix.matrix_criteria_age = coerce_boolean(data["matrix_criteria_age"]) 
    
    matrix.matrix_start_month = data["matrix_start_month"]
    matrix.matrix_end_month = data["matrix_end_month"]
    matrix.matrix_start_year = data["matrix_start_year"]
    matrix.matrix_end_year = data["matrix_end_year"]

    matrix.studied_sex = StudiedSex.query.filter_by(sex_code=data["matrix_studied_sex_id"]).first()


    start_season = StartSeason.query.filter_by(season_id=data["matrix_start_season_id"]).first()
    end_season = EndSeason.query.filter_by(season_id=data["matrix_end_season_id"]).first()

    if start_season != None:
        matrix.start_season = start_season

    if end_season != None:
        matrix.end_season = end_season
        
    matrix.matrix_fec = coerce_boolean(data["matrix_fec"])

    matrix.matrix_a_string = data["matrix_a_string"]
    matrix.matrix_f_string = data["matrix_f_string"]
    matrix.matrix_u_string = data["matrix_u_string"]
    matrix.matrix_c_string = data["matrix_c_string"]

    matrix.non_independence = data["matrix_non_independence"]
    matrix.dimension = data["matrix_dimension"]
    matrix.non_independence_author = data["matrix_non_independence_author"]
    matrix.matrix_complete = data["matrix_complete"]
    matrix.vectors_includes_na = data["matrix_vectors_includes_na"]
    matrix.class_number = data["matrix_class_number"]
    matrix.observations = data["matrix_observations"]

    captivities = Captivity.query.filter_by(cap_code=data["matrix_captivity_id"]).first()

    matrix.captivities = captivities
    matrix.class_author = data["matrix_class_author"]
    matrix.matrix_difficulty = data["matrix_difficulty"]
    matrix.independent = data["matrix_independent"]
    matrix.seasonal = data["matrix_seasonal"]

    matrix.uid = generate_uid(species, publication, pop, matrix)

    matrix.population = pop
    matrix.study = study

    db.session.add(matrix)
    db.session.commit()

    ''' matrix Version '''
    matrix_version = Version()
    matrix_version.version_number = 0
    matrix_version.matrix = matrix
    db.session.add(matrix_version) 
    db.session.commit()
    matrix_version.version_of_id = matrix_version.id
    matrix_version.checked = True
    matrix_version.checked_count = 1
    matrix_version.statuses = Status.query.filter_by(status_name="Green").first()
    matrix_version.user = User.query.filter_by(username="admin").first()
    matrix_version.database = Database.query.filter_by(database_name="COMPADRE 4").first()
    matrix.version_latest = 1
    matrix.version_original = 1

    db.session.add(matrix_version)
    db.session.commit()

    ''' Fixed '''

    fixed = Fixed.query.filter_by(matrix=matrix).first()

    if fixed == None:
        fixed = Fixed()
        fixed.matrix = matrix
        fixed.census_timings = CensusTiming.query.filter_by(census_name=data["fixed_census_timing_id"]).first()
        fixed.seed_stage_error = data["fixed_seed_stage_error"]
        fixed.smalls = Small.query.filter_by(small_name=data["fixed_small_id"]).first()

        db.session.add(fixed)
        db.session.commit()

        ''' fixed Version '''
        fixed_version = Version()
        fixed_version.version_number = 0
        fixed_version.fixed = fixed
        db.session.add(fixed_version) 
        db.session.commit()
        fixed_version.version_of_id = fixed_version.id
        fixed_version.checked = True
        fixed_version.checked_count = 1
        fixed_version.statuses = Status.query.filter_by(status_name="Green").first()
        fixed_version.user = User.query.filter_by(username="admin").first()
        fixed_version.database = Database.query.filter_by(database_name="COMPADRE 4").first()
        fixed.version_latest = 1
        fixed.version_original = 1

        db.session.add(fixed_version)
        db.session.commit()





@manager.command
def csv_migrate_new():
    import csv

    input_file = UnicodeDictReader(open("app/compadre/compadre_4_unicode.csv", "rU"))

    all_deets = []   

    for i, row in enumerate(input_file):
        print i              
        data = convert_all_headers_new(row)
        submit_new(data)

    return 

def convert_all_headers_new(dict):
    import re

    new_dict = {}

    new_dict["species_author"] = dict["species_author"]
    new_dict["species_accepted"] = dict["species_accepted"]
    new_dict["species_common"]= dict["species_common"]
    new_dict["taxonomy_genus"] = dict["taxonomy_genus"]
    new_dict["taxonomy_family"] = dict["taxonomy_family"]
    new_dict["taxonomy_order"] = dict["taxonomy_order"]
    new_dict["taxonomy_class"] = dict["taxonomy_class"]
    new_dict["taxonomy_phylum"] = dict["taxonomy_phylum"]
    new_dict["taxonomy_kingdom"] = dict["taxonomy_kingdom"]
    new_dict["trait_organism_type_id"] = dict["trait_organism_type"]
    new_dict["trait_dicot_monoc_id"] = dict["trait_dicot_monoc"]
    new_dict["trait_angio_gymno_id"] = dict["trait_angio_gymno"]
    new_dict["publication_authors"] = dict["publication_authors"]
    new_dict["publication_journal_name"] = dict["publication_journal_name"]
    new_dict["publication_year"] = dict["publication_year"]
    new_dict["publication_DOI_ISBN"] = dict["publication_DOI_ISBN"]
    new_dict["publication_additional_source_string"] = dict["publication_additional_source_string"]
    new_dict["study_duration"] = dict["study_duration"]
    new_dict["study_start"] = dict["study_start"]
    new_dict["study_end"] = dict["study_end"]
    new_dict["matrix_periodicity"] = dict["matrix_periodicity"]
    new_dict["study_number_populations"] = dict["study_number_populations"]
    new_dict["matrix_criteria_size"] = dict["matrix_criteria_size"]
    new_dict["matrix_criteria_ontogeny"] = dict["matrix_criteria_ontogeny"]
    new_dict["matrix_criteria_age"] = dict["matrix_criteria_age"]
    new_dict["population_name"] = dict["population_name"]
    new_dict["population_latitude"] = dict["population_latitude"]
    new_dict["population_longitude"] = dict["population_longitude"]
    new_dict["population_altitude"]= dict["population_altitude"]
    new_dict["population_country"] = dict["population_country"]
    new_dict["population_continent_id"] = dict["population_continent"]
    new_dict["population_ecoregion_id"] = dict["population_ecoregion"]
    new_dict["matrix_studied_sex_id"] = dict["matrix_studied_sex"]
    new_dict["matrix_composition_id"] = dict["matrix_composition"]
    new_dict["matrix_treatment_id"] = dict["matrix_treatment_type"]
    new_dict["matrix_captivity_id"] = dict["matrix_captivity"]
    new_dict["matrix_start_year"] = dict["matrix_start_year"]
    new_dict["matrix_start_season_id"] = dict["matrix_start_season"]
    new_dict["matrix_start_month"] = dict["matrix_start_month"]
    new_dict["matrix_end_year"] = dict["matrix_end_year"]
    new_dict["matrix_end_season_id"] = dict["matrix_end_season"]
    new_dict["matrix_end_month"] = dict["matrix_end_month"]
    new_dict["matrix_split"] = dict["matrix_split"]
    new_dict["matrix_fec"] = dict["matrix_fec"]
    new_dict["matrix_observations"]= dict["matrix_observations"]
    new_dict["matrix_dimension"] = dict["matrix_dimension"]
    new_dict["matrix_survival_issue"] = dict["matrix_survival_issue"]
    new_dict["matrix_a_string"] = dict["matrix_a_string"]
    new_dict["matrix_c_string"] = dict["matrix_c_string"]
    new_dict["matrix_f_string"] = dict["matrix_f_string"]
    new_dict["matrix_u_string"] = dict["matrix_u_string"]
    new_dict["matrix_class_organized"] = dict["matrix_class_organized"]
    new_dict["matrix_class_author"] = dict["matrix_class_author"]
    new_dict["matrix_class_number"] = dict["matrix_class_number"]
    new_dict["matrix_vectors_includes_na"] = dict["matrix_vectors_includes_na"]
    new_dict["population_pop_size"] = dict["population_pop_size"]
    new_dict["species_iucn_status_id"] = dict["species_iucn_status"]
    new_dict["species_esa_status_id"] = dict["species_esa_status_id"]
    new_dict["population_invasive_status_study_id"] = dict["population_invasive_status_study"]
    new_dict["population_invasive_status_elsewhere_id"] = dict["population_invasive_status_elsewhere"]
    new_dict["study_purpose_endangered_id"] = dict["study_purpose_endangered"]
    new_dict["study_purpose_weed_id"] = dict["study_purpose_weed"]
    new_dict["trait_spand_ex_growth_type_id"] = dict["trait_spand_ex_growth_type"]
    new_dict["trait_growth_form_raunkiaer_id"] = dict["trait_growth_form_raunkiaer"]
    new_dict["fixed_census_timing_id"] = dict["fixed_census_timing"]
    new_dict["fixed_small_id"] = dict["fixed_small"]
    new_dict["fixed_seed_stage_error"] = dict["fixed_seed_stage_error"]
    new_dict["species_gbif_taxon_key"] = dict["species_gbif_taxon_key"]
    new_dict["version_checked"] = dict["matrix_checked"]
    new_dict["version_checked_count"] = dict["matrix_checked_count"]
    new_dict["taxonomy_genus_accepted"] = dict["taxonomy_genus_accepted"]
    new_dict["matrix_independent"] = dict["matrix_independent"]
    new_dict["matrix_non_independence"] = dict["matrix_non_independence"]
    new_dict["matrix_non_independence_author"] = dict["matrix_non_independence_author"]
    new_dict["matrix_difficulty"] = dict["matrix_difficulty"]
    new_dict["matrix_complete"] = dict["matrix_complete"]
    new_dict["matrix_seasonal"] = dict["matrix_seasonal"]
    new_dict["database_master_version"] = dict["database_master_version"]
    new_dict["database_date_created"] = dict["database_date_created"]
    new_dict["database_number_species_accepted"] = dict["database_number_species_accepted"]
    new_dict["database_number_studies"] = dict["database_number_studies"]
    new_dict["database_number_matrices"] = dict["database_number_matrices"]
    new_dict["database_agreement"] = dict["database_agreement"]
    new_dict["taxonomy_col_check_ok"] = dict["taxonomy_col_check_ok"]
    new_dict["taxonomy_col_check_date"]= dict["taxonomy_col_check_date"]
    new_dict["matrix_independence_origin"] = dict["matrix_independence_origin"]

    for key, value in new_dict.iteritems():
        if value == "NA":
            new_dict[key] = None
        if value == "":
            new_dict[key] = None
        if value == "None":
            new_dict[key] = None


    return new_dict


@manager.command
def migrate_meta():
    from app.models import User, Role, Permission, \
    IUCNStatus, ESAStatus, OrganismType, GrowthFormRaunkiaer, ReproductiveRepetition, \
    DicotMonoc, AngioGymno, SpandExGrowthType, SourceType, Database, Purpose, MissingData, ContentEmail, Ecoregion, Continent, InvasiveStatusStudy, InvasiveStatusElsewhere, StageTypeClass, \
    TransitionType, MatrixComposition, StartSeason, StudiedSex, Captivity, Species, Taxonomy, Trait, \
    Publication, Study, AuthorContact, AdditionalSource, Population, Stage, StageType, Treatment, \
    MatrixStage, MatrixValue, Matrix, Interval, Fixed, Small, CensusTiming, PurposeEndangered, PurposeWeed, Institute

    print "Migrating Meta Tables..."
    try:
        Role.insert_roles()
        Species.migrate()
        Taxonomy.migrate()
        Trait.migrate()
        Publication.migrate()
        AuthorContact.migrate()
        Population.migrate()
        StageType.migrate()
        MatrixValue.migrate()
        Matrix.migrate()
        Fixed.migrate()
        Study.migrate()
        User.migrate()
        Version.migrate()
        Institute.migrate()
    except:
        "Error migrating metadata"
    finally:
        "Done + good"
   
    return

def model_version(model):
    for x in model.query.all():
        x.version_latest = 1
        x.version_original = 1

@manager.command
def version_current():
    models = [Taxonomy(), Trait(), Publication(), AuthorContact(), Population(), StageType(), MatrixValue(),Matrix(), Fixed(), Study(), Institute()]
    
    for model in models:
        model_version(model)
@manager.command
def deploy():
    """Run deployment tasks."""
    from flask.ext.migrate import upgrade
    from app.models import User, Role, Permission
    # create user roles
    print "Inserting roles..."
    Role.insert_roles()
    print "Migrating meta data to tables..."
    migrate_meta()
    print "Initial migration of our current version of database..."
    csv_migrate()


if __name__ == '__main__':
    manager.run()
