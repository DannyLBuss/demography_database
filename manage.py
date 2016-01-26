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
                Matrix=Matrix, Interval=Interval, Bussy=Bussy, VectorAvailability=VectorAvailability, StageClassInfo=StageClassInfo, Small=Small, \
                TreatmentType=TreatmentType, Study=Study)
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
        submit(entry)
    return 

@manager.command
def delete_table_data():
    Taxonomy.query.delete()
    Matrix.query.delete()
    Population.query.delete()
    Study.query.delete()    
    Publication.query.delete()    
    PlantTrait.query.delete()
    Species.query.delete()
    db.session.commit()

    print "All data has been removed"
    return 

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
        data['geometries_lat_sec'], data['geometries_lon_sec'], data['geometries_lon_min'], data['geometries_lat_deg'], data['geometries_latitude_dec'], data['geometries_longitude_dec'], data['geometries_altitude'], data['ecoregion_id'], \
        data['country'], data['continent_id'], matrix)
    trait = PlantTrait(data['growth_type_id'], data['dicot_monoc_id'], data['angio_gymno_id'])
    pub = Publication(data['authors'], data['year'], data['DOI_ISBN'], data['additional_source_string'], tax, pop, trait, study)

    entry = Entry(pub, study, pop, tax, trait, matrix)
    
    return entry

