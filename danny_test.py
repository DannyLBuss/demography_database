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
    MatrixStage, MatrixValue, Matrix, Interval, Fixed, Small, CensusTiming, Status, PurposeEndangered, PurposeWeed, Version, Institute, EndSeason, ChangeLogger
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

from app.matrix_functions import as_array, calc_lambda, calc_surv_issue, is_matrix_irreducible, is_matrix_primitive, is_matrix_ergodic

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
                PurposeEndangered=PurposeEndangered, PurposeWeed=PurposeWeed, Version=Version, Institute=Institute, EndSeason=EndSeason, ChangeLogger = ChangeLogger)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

@danny_test.route('/handy-functions/', methods=['GET', 'POST'])
def all_matrices():
    all_matrices_count = Matrix.query.count()
    print all_matrices_count

#Count the number of matrices in COMADRE:
@danny_test.route('/handy-functions/', methods=['GET', 'POST'])
def count_comadre():
    count_comadre = Matrix.query.join(Matrix.population).join(Population.species).join(Species.taxonomy).filter(Taxonomy.kingdom == "Animalia").count()
    print count_comadre

#Count the number of matrices in COMPADRE:
@danny_test.route('/handy-functions/', methods=['GET', 'POST'])
def count_compadre():
     count_compadre = Matrix.query.join(Matrix.population).join(Population.species).join(Species.taxonomy).filter(Taxonomy.kingdom == "Plantae").count()
     print count_compadre