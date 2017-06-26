from flask import Flask, redirect, render_template, session, url_for, flash, request, send_file
from flask.ext.wtf import Form 
from flask.ext.sqlalchemy import SQLAlchemy 
from wtforms import StringField, SubmitField 
from wtforms.validators import Required 
from flask.ext.bootstrap import Bootstrap
from flask.ext.mail import Mail, Message 
import os
import zipfile 
app = Flask(__name__)
from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response, jsonify
from flask.ext.login import login_required, current_user
from flask.ext.sqlalchemy import get_debug_queries
from . import main
from .forms import ContactForm
from flask_mail import Mail, Message
from flask.ext.mail import Message, Mail
from app import mail, create_app
from app.matrix_functions import all_species_unreleased, all_populations_unreleased,all_matrices_unreleased, \
all_species_unreleased_complete, all_populations_unreleased_complete, all_matrices_unreleased_complete, \
all_species_released_complete, all_populations_released_complete, all_matrices_released_complete, \
all_species_released_compadre, all_populations_released_compadre, all_matrices_released_compadre, \
all_species_released_comadre, all_populations_released_comadre, all_matrices_released_comadre, \
all_matrices, all_pops, all_species, count_plants, count_comadre, count_compadre, count_plants_pop, count_compadre_pop, count_comadre_pop, species_compadre_count, species_comadre_count
from ..data_manage.forms import SpeciesForm, TaxonomyForm, TraitForm, PopulationForm, MatrixForm, PublicationForm, DeleteForm
import random
from .. import db
from ..models import Permission, Role, User, \
                    IUCNStatus, OrganismType, GrowthFormRaunkiaer, ReproductiveRepetition, \
                    DicotMonoc, AngioGymno, SpandExGrowthType, SourceType, Database, Purpose, MissingData, ContentEmail, Ecoregion, Continent, InvasiveStatusStudy, InvasiveStatusElsewhere, StageTypeClass, \
                    TransitionType, MatrixComposition, StartSeason, EndSeason, StudiedSex, Captivity, Species, Taxonomy, PurposeEndangered, PurposeWeed, Trait, \
                    Publication, AuthorContact, AdditionalSource, Population, Stage, StageType, Treatment, \
                    MatrixStage, MatrixValue, Matrix, Interval, Fixed, Small, CensusTiming, Institute, Status, Version, ChangeLogger, DigitizationProtocol
from ..decorators import admin_required, permission_required, crossdomain
from werkzeug import secure_filename

@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['FLASKY_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n'
                % (query.statement, query.parameters, query.duration,
                   query.context))
    return response


#@main.route('/shutdown')
#def server_shutdown():
#    if not current_app.testing:
#        abort(404)
#    shutdown = request.environ.get('werkzeug.server.shutdown')
#    if not shutdown:
#        abort(500)
#    shutdown()
#    return 'Shutting down...'

# HOMEPAGE

@main.route('/', methods=['GET', 'POST'])
def index():
    ##Released and Complete Stats
    #1. Total
    all_species_released_green = all_species_released_complete()
    all_populations_released_green = all_populations_released_complete()
    all_matrices_released_green = all_matrices_released_complete()
    #2. Compadre
    all_species_released_compadre_green = all_species_released_compadre()
    all_populations_released_compadre_green = all_populations_released_compadre()
    all_matrices_released_compadre_green = all_matrices_released_compadre()
    #3. Comadre
    all_species_released_comadre_green = all_species_released_comadre()
    all_populations_released_comadre_green = all_populations_released_comadre()
    all_matrices_released_comadre_green = all_matrices_released_comadre()
    ##Released and Incomplete Stats
    #NDY 1. total, 2. compadre, 3. comadre

    ##Unreleased and Incomplete Stats
    #1. Total 
    all_species_unreleased_amber = all_species_unreleased()
    all_populations_unreleased_amber = all_populations_unreleased()
    all_matrices_unreleased_amber = all_matrices_unreleased()
    #2. Compadre
    #NDY
    #3. Comadre
    #NDY
    ##Unreleased and Complete Stats
    #1. Total
    all_species_unreleased_green = all_species_unreleased_complete()
    all_populations_unreleased_green = all_populations_unreleased_complete()
    all_matrices_unreleased_green = all_matrices_unreleased_complete()
    #2. Compadre
    #3. Comadre

    ##Admin use only stats
    #Matrix Stats
    count_matrices = all_matrices()
    comadre_count = count_comadre()
    compadre_count = count_compadre()
    plant_count = count_plants()
    #Population Stats
    count_pops = all_pops()
    comadre_count_pop = count_comadre_pop()
    compadre_count_pop = count_compadre_pop()
    plant_count_pop = count_plants_pop()
    #Species stats
    species_count = all_species()
    species_count_compadre = species_compadre_count()
    species_count_comadre = species_comadre_count()
    
    species = Species.query.filter(Species.image_path != None).all()
    number = len(species)
    species2 = []
    for i in range(1,5):
        random_int = random.randint(0,number-1)
        s = species[random_int]
        while "www" in s.image_path:
            random_int = random.randint(0,number-1)
            s = species[random_int]
        species2.append(s)
    return render_template('index.html',species2 = species2, all_species_released_green = all_species_released_green, all_populations_released_green = all_populations_released_green, 
           all_matrices_released_green = all_matrices_released_green, all_species_released_compadre_green = all_species_released_compadre_green,
           all_populations_released_compadre_green = all_populations_released_compadre_green, all_matrices_released_compadre_green = all_matrices_released_compadre_green, 
           all_species_released_comadre_green = all_species_released_comadre_green, all_populations_released_comadre_green = all_populations_released_comadre_green, all_matrices_released_comadre_green = all_matrices_released_comadre_green, 
           all_species_unreleased_amber = all_species_unreleased_amber, all_species_unreleased_green = all_species_unreleased_green, 
           all_populations_unreleased_amber = all_populations_unreleased_amber, all_populations_unreleased_green = all_populations_unreleased_green, 
           all_matrices_unreleased_amber = all_matrices_unreleased_amber, all_matrices_unreleased_green = all_matrices_unreleased_green, 
           count_matrices = count_matrices, comadre_count = comadre_count, compadre_count = compadre_count, plant_count = plant_count, 
           count_pops = count_pops, comadre_count_pop = comadre_count_pop, compadre_count_pop = compadre_count_pop, plant_count_pop = plant_count_pop,
           species_count = species_count, species_count_compadre = species_count_compadre, species_count_comadre = species_count_comadre)


