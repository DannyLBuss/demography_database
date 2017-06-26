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
    IUCNStatus,  OrganismType, GrowthFormRaunkiaer, ReproductiveRepetition, \
    DicotMonoc, AngioGymno, SpandExGrowthType, SourceType, Database, Purpose, MissingData, ContentEmail, Ecoregion, Continent, InvasiveStatusStudy, InvasiveStatusElsewhere, StageTypeClass, \
    TransitionType, MatrixComposition, StartSeason, StudiedSex, Captivity, Species, Taxonomy, Trait, \
    Publication, AuthorContact, AdditionalSource, Population, Stage, StageType, Treatment, \
    MatrixStage, MatrixValue, Matrix, Interval, Fixed, Small, CensusTiming, Status, PurposeEndangered, PurposeWeed, Version, Institute, EndSeason, ChangeLogger, PublicationsProtocol, DigitizationProtocol, Protocol, CommonTerm
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

from app.matrix_functions import as_array, calc_lambda, calc_surv_issue, is_matrix_irreducible, is_matrix_primitive, is_matrix_ergodic

from flask import Flask
from flask.ext.alchemydumps import AlchemyDumps, AlchemyDumpsCommand
from flask.ext.sqlalchemy import SQLAlchemy

import random
def gen_hex_code():
    r = lambda: random.randint(0,255)
    return('#%02X%02X%02X' % (r(),r(),r()))

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role,
                Permission=Permission, IUCNStatus=IUCNStatus, Species=Species, \
                Taxonomy=Taxonomy, OrganismType=OrganismType, GrowthFormRaunkiaer=GrowthFormRaunkiaer, \
                ReproductiveRepetition=ReproductiveRepetition, DicotMonoc=DicotMonoc, AngioGymno=AngioGymno, SpandExGrowthType=SpandExGrowthType, Trait=Trait, \
                Publication=Publication, SourceType=SourceType, Database=Database, Purpose=Purpose, MissingData=MissingData, \
                AuthorContact=AuthorContact, ContentEmail=ContentEmail, Population=Population, Ecoregion=Ecoregion, Continent=Continent, \
                StageType=StageType, StageTypeClass=StageTypeClass, TransitionType=TransitionType, MatrixValue=MatrixValue, \
                MatrixComposition=MatrixComposition, StartSeason=StartSeason, StudiedSex=StudiedSex, Captivity=Captivity, MatrixStage=MatrixStage,\
                Matrix=Matrix, Interval=Interval, Fixed=Fixed, Small=Small, CensusTiming=CensusTiming, Status=Status, InvasiveStatusStudy=InvasiveStatusStudy, InvasiveStatusElsewhere=InvasiveStatusElsewhere, \
                PurposeEndangered=PurposeEndangered, PurposeWeed=PurposeWeed, Version=Version, Institute=Institute, EndSeason=EndSeason, ChangeLogger = ChangeLogger, PublicationsProtocol = PublicationsProtocol, \
                DigitizationProtocol = DigitizationProtocol, Protocol=Protocol, CommonTerm=CommonTerm)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


manager.add_command('alchemydumps', AlchemyDumpsCommand)

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
def delete_table_data():
    response = raw_input("Are you sure you want to delete all data? (y/n): ")

    if response == "y":
        Version.query.delete()
        Taxonomy.query.delete()
        Matrix.query.delete()
        Population.query.delete() 
        Publication.query.delete()    
        Trait.query.delete()
        Species.query.delete()
        Version.query.delete()
        Protocol.query.delete()
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
    true = ['Yes', 'Divided','TRUE','T']
    false = ['No', 'Undivided','FALSE','F','Indivisible']

    if string in true:
        return True
    elif string in false:
        return False
    elif string == "NA":
        print "it's NA mate"
    else:
        print "you've got an error mate"
        print string


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
    "name" : dict["name"], # what sort of name is this?
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
    journal = publication.journal_name if publication else None
    year_pub = publication.year if publication else None

    try:
        authors = publication.authors[:15].encode('utf-8')
    except:
        authors = ''

    try:
        pop_name = population.population_name.encode('utf-8')[:15] if population else None
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

def data_clean(data):
    incomplete = True if 'NDY' in data.values() else False
    kwargs = {key: val for key, val in data.items() if val != 'NDY'}
    amber = Status.query.filter_by(status_name="Amber").first()
    pending = Status.query.filter_by(status_name="Pending").first()
    #kwargs['version_ok'] = 0 if incomplete else 1
    #kwargs['version_original'] = 1
    #kwargs['version_latest'] = 1
    return {'kwargs' : kwargs, 'status' : amber if incomplete else pending}

