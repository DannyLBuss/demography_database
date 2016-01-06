#!/usr/bin/env python
import os
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
    IUCNStatus, ESAStatus, TaxonomicStatus, GrowthType, GrowthFormRaunkiaer, ReproductiveRepetition, \
    DicotMonoc, AngioGymno, SourceType, Database, Purpose, MissingData, ContentEmail, Ecoregion, Continent, StageTypeClass, \
    TransitionType, MatrixComposition, Season, StudiedSex, Captivity, Species, Taxonomy, PlantTrait, \
    Publication, Study, AuthorContact, AdditionalSource, Population, Stage, StageType, Treatment, TreatmentType, \
    MatrixStage, MatrixValue, Matrix, Interval, Bussy, VectorAvailability, StageClassInfo, Small
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role,
                Permission=Permission, IUCNStatus=IUCNStatus, ESAStatus=ESAStatus, Species=Species, \
                TaxonomicStatus=TaxonomicStatus, Taxonomy=Taxonomy, GrowthType=GrowthType, GrowthFormRaunkiaer=GrowthFormRaunkiaer, \
                ReproductiveRepetition=ReproductiveRepetition, DicotMonoc=DicotMonoc, AngioGymno=AngioGymno, PlantTrait=PlantTrait, \
                Publication=Publication, SourceType=SourceType, Database=Database, Purpose=Purpose, MissingData=MissingData, \
                AuthorContact=AuthorContact, ContentEmail=ContentEmail, Population=Population, Ecoregion=Ecoregion, Continent=Continent, \
                StageType=StageType, StageTypeClass=StageTypeClass, TransitionType=TransitionType, MatrixValue=MatrixValue, \
                MatrixComposition=MatrixComposition, Season=Season, StudiedSex=StudiedSex, Captivity=Captivity, MatrixStage=MatrixStage,\
                Matrix=Matrix, Interval=Interval, Bussy=Bussy, VectorAvailability=VectorAvailability, StageClassInfo=StageClassInfo, Small=Small)
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

@manager.command
def csv_migrate():
    import csv

    input_file = csv.DictReader(open("app/compadre/compadreFlat3.csv"))

    all_deets = []   

    for i, row in enumerate(input_file):                     
        data = convert_all_headers(row)
        entry = add_to_classes(data)
        all_deets.append(entry)


    return submit(entry)

def add_to_classes(data):
    from app.conversion.models import Taxonomy, Publication, Population, PlantTrait, Matrix, Study, Entry
    
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
    trait = PlantTrait(data['growth_type_id'], data['dicot_monoc_id'], data['angio_gymno_id'])
    pub = Publication(data['authors'], data['year'], data['DOI_ISBN'], data['additional_source_string'], tax, pop, trait, study)

    entry = Entry(pub, study, pop, tax, trait, matrix)
    
    return entry

def submit(entry):
    matrix = Matrix()
    # matrix.treatment_id = Treatment.query.filter_by(name=entry.matrix.treatment_id).first() 
    matrix.matrix_split = coerce_boolean(entry.matrix.matrix_split) 
    # matrix.matrix_composition_id = MatrixComposition.query.filter_by(comp_name=entry.matrix.matrix_composition_id).first()
    matrix.survival_issue = float(entry.matrix.survival_issue)
    matrix.periodicity = entry.matrix.periodicity
    matrix.matrix_criteria_size = coerce_boolean(entry.matrix.matrix_criteria_size)
    matrix.matrix_criteria_ontogeny = coerce_boolean(entry.matrix.matrix_criteria_ontogeny)
    matrix.matrix_criteria_age = coerce_boolean(entry.matrix.matrix_criteria_age) 
    matrix.matrix_start = coerce_date(entry.matrix.matrix_start, 'start') #Coerced into date conidering NA
    matrix.matrix_end = coerce_date(entry.matrix.matrix_end , 'end') #Coerced into date considering NA
    # matrix.matrix_start_season_id = Season.query.filter_by(season_name=entry.matrix.matrix_start_season_id).first()
    # matrix.matrix_end_season_id = Season.query.filter_by(season_name=entry.matrix.matrix_end_season_id).first()
    matrix.matrix_fec = coerce_boolean(entry.matrix.matrix_fec)
    matrix.matrix_a_string = entry.matrix.matrix_a_string
    matrix.matrix_class_string = entry.matrix.matrix_class_string
    # matrix.studied_sex_id = StudiedSex.query.filter_by(sex_code=entry.matrix.studied_sex_id).first()
    # matrix.captivity_id = Captivity.query.filter_by(cap_code=entry.matrix.captivity_id).first()
    matrix.matrix_dimension = int(entry.matrix.matrix_dimension)
    matrix.observations = entry.matrix.observations


    publication = Publication()
    publication.authors = entry.publication.authors
    publication.year = entry.publication.year
    publication.DOI_ISBN = entry.publication.DOI_ISBN
    publication.additional_source_string = entry.publication.additional_source_string



    print entry.matrix.treatment_id

    return vars(matrix)

    # for key, value in vars(entry.matrix).items():
    #     print key, '|', value