# now defunct 'display all data' page
@main.route('/data/')
# @login_required
def data():
    species = Species.query.all()

    return render_template('data.html', species=species)

### TABLE PAGES
# the big table of species
@main.route('/species-table/')
def species_table():
    # species = Species.query.all()
    species = Species.query.all()
    return render_template('species_table_template.html', species=species)

# the big table of publications
@main.route('/publications-table/')
def publications_table():
    publications = Publication.query.all()
    return render_template('publications_table_template.html', publications=publications)

###############################################################################################################################
### OVERVIEW PAGES
# species overview page
@main.route('/species=<list:species_ids>/publications=<list:pub_ids>')
def species_page(species_ids,pub_ids):
    if species_ids[0] == "all" and pub_ids[0] == "all":
        flash('Loading all species and publications is not allowed, sorry.')
        abort(404)
        
        
    can_edit = False
    try:
        if current_user.role_id in [1,3,4,6]:
            can_edit = True
    except:
        pass
    
    try:
        #get species
        all_species = []
        if species_ids[0] != "all": # aka if species are filtered
            for id in species_ids:
                all_species.append((Species.query.filter_by(id=id)).first())

            all_populations_species = []
            for species in all_species:
                all_populations_species.extend(Population.query.filter_by(species_id=species.id).all())

        #get pubs
        all_pubs = []
        if pub_ids[0] != "all": # aka if publications are being filtered
            for id in pub_ids:
                all_pubs.append((Publication.query.filter_by(id=id)).first())

            all_populations_pubs = []
            for publications in all_pubs:
                all_populations_pubs.extend(Population.query.filter_by(publication_id=publications.id).all())
    except:
        abort(404)
            
    # variable for whether to show the compadrino info box at the top (when only 1 publication is selected)
    compadrino_info = False
    if species_ids[0] == "all" and len(pub_ids) == 1:
        compadrino_info = True
        
      
    # Pick the right populations + get stuff
    if species_ids[0] == "all": # aka if species are filtered 
        populations = all_populations_pubs
    elif pub_ids[0] == "all": # aka if publications are being filtered
        populations = all_populations_species
    else: # aka if publications AND species are being filtered
        populations = set(all_populations_species).intersection(all_populations_pubs)
    
    
    if species_ids[0] != "all":  #aka if species are filtered 
        all_pubs = []
        for population in populations:
            all_pubs.append(Publication.query.filter_by(id=population.publication_id).first())
        
    if pub_ids[0] != "all": # aka if publications are being filtered
        all_species = []
        for population in populations:
            all_species.append(Species.query.filter_by(id=population.species_id).first())
        

          
    # remove duplicates 
    populations = list(set(populations))
    all_species = list(set(all_species))
    publications = list(set(all_pubs))
    
    # remove unchecked populations
    if can_edit == False:
        checked_pops = []
        waiting_list_note = False

        for population in populations:
            if population.version[0].status_id ==3:
                checked_pops.append(population)
            else:
                waiting_list_note = True
                
        populations = checked_pops
        if waiting_list_note == True:
            flash('There are matrices coming soon for this species/publication')
    
    #print(publications)
    #publications.sort();
    #print(publications)
    
    #flash('test')
    
    exeter_data = False
    try:
        if current_user.institute.institution_short == "UoE" and current_user.institute_confirmed == 1:
            exeter_data = True
        if current_user.institute.institution_short == "UOS" and current_user.institute_confirmed == 1:
            exeter_data = True
    except:
        pass

    
    protocol = DigitizationProtocol.query.all() 
        
    protocol_dict = {}
    for ocol in protocol:
        protocol_dict[ocol.name_in_csv] = ocol.field_short_description   
    
    return render_template('species_template.html',all_species = all_species, publications = publications, populations = populations,can_edit = can_edit,exeter_data = exeter_data,compadrino_info = compadrino_info,protocol_dict = protocol_dict)

