#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
    IUCNStatus, ESAStatus, GrowthType, GrowthFormRaunkiaer, ReproductiveRepetition, \
    DicotMonoc, AngioGymno, DavesGrowthType, SourceType, Database, Purpose, MissingData, ContentEmail, Ecoregion, Continent, InvasiveStatusStudy, InvasiveStatusElsewhere, StageTypeClass, \
    TransitionType, MatrixComposition, Season, StudiedSex, Captivity, Species, Taxonomy, Trait, \
    Publication, Study, AuthorContact, AdditionalSource, Population, Stage, StageType, Treatment, TreatmentType, \
    MatrixStage, MatrixValue, Matrix, Interval, Fixed, Small, CensusTiming, Status, PurposeEndangered, PurposeWeed
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role,
                Permission=Permission, IUCNStatus=IUCNStatus, ESAStatus=ESAStatus, Species=Species, \
                Taxonomy=Taxonomy, GrowthType=GrowthType, GrowthFormRaunkiaer=GrowthFormRaunkiaer, \
                ReproductiveRepetition=ReproductiveRepetition, DicotMonoc=DicotMonoc, AngioGymno=AngioGymno, DavesGrowthType=DavesGrowthType, Trait=Trait, \
                Publication=Publication, SourceType=SourceType, Database=Database, Purpose=Purpose, MissingData=MissingData, \
                AuthorContact=AuthorContact, ContentEmail=ContentEmail, Population=Population, Ecoregion=Ecoregion, Continent=Continent, \
                StageType=StageType, StageTypeClass=StageTypeClass, TransitionType=TransitionType, MatrixValue=MatrixValue, \
                MatrixComposition=MatrixComposition, Season=Season, StudiedSex=StudiedSex, Captivity=Captivity, MatrixStage=MatrixStage,\
                Matrix=Matrix, Interval=Interval, Fixed=Fixed, Small=Small, CensusTiming=CensusTiming, \
                TreatmentType=TreatmentType, Study=Study, Status=Status, InvasiveStatusStudy=InvasiveStatusStudy, InvasiveStatusElsewhere=InvasiveStatusElsewhere, \
                PurposeEndangered=PurposeEndangered, PurposeWeed=PurposeWeed)
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
        db.session.commit()
        print "All data has been removed"
    elif response == "n":
        print "Table data not deleted"
        pass
    else:
        print("Valid response required (y/n)")
    return    

def add_to_classes(data):
    from app.conversion.models import Taxonomy, Publication, Population, Trait, Matrix, Study, Entry
    
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
    
    return entry

def submit(entry):
    import json, re

    ''' Species '''
    species = Species.query.filter_by(species_accepted=entry.taxonomy.species_accepted).first()
    if species == None:
        species = Species(species_accepted=entry.taxonomy.species_accepted)
    db.session.add(species)
    db.session.commit()

    ''' Publication '''
    if entry.publication.DOI_ISBN == "None" or entry.publication.DOI_ISBN == "NA":
        publication = Publication.query.filter_by(authors=entry.publication.authors).filter_by(year=entry.publication.year).filter_by(pub_title=entry.publication.pub_name).first()
    else: 
        publication = Publication.query.filter_by(DOI_ISBN=entry.publication.DOI_ISBN).first()
    if publication == None:
        publication = Publication()
        publication.authors = entry.publication.authors
        publication.year = entry.publication.year
        publication.DOI_ISBN = entry.publication.DOI_ISBN
        publication.additional_source_string = entry.publication.additional_source_string
        publication.pub_title = entry.publication.pub_name
        db.session.add(publication)
        db.session.commit()


    ''' Plant Trait '''
    trait = Trait.query.filter_by(species_id=species.id).first()
    if trait == None:
        trait = Trait()
        growth_type = GrowthType.query.filter_by(type_name=entry.trait.growth_type_id).first()
        if growth_type != None:
            trait.growth_type_id = growth_type.id
        dicot_monoc = DicotMonoc.query.filter_by(dicot_monoc_name=entry.trait.dicot_monoc_id).first()
        if dicot_monoc != None:
            trait.dicot_monoc_id = dicot_monoc.id
        angio_gymno = AngioGymno.query.filter_by(angio_gymno_name=entry.trait.angio_gymno_id).first()
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
    pop = Population.query.filter_by(name=json.dumps(entry.population.name), species_id=species.id, publication_id=publication.id).first()
    if pop == None:
        pop = Population()
        pop.species_author = entry.population.species_author
        pop.name = entry.population.name.encode('utf-8')   
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
        try:
            start_id = Season.query.filter_by(season_id=int(entry.matrix.matrix_start_season_id)).first()
        except ValueError:
            pass

    if start_id != None:
        matrix.matrix_start_season_id = start_id.id

    if entry.matrix.matrix_end_season_id != 'NA':
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
    matrix.create_uid()

    return 

def submit_model(instance):
    db.session.add(instance)
    # db.session.commit()


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