def version_data(cleaned):
    version =  {'checked' : False, 
    'checked_count' : 0, 
    'statuses' : cleaned['status']#,
    #'version_number' : 1,
    #'user' : User.query.filter_by(username='admin').first(), 
    #'database' : Database.query.filter_by(database_name='COMPADRE 4').first()
               }
    return version

@manager.command
def submit_new(data):
    import datetime

    # When checking for null data later, these need to be excluded, as they will always have a value
    ignore_keys = ['version_ok', 'version_latest', 'version_original']

    ''' DigitizationProtocol ''' 

#    digitization_protocol = DigitizationProtocol.query.filter_by(field_name=data["digitization_protocol"]).first()

 #   if digitization_protocol == None:
 #           ac_dict = {'protocol_id' : protocol.id, 
 #           'field_name' : data['field_name'],
 #           'name_in_csv' : data["name_in_csv"],
 #           'database_model' : data["database_model"],
 #           'field_description' : data["field_description"],
 #           'field_short_description' : data["field_short_description"]
 #           }

 #           ac_cleaned = data_clean(ac_dict)
 #           digitization_protocol = Protocol(**ac_cleaned["kwargs"])
            
 #           db.session.add(digitization_protocol)
 #           db.session.commit()

    ''' Publication '''   
    
    publications_protocol = PublicationsProtocol.query.filter_by(protocol_number=data["publications_protocol_id"]).first()
    
    if data["publication_DOI_ISBN"] == None:
        publication = Publication.query.filter_by(authors=data["publication_authors"]).filter_by(year=data["publication_year"]).filter_by(journal_name=data["publication_journal_name"]).filter_by(additional_source_string=data["publication_additional_source_string"]).filter_by(study_notes= data["publication_study_notes"]).first()
    else: 
        publication = Publication.query.filter_by(DOI_ISBN=data["publication_DOI_ISBN"]).first()    
    
    if publication == None:
        purposes = {"Comparative Demography" : data["publication_purpose_comparative_demography"],
        "Spatial Demography" : data["publication_purpose_spatial_demography"], 
        "Abiotic Impacts" : data["publication_purpose_abiotic"],
        "PVA" : data["publication_purpose_pva"],
        "Species Dynamics Description" : data["publication_purpose_species_dynamics_description"],
        "Interspecific Interactions" : data["publication_purpose_interspecific_interactions"],
        "Management Evaluation" : data["publication_purpose_management_evaluation"],
        "Methodological Advancement" : data["publication_purpose_methodological_advancement"]
        }

        queryset = [Purpose.query.filter(Purpose.purpose_name == key).first() for key, val in purposes.items() if val == '1']
    
        if data['publication_missing_data'] != 'NDY' and data['publication_missing_data']:
            missing_data_unicode = data['publication_missing_data'].replace(" ", "").split(';')
            missing_data = [MissingData.query.filter_by(missing_code=key).first() for key in missing_data_unicode if MissingData.query.filter_by(missing_code=key).first()]
        else:
            missing_data = 'NDY'

        possible_user = User.query.filter_by(name = data["publication_student"]).first()
        na_user = User.query.filter_by(name = "N/A").first()
        if possible_user == None:
            possible_user = na_user

        pub_dict = {'authors': data["publication_authors"],
        'year' : data["publication_year"],
        'publications_protocol' : publications_protocol, 
        'DOI_ISBN' : data["publication_DOI_ISBN"],
        'additional_source_string' : data["publication_additional_source_string"],
        'journal_name' : data["publication_journal_name"],
        'date_digitised' : datetime.datetime.strptime(data['publication_date_digitization'], "%d/%m/%Y").strftime("%Y-%m-%d") if data['publication_date_digitization'] else None,
        'purposes' : queryset,
        'entered_by_id' :  possible_user.id if possible_user else None,
        'checked_by_id' :  na_user.id if na_user else None,
        'study_notes' : data["publication_study_notes"]
        }

        pub_cleaned = data_clean(pub_dict)

        # if not all(value == None for key, value in pub_cleaned["kwargs"].items() if key not in ignore_keys) and study_present:
        publication = Publication(**pub_cleaned["kwargs"])
        db.session.add(publication)
        db.session.commit()

        publication.missing_data = missing_data if type(missing_data) == list else []

        db.session.add(publication)
        db.session.commit()

        ''' Publication Version '''
        version = version_data(pub_cleaned)
        publication_version = Version(**version)
        publication_version.publication = publication
        publication.colour = gen_hex_code()
        db.session.add(publication_version) 
        db.session.commit()  
        publication_version.original_version_id = publication_version.id
        db.session.add(publication_version)
        db.session.commit()
    
        ''' Author contact '''
        
        author_contacts = AuthorContact.query.filter_by(corresponding_author = data["publication_corresponding_author"]).filter_by(corresponding_author_email = data["publication_corresponding_email"]).first()
        
        
        
        if author_contacts == None:
            ac_dict = {'publication_id' : publication.id, 
            'date_contacted' : datetime.datetime.strptime(data['date_author_contacted'], "%d/%m/%Y").strftime("%Y-%m-%d") if data['date_author_contacted'] else None,
            'date_contacted_again' : datetime.datetime.strptime(data['date_author_contacted_again'], "%d/%m/%Y").strftime("%Y-%m-%d") if data['date_author_contacted_again'] else None,
            'extra_content_email' : data["correspondence_email_content"],
            'author_reply' : data["correspondence_author_reply"],
            'corresponding_author' : data["publication_corresponding_author"],
            'corresponding_author_email' : data["publication_corresponding_email"],
            'correspondence_email_content' : data["correspondence_email_content"],
            'extra_content_email' : data["extra_content_email"],
            'contacting_user_id' : possible_user.id if possible_user else None
            }

            ac_cleaned = data_clean(ac_dict)
            author_contact = AuthorContact(**ac_cleaned["kwargs"])
            
            db.session.add(author_contact)
            db.session.commit()

            ''' Author Contact Version '''
            version = version_data(ac_cleaned)
            author_contact_version = Version(**version)
            author_contact_version.author_contact = author_contact
            db.session.add(author_contact_version) 
            db.session.commit()  
            author_contact_version.original_version_id = author_contact_version.id
            db.session.add(author_contact_version)
            db.session.commit()

    ''' Species '''
    species = Species.query.filter_by(species_accepted=data["species_accepted"]).first()
    iucn = IUCNStatus.query.filter_by(status_code=data["species_iucn_status_id"]).first()

    if species == None:
        species_dict = {'gbif_taxon_key': data["species_gbif_taxon_key"], 
        'species_iucn_taxonid': data["species_iucn_taxonid"], 
        'species_accepted' : data["species_accepted"], 
        'species_common' :  data["species_common"], 
        'iucn_status_id' : iucn.id if iucn else None, 
        'image_path' : data["image_path"], 
        'image_path2' : data["image_path2"]}
        
        species_cleaned = data_clean(species_dict)
        species = Species(**species_cleaned["kwargs"])

        db.session.add(species)
        db.session.commit()

        ''' Species Version '''
        version = version_data(species_cleaned)
        species_version = Version(**version)
        species_version.species = species
        db.session.add(species_version) 
        db.session.commit()  
        species_version.original_version_id = species_version.id
        db.session.add(species_version)
        db.session.commit()

    ''' Trait '''
    spand_ex_growth_type = SpandExGrowthType.query.filter_by(type_name=data["trait_spand_ex_growth_type_id"]).first()
    dicot_monoc = DicotMonoc.query.filter_by(dicot_monoc_name=data["trait_dicot_monoc_id"]).first()
    growth_form_raunkiaer = GrowthFormRaunkiaer.query.filter_by(form_name=data["trait_growth_form_raunkiaer_id"]).first()
    organism_type = OrganismType.query.filter_by(type_name=data["trait_organism_type_id"]).first()
    angio_gymno = AngioGymno.query.filter_by(angio_gymno_name=data["trait_angio_gymno_id"]).first()

    trait = Trait.query.filter_by(species_id=species.id).first()

    if trait == None:
        trait_dict = {'species_id': species.id, 
        'organism_type': organism_type,
        'dicot_monoc': dicot_monoc,
        'angio_gymno': angio_gymno,
        'species_seedbank' : coerce_boolean(data["species_seedbank"]),
        'species_gisd_status' : coerce_boolean(data["species_gisd_status"]),
        'species_clonality' : coerce_boolean(data["species_clonality"]),  
        'spand_ex_growth_type_id' : spand_ex_growth_type.id if spand_ex_growth_type else None,
        'growth_form_raunkiaer_id' : growth_form_raunkiaer.id if growth_form_raunkiaer else None}

        trait_cleaned = data_clean(trait_dict)
        trait = Trait(**trait_cleaned["kwargs"])

        db.session.add(trait)
        db.session.commit()

        ''' Trait Version '''
        version = version_data(trait_cleaned)
        trait_version = Version(**version)
        trait_version.trait = trait
        db.session.add(trait_version) 
        db.session.commit()  
        trait_version.original_version_id = trait_version.id
        db.session.add(trait_version)
        db.session.commit()

    ''' Taxonomy '''
    tax = Taxonomy.query.filter_by(species_id=species.id).first()
    if tax == None:
        tax_dict = {'authority' : None, 
        'tpl_version' : None, 
        'infraspecies_accepted' : None,
        'species_epithet_accepted' : None, 
        'genus_accepted' : data["taxonomy_genus_accepted"],
        'genus' : data["taxonomy_genus"], 
        'family' : data["taxonomy_family"], 
        'tax_order' : data["taxonomy_order"], 
        'tax_class' : data["taxonomy_class"],
        'phylum' : data["taxonomy_phylum"], 
        'kingdom' : data["taxonomy_kingdom"], 
        'col_check_date' : datetime.datetime.strptime(data["taxonomy_col_check_date"], "%d/%m/%Y").strftime("%Y-%m-%d") if data['taxonomy_col_check_date'] else None,
        'col_check_ok' : coerce_boolean(data["taxonomy_col_check_ok"])}

        tax_cleaned = data_clean(tax_dict)

        # if not all(value == None for key, value in tax_cleaned["kwargs"].items() if key not in ignore_keys):
        tax = Taxonomy(**tax_cleaned["kwargs"])
        db.session.add(tax)
        db.session.commit()
        tax.species = species
        db.session.add(tax)
        db.session.commit()

        ''' Taxonomy Version '''
        version = version_data(tax_cleaned)
        taxonomy_version = Version(**version)
        taxonomy_version.version_number = 1
        taxonomy_version.taxonomy = tax    
        db.session.add(taxonomy_version) 
        db.session.commit()
        taxonomy_version.original_version_id = taxonomy_version.id
        db.session.add(taxonomy_version)
        db.session.commit()

    ''' Study '''
    # What if all none? Will they be grouped together?