@main.route('/protocol')
def protocol_page():
    protocol = DigitizationProtocol.query.all() 
        
    protocol_dict = {}
    for ocol in protocol:
        protocol_dict[ocol.name_in_csv] = ocol.field_description 
        
    return render_template('protocol_template.html',protocol_dict = protocol_dict,protocol = protocol)

# Taxonomic explorer
# DOES NOT WORK IN FIREFOX
@main.route('/explorer/<taxon_level>/<taxon>')
# @login_required
def explorer(taxon_level,taxon):
    if taxon_level == "life":
        taxon_list = Taxonomy.query.all()
        next_taxon_level = "kingdom"
        tax_pos = 0
    elif taxon_level == "kingdom":
        taxon_list = Taxonomy.query.filter_by(kingdom=taxon).all()
        next_taxon_level = "phylum"
        tax_pos = 1
    elif taxon_level == "phylum":
        taxon_list = Taxonomy.query.filter_by(phylum=taxon).all()
        next_taxon_level = "class" 
        tax_pos = 2
    elif taxon_level == "class":
        taxon_list = Taxonomy.query.filter_by(tax_class=taxon).all()
        next_taxon_level = "order"
        tax_pos = 3
    elif taxon_level == "order":
        taxon_list = Taxonomy.query.filter_by(tax_order=taxon).all()
        next_taxon_level = "family"
        tax_pos = 4
    elif taxon_level == "family":
        taxon_list = Taxonomy.query.filter_by(family=taxon).all()
        next_taxon_level = "species"
        tax_pos = 5
    
    
    return render_template('explorer_template.html',taxon=taxon,taxon_list = taxon_list,taxon_level=taxon_level,next_taxon_level=next_taxon_level, tax_pos = tax_pos)


# contribute
@main.route('/contribute-data')
def contribute_data():
    return render_template('contribute_data.html')

#coming soon page
@main.route('/comingsoon')
def comingsoon():
    return render_template('coming_soon.html')

###############################################################################################################################
### Become a Compadrino Form and HTML page
@main.route('/become-a-compadrino', methods=('GET', 'POST'))
def become_a_compadrino():
    form = ContactForm()
    if request.method == 'POST':
        if form.validate() == False:
            flash('All fields are required.')
            return render_template('become_a_compadrino.html', form=form)
        else:
            msg = Message("Demography Database Message from your visitor " + form.name.data,
                          sender='YourUser@NameHere',
                          recipients=['spandex.ex@gmail.com', 'd.l.buss@exeter.ac.uk', 'demographydatabase@gmail.com'])
            msg.body = """
            From: %s <%s>,
            Subject: %s
            Message: %s
            """ % (form.name.data, form.email.data, form.subject.data, form.message.data)
            mail.send(msg)
            flash('Successfully  sent message! If you do not receive a response within 10 working days, I apologise for this, please resend your enquiry.')
            return render_template('become_a_compadrino.html', form=form)
    elif request.method == 'GET':
        return render_template('become_a_compadrino.html', form=form)

### Report a Website Error Form
@main.route('/error-form', methods=('GET', 'POST'))
def error_form():
    form = ContactForm()
    if request.method == 'POST':
        if form.validate() == False:
            flash('All fields are required.')
            return render_template('Error_form.html', form=form)
        else:
            msg = Message("Demography Database Message from your visitor " + form.name.data,
                          sender='YourUser@NameHere',
                          recipients=['spandex.ex@gmail.com', 'd.l.buss@exeter.ac.uk', 'demographydatabase@gmail.com'])
            msg.body = """
            From: %s <%s>,
            Subject: %s
            Message: %s
            """ % (form.name.data, form.email.data, form.subject.data, form.message.data)
            mail.send(msg)
            flash('Successfully  sent message! Thank you for reporting the error, we will try and fix this as soon as possible. If the problem persists please resend your enquiry after 10 working days.')
            return render_template('Error_form.html', form=form)
    elif request.method == 'GET':
        return render_template('Error_form.html', form=form)