@manager.command
def duplicates():
    import csv

    input_file = csv.DictReader(open("app/compadre/compadreFlat3.csv", "rU"))

    all_data = []
    all_ids = []   

    for i, row in enumerate(input_file):                    
        data = convert_all_headers(row)
        all_ids.append(create_id_string(data))
        all_data.append(data)

    
    
    spot_vals = [67, 142, 678, 1389, 4454, 5172, 295]

    # Check each against all others
    f = open("dupes_96.csv","a")
    for n, item in enumerate(all_data):
        if n in spot_vals:
            species_accepted = item['species_accepted']
            authors = item['authors'][:15]
            journal = item['journal'].replace(",", "")
            population = item['name'].replace(",", "")
            matrix_composite = item['matrix_composition_id'].replace(",", "") 
            matrix_treatment = item['treatment_id'].replace(",", "") 
            matrix_start_year = item['matrix_start_year'].replace(",", "") 
            observation = item['observations'].replace(",", "") 
            matrix_a_string = item['matrix_a_string'].replace(",", "")        
            uid = create_id_string(item)
            f.write('Index, Species Accepted, Journal, Authors (capped to 15), Population Name, Matrix Composite, Matrix Treatment, Matrix Start Year, Observation, Matrix A String, UID, Ratio\n')
            f.write('{},{},{},{},{},{},{},{},{},{},{},{}\n'.format(n, species_accepted, journal, authors, population, matrix_composite, matrix_treatment, matrix_start_year, observation, matrix_a_string, uid, 1))
            temp_ratio = []
            for i, detail in enumerate(all_data):
                record_species = detail['species_accepted']
                record_journal = detail['journal'].replace(",", "")
                record_authors = detail['authors'].replace(",", "")[:15] 
                record_population = detail['name'].replace(",", "")
                record_matrix_composite = detail['matrix_composition_id'].replace(",", "") 
                record_matrix_treatment = detail['treatment_id'].replace(",", "") 
                record_matrix_start_year = detail['matrix_start_year'].replace(",", "") 
                record_observation = detail['observations'].replace(",", "") 
                record_matrix_a_string = detail['matrix_a_string'].replace(",", "")
                record_uid = create_id_string(detail)
                record_uid = record_uid.replace(",", "")
                ratio = similar(uid, record_uid)

                if ratio >= 0.96:
                    if i != n:
                        print '{},{},{},{},{},{},{},{},{},{},{},{}\n'.format(i, record_species, record_journal, record_authors, record_population, record_matrix_composite, record_matrix_treatment, record_matrix_start_year, record_observation, record_matrix_a_string, record_uid, ratio)
                        f.write('{},{},{},{},{},{},{},{},{},{},{},{}\n'.format(i, record_species, record_journal, record_authors, record_population, record_matrix_composite, record_matrix_treatment, record_matrix_start_year, record_observation, record_matrix_a_string, record_uid, ratio))
                        temp_ratio.append(ratio)
                # if species_accepted == record_species:
                #     f.write('{},{},{},{},{},{},{}\n'.format(i, record_species, record_journal, record_authors, record_population, record_uid, ratio))
                #     temp_ratio.append(ratio)
                # if authors == record_authors:
                #     f.write('{},{},{},{},{},{},{}\n'.format(i, record_species, record_journal, record_authors, record_population, record_uid, ratio))
                #     temp_ratio.append(ratio)
            
            if temp_ratio:
                mini = min(temp_ratio)
                maxi = max(temp_ratio)
                average = sum(temp_ratio) / float(len(temp_ratio))
                length = len(temp_ratio)
                print 'Count, Minimum, Maximum, Average\n{},{},{},{}\n\n'.format(length, mini, maxi, average)
                f.write('Count, Minimum, Maximum, Average\n{},{},{},{}\n'.format(length, mini, maxi, average))
            else:
                print 'Count, Minimum, Maximum, Average\n{},{},{},{}\n\n'.format(0, 0, 0, 0)
                f.write('Count, Minimum, Maximum, Average\n{},{},{},{}\n'.format(0, 0, 0, 0))

    f.close()

def convert_all_headers(dict):
    import re

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
    new_dict['pub_name'] = dict['Journal']
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
    IUCNStatus, ESAStatus, GrowthType, GrowthFormRaunkiaer, ReproductiveRepetition, \
    DicotMonoc, AngioGymno, DavesGrowthType, SourceType, Database, Purpose, MissingData, ContentEmail, Ecoregion, Continent, InvasiveStatusStudy, InvasiveStatusElsewhere, StageTypeClass, \
    TransitionType, MatrixComposition, Season, StudiedSex, Captivity, Species, Taxonomy, Trait, \
    Publication, Study, AuthorContact, AdditionalSource, Population, Stage, StageType, Treatment, TreatmentType, \
    MatrixStage, MatrixValue, Matrix, Interval, Fixed, Small, CensusTiming, PurposeEndangered, PurposeWeed

    print "Migrating Meta Tables..."
    try:
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