#    study = Study.query.filter_by(publication_id=publication.id, study_start=data["study_start"], study_end=data["study_end"]).first()
#    if study == None:
#        purpose_endangered = PurposeEndangered.query.filter_by(purpose_name=data["study_purpose_endangered_id"]).first() if data["study_purpose_endangered_id"] else data["study_purpose_endangered_id"]
#
#        purpose_weed = PurposeWeed.query.filter_by(purpose_name="study_purpose_weed_id").first() if data["study_purpose_weed_id"] else data["study_purpose_weed_id"]
#        database_source = Institute.query.filter_by(institution_name=data["study_database_source"]).first()# if data["study_purpose_weed_id"] else data["study_purpose_endangered_id"]
#        
#        study_dict = {'study_duration' : data["study_duration"],
#        'study_start' : data["study_start"], 
#        'study_end' :  data["study_end"], 
#        'number_populations' : data["study_number_populations"], 
#        'purpose_endangered_id' : purpose_endangered.id if purpose_endangered else None, 
#        'purpose_weed_id' : purpose_weed.id if purpose_weed else None,
#        'database_source' : database_source}
#
#        study_cleaned = data_clean(study_dict)
#
#        # if not all(value == None for key, value in study_cleaned["kwargs"].items() if key not in ignore_keys) and population_present:
#        study = Study(**study_cleaned["kwargs"])
#        db.session.add(study)
#        db.session.commit()
#
#        study.publication_id = publication.id
#        study.species_id = species.id
#        db.session.add(study)
#        db.session.commit()
#
#
#        ''' Study Version '''
#        version = version_data(study_cleaned)
#        study_version = Version(**version)
#        study_version.version_number = 1
#        study_version.study = study    
#        db.session.add(study_version) 
#        db.session.commit()
#        study_version.original_version_id = study_version.id
#        db.session.add(study_version)
#        db.session.commit()

    ''' Protocol '''