# This can be padded out for future stuff...
def coerce_boolean(string):
    true = ['Yes', 'Divided']
    false = ['No', 'Undivided']

    if string in true:
        return True
    elif string in false:
        return False

def coerce_date(dict, type):
    import datetime
    date = dict

    datetime.date()

    month_start = date['matrix_'+type+'_month']
    year_start = date['matrix_'+type+'_year']

    if month_start and year_start == 'NA':
        date = None
    elif month_start == 'NA' and year_start != 'NA':
        date = datetime.datetime(datetime.date(int(year_start), 0, 0))
    elif month_start != 'NA' and year_start == 'NA':
        date = datetime.datetime(1, datetime.date(int(month_start), 0))

    return date

    #CREATE DATE



def convert_all_headers(dict):

    new_dict = {}

    new_dict['additional_source_string'] = dict['AdditionalSource']
    new_dict['matrix_end_season_id'] = dict['MatrixEndSeason']
    new_dict['growth_type_id'] = dict['GrowthType']
    new_dict['geometries_lat_sec'] = dict['LatSec']
    new_dict['study_duration'] = dict['StudyDuration']
    new_dict['matrix_values_c'] = dict['matrixC']
    new_dict['geometries_lat_we'] = dict['LonWE']
    new_dict['infraspecies_accepted'] = dict['InfraspecificAccepted']
    new_dict['matrix_values_a'] = dict['matrixA']
    new_dict['matrix_a_string'] = dict['matrixA']
    new_dict['matrix_start_year'] = dict['MatrixStartYear']
    new_dict['kingdom'] = dict['Kingdom']
    new_dict['DOI_ISBN'] = dict['DOI.ISBN']
    new_dict['genus'] = dict['Genus']
    new_dict['species_epithet_accepted'] = dict['SpeciesEpithetAccepted']
    new_dict['name'] = dict['Journal']
    new_dict['geometries_lat_ns'] = dict['LatNS']
    new_dict['number_populations'] = dict['NumberPopulations']
    new_dict['matrix_fec'] = dict['MatrixFec']
    new_dict['matrix_criteria_size'] = dict['CriteriaSize']
    new_dict['geometries_lon_min'] = dict['LonMin']
    new_dict['matrix_start_month'] = dict['MatrixStartMonth']
    new_dict['authors'] = dict['Authors']
    new_dict['geometries_lon_sec'] = dict['LonSec']
    new_dict['taxonomic_status_id'] = dict['TaxonomicStatus']
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

@manager.command
def migrate_meta():
    from app.models import User, Role, Permission, \
    IUCNStatus, ESAStatus, TaxonomicStatus, GrowthType, GrowthFormRaunkiaer, ReproductiveRepetition, \
    DicotMonoc, AngioGymno, SourceType, Database, Purpose, MissingData, ContentEmail, Ecoregion, Continent, StageTypeClass, \
    TransitionType, MatrixComposition, Season, StudiedSex, Captivity, Species, Taxonomy, PlantTrait, \
    Publication, Study, AuthorContact, AdditionalSource, Population, Stage, StageType, Treatment, TreatmentType, \
    MatrixStage, MatrixValue, Matrix, Interval, Bussy, VectorAvailability, StageClassInfo, Small

    print "Migrating Meta Tables..."
    try:
        Species.migrate()
        Taxonomy.migrate()
        PlantTrait.migrate()
        Publication.migrate()
        AuthorContact.migrate()
        Population.migrate()
        StageType.migrate()
        MatrixValue.migrate()
        Matrix.migrate()
        Bussy.migrate()
    except:
        "Error migrating metadata"
    finally:
        "Done + good"
   
    return


@manager.command
def deploy():
    """Run deployment tasks."""
    from flask.ext.migrate import upgrade
    from app.models import User, Role, Permission
    # migrate database to latest revision
    # upgrade()

    # create user roles
    Role.insert_roles()


if __name__ == '__main__':
    manager.run()