### Help Develop Site Form
@main.route('/help-develop-site', methods=('GET', 'POST'))
def help_develop_site():
    form = ContactForm()

    if request.method == 'POST':
        if form.validate() == False:
            flash('All fields are required.')
            return render_template('help_develop_site.html', form=form)
        else:
            msg = Message("Demography Database Message from your visitor " + form.name.data,
                          sender='YourUser@NameHere',
                          recipients=['spandex.ex@gmail.com', 'd.l.buss@exeter.ac.uk', 'demographydatabase@gmail.com'])
            msg.body = """
            From: %s <%s>,
            Subject: %s
            Message: %s
            """ % (form.name.data, form.email.data, form.subject.data, form.message.data)
            mail.send(msg)
            flash('Successfully  sent message! If you do not receive a response within 10 working days, I apologise for this, please resend your enquiry.')
            return render_template('help_develop_site.html', form=form)
    elif request.method == 'GET':
        return render_template('help_develop_site.html', form=form)



# USER + PROFILE PAGES
# User
@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()    
    return render_template('user.html', user=user)

##Trying get uploads to work - Success 
##Need to alter file path once on the Exeter server!!!!!
UPLOAD_FOLDER = '/Users/daniellebuss/Sites/demography_database/app/static/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'csv', 'RData', 'DS_Store'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/datadownloads', methods=['GET', 'POST'])
def datadownloads():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return render_template('upload_files.html',
                filename=filename, type=file.content_type)
    return render_template('datadownloads.html')

@main.route('/download_all')
def download_all():
    UPLOAD_FOLDER = '/Users/daniellebuss/Sites/demography_database/app/static/uploads/'
    zipf = zipfile.ZipFile('Database.zip', 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(UPLOAD_FOLDER):
        for file in files:
            zipf.write(UPLOAD_FOLDER+file)
        zipf.close()
        return send_file('Database.zip',
            mimetype = 'zip',
            attachment_filename = 'Database.zip',
            as_attachment = True)

#@main.route('/return-file/', methods=['GET', 'POST'])
#def return_file():
#    return send_file('/Users/daniellebuss/Sites/demography_database/app/static/uploads/COMADRE_v_2_0_1.RData', attachment_filename='comadre_2.RData')

#Download file html template
@main.route('/download')
def download():
    return render_template('outputs/download.html')

#Download COMADRE 2.0.1
@main.route('/download-zip/', methods=['GET', 'POST'])
def download_zip():
    file_name = '/Users/daniellebuss/Sites/demography_database/app/static/uploads/COMADRE_v_2_0_1.RData'
    return send_file(file_name, as_attachment=True, mimetype='text/plain')

#Download COMADRE xxx
@main.route('/download-zip2/', methods=['GET', 'POST'])
def download_zip2():
    file_name = '/Users/daniellebuss/Sites/demography_database/app/static/uploads/COMADRE_v_xxx.RData'
    return send_file(file_name, as_attachment=True, mimetype='text/plain')

#Download COMPADRE xxx
@main.route('/download-zip3/', methods=['GET', 'POST'])
def download_zip3():
    file_name = '/Users/daniellebuss/Sites/demography_database/app/static/uploads/COMPADRE_v_xxx.RData'
    return send_file(file_name, as_attachment=True, mimetype='text/plain')

#Download COMPADRE 4.0.1
@main.route('/download-zip4/', methods=['GET', 'POST'])
def download_zip4():
    file_name = '/Users/daniellebuss/Sites/demography_database/app/static/uploads/COMPADRE_v_4_0_1.RData'
    return send_file(file_name, as_attachment=True, mimetype='text/plain')

#Download current SQL Dump (This gets updated Daily)
#!!!On server file is /var/www/demography-database/alchemydumps/demography-database.sql
@main.route('/download-sql/', methods=['GET', 'POST'])
def download_sql():
    file_name = '/Users/daniellebuss/Sites/demography_database/application_tasks/mysql_dump/demography_database.sql'
    return send_file(file_name, as_attachment=True, mimetype='text/plain')

@main.route('/downloadsql')
def downloadsql():
    return render_template('outputs/download_sql.html')

#@main.route('/datadownloads')
#def datadownloads():
#    return render_template('datadownloads.html')

#@main.route('/upload', methods=['GET','POST'])
#def upload():
    # Get the name of the uploaded file
#    file = request.files['file']
    # Check if the file is one of the allowed types/extensions
#    if file and allowed_file(file.filename):
        # Make the filename safe, remove unsupported chars
#        filename = secure_filename(file.filename)
        # Move the file form the temporal folder to
        # the upload folder we setup
#        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Redirect the user to the uploaded_file route, which
        # will basicaly show on the browser the uploaded file
#        return redirect(url_for('uploaded_file',
#                                filename=filename))

@main.route('/uploads/<filename>', methods=['GET', 'POST'])
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)