#    digitization_protocol = DigitizationProtocol.query.filter_by(field_name=data["digitization_protocol_id"]).first()
#    commonterm = CommonTerm.query.filter_by(common_value_name=data["commonterm_id"]).first()

#    protocol = Protocol.query.filter_by(protocol_id=protocol.id).first()

#    if protocol == None:
#        protocol_dict = {'protocol_id' : protocol.id,
#        'digitization_protocol_id' : digitization_protocol.id if digitization_protocol else None,
#        'commonterm_id' : commonterm.id if commonterm else None}

#        protocol_cleaned = data_clean(protocol_dict)
#        protocol = Protocol(**protocol_cleaned["kwargs"])

#        db.session.add(protocol)
#        db.session.commit()
    
    ''' Population '''
    '''            '''
    invasive_status_study = InvasiveStatusStudy.query.filter_by(status_name=data["population_invasive_status_study_id"]).first()
    invasive_status_elsewhere = InvasiveStatusStudy.query.filter_by(status_name=data["population_invasive_status_elsewhere_id"]).first()
    ecoregion = Ecoregion.query.filter_by(ecoregion_code=data["population_ecoregion_id"]).first()
    continent = Continent.query.filter_by(continent_name=data["population_continent_id"]).first()
    ###Danny trying add database meta-table in correct location
    database = Database.query.filter_by(database_master_version=data["population_database_id"]).first()
    
    purpose_endangered = PurposeEndangered.query.filter_by(purpose_name=data["study_purpose_endangered_id"]).first() if data["study_purpose_endangered_id"] else data["study_purpose_endangered_id"]

    purpose_weed = PurposeWeed.query.filter_by(purpose_name="study_purpose_weed_id").first() if data["study_purpose_weed_id"] else data["study_purpose_weed_id"]
    database_source = Institute.query.filter_by(institution_name=data["study_database_source_id"]).first()

    
    pop = Population.query.filter_by(population_name=data["population_name"], publication_id=publication.id, species_id=species.id).first()

    if pop == None:
        pop_dict = {'population_name' : data["population_name"],       
        'latitude' : data["population_latitude"],
        'lat_ns' : data["lat_ns"], 
        'lat_deg' : data["lat_deg"], 
        'lat_min' : data["lat_min"],  
        'lat_sec' : data["lat_sec"], 

        'longitude' : data["population_longitude"],
        'lon_ew' : data["lon_ew"],
        'lon_deg' : data["lon_deg"],
        'lon_min' : data["lon_min"], 
        'lon_sec' : data["lon_sec"],           
     
        'altitude' : data["population_altitude"],
        #'pop_size' : data["population_pop_size"],
        'country' : data["population_country"],
        'invasive_status_study_id' : invasive_status_study.id if invasive_status_study else None,
        'invasive_status_elsewhere_id' : invasive_status_elsewhere.id if invasive_status_elsewhere else None,
        'ecoregion' : ecoregion, 
        'continent' : continent,
        'database' : database,
        'within_site_replication' : data['population_within_site_replication'],
                    
        'study_duration' : data["study_duration"],
        'study_start' : data["study_start"], 
        'study_end' :  data["study_end"], 
        'number_populations' : data["study_number_populations"], 
        'purpose_endangered_id' : purpose_endangered.id if purpose_endangered else None, 
        'purpose_weed_id' : purpose_weed.id if purpose_weed else None,
        'database_source' : database_source
        }

        pop_cleaned = data_clean(pop_dict)

        # if not all(value == None for key, value in pop_cleaned["kwargs"].items() if key not in ignore_keys) and matrix_present:
        pop = Population(**pop_cleaned["kwargs"])

        db.session.add(pop)
        db.session.commit()

        pop.species_author = data["species_author"]
        pop.publication_id = publication.id
        pop.species_id = species.id

        db.session.add(pop)
        db.session.commit()

        ''' Population Version '''
        version = version_data(pop_cleaned)
        population_version = Version(**version)
        population_version.version_number = 1
        population_version.population = pop    
        db.session.add(population_version) 
        db.session.commit()
        population_version.original_version_id = population_version.id
        db.session.add(population_version)
        db.session.commit()


    ''' Matrix '''
    treatment_string = data["matrix_treatment_id"]    

    if treatment_string == 'NDY':
        treatment = 'NDY'
    elif treatment_string == None:
        treatment = None
    else:
        treatment = Treatment.query.filter_by(treatment_name=data["matrix_treatment_id"]).first() if Treatment.query.filter_by(treatment_name=data["matrix_treatment_id"]).first() else Treatment(treatment_name=data["matrix_treatment_id"])
        db.session.add(treatment)
        db.session.commit()

    matrix_dict = {'treatment' : treatment,
    'matrix_split' : coerce_boolean(data["matrix_split"]),
    'matrix_composition' : MatrixComposition.query.filter_by(comp_name=data["matrix_composition_id"]).first(),
    'matrix_criteria_size' : data["matrix_criteria_size"],
    'matrix_criteria_ontogeny' : coerce_boolean(data["matrix_criteria_ontogeny"]),
    'matrix_criteria_age' : coerce_boolean(data["matrix_criteria_age"]),
    'matrix_start_month' : data["matrix_start_month"],
    'matrix_end_month' : data["matrix_end_month"],
    'matrix_start_year' : data["matrix_start_year"],
    'matrix_end_year' : data["matrix_end_year"],
    'studied_sex' : StudiedSex.query.filter_by(sex_code=data["matrix_studied_sex_id"]).first(),
    'start_season' : StartSeason.query.filter_by(season_id=data["matrix_start_season_id"]).first() if data["matrix_start_season_id"] else None,
    'end_season' : EndSeason.query.filter_by(season_id=data["matrix_end_season_id"]).first() if data["matrix_end_season_id"] else None,
    'matrix_fec' : coerce_boolean(data["matrix_fec"]),
    'matrix_a_string' : data["matrix_a_string"],
    'matrix_f_string' : data["matrix_f_string"],
    'matrix_u_string' : data["matrix_u_string"],
    'matrix_c_string' : data["matrix_c_string"],
    'non_independence' : data["matrix_non_independence"],
    'matrix_dimension' : data["matrix_dimension"],
    'non_independence_author' : data["matrix_non_independence_author"],
    'matrix_complete' : coerce_boolean(data["matrix_complete"]),
    'class_number' : data["matrix_class_number"],
    'observations' : data["matrix_observations"],
    'captivities' : Captivity.query.filter_by(cap_code=data["matrix_captivity_id"]).first(),
    'class_author' : data["matrix_class_author"],
    'class_organized' : data["matrix_class_organized"],
    'matrix_difficulty' : data["matrix_difficulty"],
    'seasonal' : coerce_boolean(data["matrix_seasonal"]),
    'survival_issue' : calc_surv_issue(data["matrix_u_string"]),
    'periodicity' : data["matrix_periodicity"],
    'matrix_irreducible' : is_matrix_irreducible(data["matrix_a_string"]),
    'matrix_primitive' : is_matrix_primitive(data["matrix_a_string"]),
    'matrix_ergodic' : is_matrix_ergodic(data["matrix_a_string"]),
    'matrix_lambda' : calc_lambda(data["matrix_a_string"])
    }

    matrix_cleaned = data_clean(matrix_dict)

    # if not all(value == None for key, value in matrix_cleaned["kwargs"].items() if key not in ignore_keys):
    matrix = Matrix(**matrix_cleaned["kwargs"])    

    db.session.add(matrix)
    db.session.commit()

    matrix.population_id = pop.id

    db.session.add(matrix)
    db.session.commit()

    ''' matrix Version '''
    version = version_data(matrix_cleaned)
    matrix_version = Version(**version)
    matrix_version.version_number = 1
    matrix_version.matrix = matrix    
    db.session.add(matrix_version) 
    db.session.commit()
    matrix_version.original_version_id = matrix_version.id
    db.session.add(matrix_version)
    db.session.commit()

    ''' Fixed '''

    fixed = Fixed.query.filter_by(matrix=matrix).first()

    if fixed == None:
        fixed_dict = {'matrix' : matrix,
        'census_timings' : CensusTiming.query.filter_by(census_name=data["fixed_census_timing_id"]).first(),
        'seed_stage_error' : coerce_boolean(data["fixed_seed_stage_error"]),
        'smalls' : Small.query.filter_by(small_name=data["fixed_small_id"]).first(),
        'vector_str' : data["matrix_vectors_includes_na"]
        }

        fixed_cleaned = data_clean(fixed_dict)
        fixed = Fixed(**fixed_cleaned["kwargs"])

        db.session.add(fixed)
        db.session.commit()

        ''' fixed Version '''
        version = version_data(fixed_cleaned)
        fixed_version = Version(**version)
        fixed_version.version_number = 1
        fixed_version.fixed = fixed    
        db.session.add(fixed_version) 
        db.session.commit()
        fixed_version.original_version_id = fixed_version.id
        db.session.add(fixed_version)
        db.session.commit()