def submit(entry):
    import json

    ''' Species '''
    species = Species.query.filter_by(species_accepted=entry.taxonomy.species_accepted).first()
    if species == None:
        species = Species(species_accepted=entry.taxonomy.species_accepted)
    db.session.add(species)
    db.session.commit()

    ''' Publication '''
    publication = Publication.query.filter_by(DOI_ISBN=entry.publication.DOI_ISBN).first()
    if publication == None:
        publication = Publication()
        publication.authors = entry.publication.authors
        publication.year = entry.publication.year
        publication.DOI_ISBN = entry.publication.DOI_ISBN
        publication.additional_source_string = entry.publication.additional_source_string
        db.session.add(publication)
        db.session.commit()

    ''' Plant Trait '''
    trait = PlantTrait.query.filter_by(species_id=species.id).first()
    if trait == None:
        trait = PlantTrait()
        growth_type = GrowthType.query.filter_by(type_name=entry.plant_trait.growth_type_id).first()
        if growth_type != None:
            trait.growth_type_id = growth_type.id
        dicot_monoc = DicotMonoc.query.filter_by(dicot_monoc_name=entry.plant_trait.dicot_monoc_id).first()
        if dicot_monoc != None:
            trait.dicot_monoc_id = dicot_monoc.id
        angio_gymno = AngioGymno.query.filter_by(angio_gymno_name=entry.plant_trait.angio_gymno_id).first()
        if angio_gymno != None:
            trait.angio_gymno_id = angio_gymno.id
        trait.species_id = species.id
        db.session.add(trait)
        db.session.commit()

    ''' Study '''
    study = Study.query.filter_by(publication_id=publication.id, study_start=entry.study.study_start, study_end=entry.study.study_end).first()
    if study == None:
        study = Study()
        if entry.study.study_duration != 'NA':
            study.study_duration = entry.study.study_duration

        if entry.study.study_start != 'NA':
            study.study_start = entry.study.study_start

        if entry.study.study_end != 'NA':
            study.study_end = entry.study.study_end

        study.publication_id = publication.id
        db.session.add(study)
        db.session.commit()

    ''' Population '''
    pop = Population.query.filter_by(geometries=json.dumps(entry.population.geometries), species_id=species.id, publication_id=publication.id).first()
    if pop == None:
        pop = Population()
        pop.species_author = entry.population.species_author
        pop.name = entry.population.name    
        ecoregion = Ecoregion.query.filter_by(ecoregion_code=entry.population.ecoregion_id).first()
        if ecoregion != None:
            pop.ecoregion_id = ecoregion.id
        pop.country = entry.population.country    
        continent = Continent.query.filter_by(continent_name=entry.population.continent_id).first()
        if continent != None:
            pop.continent_id = continent.id
        pop.geometries = json.dumps(entry.population.geometries)
        pop.species_id = species.id
        pop.publication_id = publication.id
        pop.study_id = study.id
        db.session.add(pop)
        db.session.commit()

    ''' Taxonomy '''
    tax = Taxonomy.query.filter_by(species_id=species.id).first()
    if tax == None:
        tax = Taxonomy()
        tax.species_author = entry.taxonomy.species_author
        tax.species_accepted = entry.taxonomy.species_accepted
        tax.authority = entry.taxonomy.authority
        tax.tpl_version = entry.taxonomy.tpl_version    
        tax_status = TaxonomicStatus.query.filter_by(status_name=entry.taxonomy.taxonomic_status_id).first()
        if tax_status != None:
            tax.taxonomic_status_id = tax_status.id
        tax.infraspecies_accepted = entry.taxonomy.infraspecies_accepted
        tax.species_epithet_accepted = entry.taxonomy.species_epithet_accepted
        tax.genus_accepted = entry.taxonomy.genus_accepted
        tax.genus = entry.taxonomy.genus
        tax.family = entry.taxonomy.family
        tax.tax_order = entry.taxonomy.tax_order
        tax.tax_class = entry.taxonomy.tax_class
        tax.phylum = entry.taxonomy.phylum
        tax.kingdom = entry.taxonomy.kingdom
        tax.species_id = species.id
        tax.publication_id = publication.id
        db.session.add(tax)
        db.session.commit()

    ''' Matrix '''
    matrix = Matrix()
    treatment_type = TreatmentType.query.filter_by(type_name=entry.matrix.treatment_id).first()
    if treatment_type == None:
        treatment_type = TreatmentType(type_name=entry.matrix.treatment_id)
        db.session.add(treatment_type)
        db.session.commit()
    matrix.treatment_id = treatment_type.id
    matrix.treatment_type_id = treatment_type.id
    matrix.matrix_split = coerce_boolean(entry.matrix.matrix_split)
    comp_id = MatrixComposition.query.filter_by(comp_name=entry.matrix.matrix_composition_id).first()
    if comp_id != None:
        matrix.matrix_composition_id = comp_id.id  

    if entry.matrix.survival_issue != 'NA':  
        matrix.survival_issue = float(entry.matrix.survival_issue)
    
    matrix.periodicity = entry.matrix.periodicity
    matrix.matrix_criteria_size = coerce_boolean(entry.matrix.matrix_criteria_size)
    matrix.matrix_criteria_ontogeny = coerce_boolean(entry.matrix.matrix_criteria_ontogeny)
    matrix.matrix_criteria_age = coerce_boolean(entry.matrix.matrix_criteria_age) 
    matrix.matrix_start = coerce_date(entry.matrix.matrix_start, 'start') #Coerced into date conidering NA
    matrix.matrix_end = coerce_date(entry.matrix.matrix_end , 'end') #Coerced into date considering NA
    start_id = Season.query.filter_by(season_name=entry.matrix.matrix_start_season_id).first()


    if entry.matrix.matrix_start_season_id != 'NA':
        print entry.matrix.matrix_start_season_id
        try:
            start_id = Season.query.filter_by(season_id=int(entry.matrix.matrix_start_season_id)).first()
        except ValueError:
            pass

    if start_id != None:
        matrix.matrix_start_season_id = start_id.id

    if entry.matrix.matrix_end_season_id != 'NA':
        print entry.matrix.matrix_end_season_id
        try:
            end_id = Season.query.filter_by(season_id=int(entry.matrix.matrix_end_season_id)).first()
        except ValueError:
            pass
    
    end_id = Season.query.filter_by(season_name=entry.matrix.matrix_end_season_id).first()
    if end_id != None:
        matrix.matrix_end_season_id = end_id.id
        
    matrix.matrix_fec = coerce_boolean(entry.matrix.matrix_fec)
    matrix.matrix_a_string = entry.matrix.matrix_a_string
    matrix.matrix_class_string = entry.matrix.matrix_class_string
    sex_id = StudiedSex.query.filter_by(sex_code=entry.matrix.studied_sex_id).first()
    if sex_id != None:
        matrix.studied_sex_id = sex_id.id
    cap_id = Captivity.query.filter_by(cap_code=entry.matrix.captivity_id).first()
    if cap_id != None:
        matrix.captivity_id = cap_id.id
    matrix.matrix_dimension = int(entry.matrix.matrix_dimension)
    matrix.observations = entry.matrix.observations
    matrix.population_id = pop.id
    matrix.study_id = study.id
    db.session.add(matrix)
    db.session.commit()

    return 

def submit_model(instance):
    db.session.add(instance)
    db.session.commit()


# This can be padded out for future stuff...
def coerce_boolean(string):
    true = ['Yes', 'Divided']
    false = ['No', 'Undivided']

    if string in true:
        return True
    elif string in false:
        return False

#Month doesn't seem to be i
def coerce_date(dict, typeof):
    import datetime

    date = dict

    month_start = date['matrix_'+typeof+'_month']
    year_start = date['matrix_'+typeof+'_year']

    if month_start and year_start == 'NA':
        date = None
    elif month_start == 'NA' and year_start != 'NA':
        date = 'M/' + year_start
    elif month_start != 'NA' and year_start == 'NA':
        date = month_start + '/YYYY'
    elif month_start != 'NA' and year_start != 'NA':
        date = month_start + '/' + year_start

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
    new_dict['name'] = dict['MatrixPopulation']
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
    new_dict['geometries_latitude_dec'] = dict['LatitudeDec']
    new_dict['geometries_longitude_dec'] = dict['LongitudeDec']
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
    # create user roles
    print "Inserting roles..."
    Role.insert_roles()
    print "Migrating meta data to tables..."
    migrate_meta()
    print "Initial migration of our current version of database..."
    csv_migrate()


if __name__ == '__main__':
    manager.run()
