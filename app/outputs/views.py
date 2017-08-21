from datetime import datetime
from flask import Flask, render_template, redirect, request, url_for
from flask_wtf import Form
from flask_wtf.file import FileField
from werkzeug import secure_filename
from flask import send_from_directory
from flask.ext.login import login_user, logout_user, login_required, current_user
from flask import *
from flask import send_file
from . import outputs
from .. import db
from bs4 import BeautifulSoup
from urllib2 import urlopen
from werkzeug.utils import secure_filename
from forms import Average, AddDatabaseForm, UploadForm
import numpy as np
import pandas as pd
import wtforms as wtf
import re
import os
from ..models import Permission, Role, User, \
                    IUCNStatus, OrganismType, GrowthFormRaunkiaer, ReproductiveRepetition, \
                    DicotMonoc, AngioGymno, SpandExGrowthType, SourceType, Database, Purpose, MissingData, ContentEmail, Ecoregion, Continent, InvasiveStatusStudy, InvasiveStatusElsewhere, StageTypeClass, \
                    TransitionType, MatrixComposition, StartSeason, EndSeason, StudiedSex, Captivity, Species, Taxonomy, PurposeEndangered, PurposeWeed, Trait, \
                    Publication, AuthorContact, AdditionalSource, Population, Stage, StageType, Treatment, \
                    MatrixStage, MatrixValue, Matrix, Interval, Fixed, Small, CensusTiming, Institute, Status, Version, ChangeLogger, DigitizationProtocol

#news
@outputs.route('/termsofuse')
def termsofuse():
    return render_template('outputs/terms_of_use.html')

##Downloading models as csvs - useful for creating R objects

@outputs.route('/populations')
def population_export():   
    import csv 
    
    # First, grab all matrices, as these will be each 'row'
    all_populations = Population.query.all()
    
    #function to merge dictionaries to a super dictionary
    def merge_dicts(*dict_args):
        result = {}
        for dictionary in dict_args:
            result.update(dictionary)
        return result
            
    w_file = open('app/outputs/populations.csv','w')

    #looping through rows
    for i, population in enumerate(all_populations):
        
        # Grab all of the parent objects
        population = population
        species = population.species
        publication = population.publication
        
        # Merge all of them to one single dict, as dict
        entry = merge_dicts(vars(population), vars(species), vars(publication))
        
        #If this is the first matrix, construct the headers too
        if i == 0:
            #get all the headings from entry - the super dict
            headings = [key for key in entry.keys()]
            headings = str(headings)
            w_file.write(headings[1:-1] + '\n')
            
        entry = str(entry.values())        
        # cleaning needed to be added here
        
        w_file.write(entry[1:-1] + '\n')
                     
    return ('populations success')

# outputs/downloads
#@outputs.route('/download_csv', methods=['GET', 'POST']) # this is a job for GET, not POST
#def download_csv():
#    return send_file('outputs/test.csv',
#                     mimetype='text/csv',
#                     attachment_filename='test.csv',
#                     as_attachment=True)

@outputs.route('/species')
def species_export():   
    import csv 
    
    # First, grab all matrices, as these will be each 'row'
    all_species = Species.query.all()
    
    #function to merge dictionaries to a super dictionary
    def merge_dicts(*dict_args):
        result = {}
        for dictionary in dict_args:
            result.update(dictionary)
        return result
            
    w_file = open('app/outputs/species.csv','w')

    #looping through rows
    for i, species in enumerate(all_species):
        
        # Grab all of the parent objects
        species = species
        traits = species.trait[0]
        taxonomy = species.taxonomy[0]
        
        # Merge all of them to one single dict, as dict
        entry = merge_dicts(vars(species), vars(taxonomy), vars(traits))
        
        #If this is the first matrix, construct the headers too
        if i == 0:
            #get all the headings from entry - the super dict
            headings = [key for key in entry.keys()]
            headings = str(headings)
            w_file.write(headings[1:-1] + '\n')
            
        entry = str(entry.values())
        # cleaning needed to be added here
        
        w_file.write(entry[1:-1] + '\n')
                     
    return ('success')

@outputs.route('/publications')
def publication_export():   
    import csv 
    
    # First, grab all matrices, as these will be each 'row'
    all_publications = Publication.query.all()
#    f = date_digitised
#    date_str = f.strftime('%Y-%m-%d')
#    all_publications.date_digitised = date_str

    #function to merge dictionaries to a super dictionary
    def merge_dicts(*dict_args):
        result = {}
        for dictionary in dict_args:
            result.update(dictionary)
        return result
            
    w_file = open('app/outputs/publications.csv','w')

    #looping through rows
    for i, publication in enumerate(all_publications):
        
        # Grab all of the parent objects
        publication = publication
        
        # Merge all of them to one single dict, as dict
        entry = merge_dicts(vars(publication))
        
        #If this is the first matrix, construct the headers too
        if i == 0:
            #get all the headings from entry - the super dict
            headings = [key for key in entry.keys()]
            headings = str(headings)
            w_file.write(headings[1:-1] + '\n')
            
        entry = str(entry.values())
        # cleaning needed to be added here
        
        w_file.write(entry[1:-1] + '\n')
                     
    return ('publications success')

@outputs.route('/matrices')
def matrices_export():   
    import csv 
    
    # First, grab all matrices, as these will be each 'row'
    all_matrices = Matrix.query.all()
    
    #function to merge dictionaries to a super dictionary
    def merge_dicts(*dict_args):
        result = {}
        for dictionary in dict_args:
            result.update(dictionary)
        return result
            
    w_file = open('app/outputs/matrix.csv','w')

    #looping through rows
    for i, matrix in enumerate(all_matrices):
        
        # Grab all of the parent objects
        matrix = matrix
        if matrix.fixed:
            fixed = matrix.fixed[0]
        
        # Merge all of them to one single dict, as dict
        entry = merge_dicts(vars(matrix),  vars(fixed))
        
        #If this is the first matrix, construct the headers too
        if i == 0:
            #get all the headings from entry - the super dict
            headings = [key for key in entry.keys()]
            headings = str(headings)
            w_file.write(headings[1:-1] + '\n')
            
        entry = str(entry.values())
        
        # cleaning
        # remove quotes from strings
        # remove u from unicode strings
        #[<taxonomy 1l="">] to 1
        # remove L from numbers
        # study purposes
        # remove fields we don't want
        # date time
        
        #re.sub("u'","",entry)
        
        w_file.write(entry[1:-1] + '\n')
                     
    return ('matrices successful')
#if __name__ == '__main__':
#   app.run(debug = True)