def migration_loop(input_file):
    all_deets = []   

    for i, row in enumerate(input_file):  
        print i       
        data = convert_all_headers_new(row)
        submit_new(data)
    return "Migration Complete"

@manager.command
def migrate_compadre():
    import csv

    print "Migrating COMPADRE"
    compadre = UnicodeDictReader(open("app/data-migrate/compadre_migration_2017.csv", "rU"))
    return migration_loop(compadre)


@manager.command
def migrate_comadre():
    import csv

    print "Migrating COMADRE"
    comadre = UnicodeDictReader(open("app/data-migrate/comadre_migration_2017.csv", "rU"))
    return migration_loop(comadre)

@manager.command
def migrate_all():
    import csv
    
    print "Preparing to migrate COMPADRE and COMADRE"
    compadre = UnicodeDictReader(open("app/data-migrate/compadre_migration_2017.csv", "rU"))
    comadre = UnicodeDictReader(open("app/data-migrate/comadre_migration_2017.csv", "rU"))
    print "Migrating COMPADRE"
    migration_loop(compadre)
    print "Migrating COMADRE"
    migration_loop(comadre)
    return

def convert_all_headers_new(dict):
    import re

    new_dict = {}

    new_dict["species_gisd_status"] = dict["species_gisd_status"]
    new_dict["species_seedbank"] = dict["species_seedbank"]
    new_dict["species_clonality"] = dict["species_clonality"]
    new_dict["publication_purpose_comparative_demography"] = dict["publication_purpose_comparative_demography"]
    new_dict["publication_purpose_species_dynamics_description"] = dict["publication_purpose_species_dynamics_description"]
    new_dict["publication_purpose_spatial_demography"] = dict["publication_purpose_spatial_demography"]
    new_dict["publication_purpose_pva"] = dict["publication_purpose_pva"]
    new_dict["publication_purpose_methodological_advancement"] = dict["publication_purpose_methodological_advancement"]
    new_dict["publication_purpose_management_evaluation"] = dict["publication_purpose_management_evaluation"]
    new_dict["publication_purpose_interspecific_interactions"] = dict["publication_purpose_interspecific_interactions"]
    new_dict["publication_purpose_abiotic"] = dict["publication_purpose_abiotic"]
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
    new_dict["lat_ns"] = dict["lat_ns"]
    new_dict["lat_deg"] = dict["lat_deg"]
    new_dict["lat_min"] = dict["lat_min"]
    new_dict["lat_sec"] = dict["lat_sec"]
    new_dict["population_longitude"] = dict["population_longitude"]
    new_dict["lon_ew"] = dict["lon_ew"]
    new_dict["lon_deg"] = dict["lon_deg"]
    new_dict["lon_min"] = dict["lon_min"]
    new_dict["lon_sec"] = dict["lon_sec"]   
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
    #new_dict["population_pop_size"] = dict["population_pop_size"]
    new_dict["species_iucn_status_id"] = dict["species_iucn_status"]
    new_dict["publication_date_digitization"] = dict["publication_date_digitization"]
    # new_dict["species_esa_status_id"] = dict["species_esa_status"]
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
    #new_dict["version_checked"] = dict["matrix_checked"] #column not in scv?
    new_dict["version_checked_count"] = dict["matrix_checked_count"]
    new_dict["taxonomy_genus_accepted"] = dict["taxonomy_genus_accepted"]
    new_dict["matrix_independent"] = dict["matrix_independent"]
    new_dict["matrix_non_independence"] = dict["matrix_non_independence"]
    new_dict["matrix_non_independence_author"] = dict["matrix_non_independence_author"]
    new_dict["matrix_difficulty"] = dict["matrix_difficulty"]
    new_dict["matrix_complete"] = dict["matrix_complete"]
    new_dict["matrix_seasonal"] = dict["matrix_seasonal"]
    #new_dict["database_master_version"] = dict["database_master_version"]
    new_dict["population_database_id"] = dict["database_master_version"]
    #new_dict["database_date_created"] = dict["database_date_created"]
    #new_dict["database_number_species_accepted"] = dict["database_number_species_accepted"]
    #new_dict["database_number_studies"] = dict["database_number_studies"]
    #new_dict["database_number_matrices"] = dict["database_number_matrices"]
    #new_dict["database_agreement"] = dict["database_agreement"]
    new_dict["taxonomy_col_check_ok"] = dict["taxonomy_col_check_ok"]
    new_dict["taxonomy_col_check_date"]= dict["taxonomy_col_check_date"]
    new_dict["matrix_independence_origin"] = dict["matrix_independence_origin"]
    new_dict['image_path'] = dict["image_path"]
    new_dict['image_path2'] = dict["image_path2"]
    new_dict['species_iucn_taxonid'] = dict["species_iucn_taxonid"]
    
    # correspondence
    new_dict['publication_corresponding_author'] = dict["publication_corresponding_author"]
    new_dict['publication_corresponding_email'] = dict["publication_corresponding_email"]
    new_dict['date_author_contacted'] = dict["date_author_contacted"]
    new_dict['date_author_contacted_again'] = dict["date_author_contacted_again"]
    new_dict['correspondence_email_content'] = dict["correspondence_email_content"] # what was missing from publication (asked for)
    new_dict['correspondence_author_reply'] = dict["correspondence_author_reply"] # did they reply?
    new_dict['publication_student'] = dict["publication_student"] #who asked for it
    new_dict['extra_content_email'] = dict["extra_content_email"] # extra information asked for
    
    new_dict['publication_missing_data'] = dict["publication_missing_data"] # attatched to publication as a note about what is missing
    new_dict['population_within_site_replication'] = dict["within_site_replication"]
    new_dict['study_database_source_id'] = dict["study_database_source"]
    new_dict['publication_study_notes'] = dict["publication_study_notes"]
    new_dict['publications_protocol_id'] = dict["publications_protocol"]
    new_dict['digitization_protocol_id'] = dict["digitization_protocol"]
    new_dict['commonterm_id'] = dict["commonterm"]
    
    for key, value in new_dict.iteritems():
        if value == "NA":
            new_dict[key] = None
        if value == "":
            new_dict[key] = None
        if value == "None":
            new_dict[key] = None
        if value == "NC":
            new_dict[key] = None
        if value == ".":
            new_dict[key] = None
        if value == "AFI":
            new_dict[key] = 'NDY'


    return new_dict


@manager.command
def migrate_meta():
    from app.models import User, Role, Permission, \
    IUCNStatus, OrganismType, GrowthFormRaunkiaer, ReproductiveRepetition, \
    DicotMonoc, AngioGymno, SpandExGrowthType, SourceType, Database, Purpose, MissingData, ContentEmail, Ecoregion, Continent, InvasiveStatusStudy, InvasiveStatusElsewhere, StageTypeClass, \
    TransitionType, MatrixComposition, StartSeason, StudiedSex, Captivity, Species, Taxonomy, Trait, \
    Publication, AuthorContact, AdditionalSource, Population, Stage, StageType, Treatment, \
    MatrixStage, MatrixValue, Matrix, Interval, Fixed, Small, CensusTiming, PurposeEndangered, PurposeWeed, Institute, Version, \
    PublicationsProtocol, DigitizationProtocol, Protocol, CommonTerm

    print "Migrating Meta Tables..."
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
    Version.migrate()
    Institute.migrate()
    User.migrate()
    Database.migrate()
    Status.migrate()
    PublicationsProtocol.migrate()
    DigitizationProtocol.migrate()
    CommonTerm.migrate()
   
    return

def model_version(model):
    count = model.query.count()
    for x in range(count):
        y = model.query.get(x+1)
        y.version_latest = 1
        y.version_original = 1
        y.version_ok = 1
        db.session.add(y)
        db.session.commit()

@manager.command
def version_current():
    models = [Species(), Taxonomy(), Trait(), Publication(), AuthorContact(), Population(), StageType(), MatrixValue(),Matrix(), Fixed(), Institute(), Protocol()]
    
    for model in models:
        model_version(model)

@manager.command
def deploy():
    """Run deployment tasks."""
    from flask.ext.migrate import upgrade, migrate, init
    from app.models import User, Role, Permission
    


    print "Migrating models to database"
    init()
    migrate()
    upgrade()
    migrate()

    print "Models migrated to database"

    print "Migrating meta data to tables"
    migrate_meta()
    print "Meta tables migrated"

    print "Initial migration of our current version of database..."
    # migrate_comadre()
    migrate_all()


if __name__ == '__main__':
    manager.run()
