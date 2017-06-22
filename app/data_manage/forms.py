from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField, DecimalField, IntegerField, DateField, FloatField, FormField
from wtforms.validators import Required, Length, Email, Regexp, Optional
from wtforms import ValidationError
from flask.ext.pagedown.fields import PageDownField
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from ..models import IUCNStatus,  OrganismType, GrowthFormRaunkiaer, ReproductiveRepetition, \
    DicotMonoc, AngioGymno, SpandExGrowthType, SourceType, Database, Purpose, MissingData, ContentEmail, Ecoregion, Continent, InvasiveStatusStudy, InvasiveStatusElsewhere, StageTypeClass, \
    TransitionType, MatrixComposition, StartSeason, EndSeason, StudiedSex, Captivity, Species, Taxonomy, Trait, \
    Publication, AuthorContact, AdditionalSource, Population, Stage, StageType, Treatment, \
    MatrixStage, MatrixValue, Matrix, Interval, Fixed, Small, CensusTiming, PurposeEndangered, PurposeWeed, Institute, Status
from wtforms.fields.html5 import DateField
    

def stringFromText(string):
    #Formatting string and separating for use as a list
    #string usually contained within [], remove these
    if string.startswith('[') and string.endswith(']'):
        string = string[1:-1]
        matrix = []
        xl = string.split(' ')
        for x in xl:
            # print x
            if x != '':
                if x == 'NA':
                    matrix.append(0)
                else:
                    if x == 'NDY':
                        matrix.append(0)
                    else:
                        matrix.append(float(x.strip()))

        return matrix


def classNamesFromText(string):
    classNames = string.split('|')
    return classNames

def dimensionSquared(classnames, matrix):
    m = len(matrix)
    c = len(classnames)
    s = len(classnames)*len(classnames)

    if s == m:
        return True
    else:
        return False

def dimensionSize(classnames):
    return len(classnames)

def validate_dimension(matrix, classnames):
    classnames = classNamesFromText(classnames)
    matrix = stringFromText(matrix)
    squared = dimensionSquared(classnames, matrix)
    dimension = dimensionSize(classnames)
    return squared

class VersionForm(Form):
    checked = BooleanField('Has this field been checked?')
    status = QuerySelectField('Status',
            query_factory=lambda: Status.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:'{} ({})'.format(a.status_name, a.status_description))
    checked_count = IntegerField('How many times has this been checked?')
    submit = SubmitField('Submit')

class SpeciesForm(Form):
    species_accepted = StringField('Species Accepted', validators=[Required()])
    species_common = StringField('Species Common Name')
    iucn_status = QuerySelectField('IUCN Status',
            query_factory=lambda: IUCNStatus.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:'{} - {} ({})'.format(a.status_code, a.status_name, a.status_description))
    species_iucn_taxonid = IntegerField('IUCN Taxon key', validators=[Optional()])
    gbif_taxon_key = IntegerField('GBIF Taxon Key', validators=[Optional()])
    image_path = StringField('Path to image')
    image_path2 = StringField('Path to image')
    
    
    submit = SubmitField('Submit')

# Taxonomy form, up to date: 30/1/17
class TaxonomyForm(Form):
    authority = StringField('Authority', validators=[])
    tpl_version = StringField('TPL Version')
    infraspecies_accepted = StringField('Infraspecies Accepted')
    species_epithet_accepted = StringField('Species Epithet Accepted', validators=[Required()])
    genus_accepted = StringField('Genus Accepted', validators=[Required()])
    genus = StringField('Genus', validators=[Required()])
    family = StringField('Family', validators=[Required()])
    tax_order = StringField('Order', validators=[Required()])
    tax_class = StringField('Class', validators=[Required()])
    phylum = StringField('Phylum', validators=[Required()])
    kingdom = StringField('Kingdom', validators=[Required()])
    col_check_ok = BooleanField('Col Check OK')
    col_check_date = DateField('Col Check Date', validators=[Optional()])

    submit = SubmitField('Submit')
    
#trait form, up to date 30/1/17
class TraitForm(Form):
    #max_height = FloatField('Max Height')
    organism_type = QuerySelectField('Organism type',
            query_factory=lambda: OrganismType.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:a.type_name)
    growth_form_raunkiaer = QuerySelectField('Growth Form Raunkiaer',
            query_factory=lambda: GrowthFormRaunkiaer.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:a.form_name)
    reproductive_repetition = QuerySelectField('Reproductive Repetition',
            query_factory=lambda: ReproductiveRepetition.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:a.repetition_name)
    dicot_monoc = QuerySelectField('Dicot Monoc',
            query_factory=lambda: DicotMonoc.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:a.dicot_monoc_name)
    angio_gymno = QuerySelectField('Angio Gymno',
            query_factory=lambda: AngioGymno.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:a.angio_gymno_name)
    spand_ex_growth_types = QuerySelectField('Spand.ex growth type',
            query_factory=lambda: SpandExGrowthType.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:a.type_name)
    species_seedbank = BooleanField('Species seedbank')
    species_seedbank_source = StringField('Species seedbank source')
    species_clonality = BooleanField('Species clonality')
    species_clonality_source = StringField('Species clonality source')
    species_gisd_status = BooleanField('Species GISD status')
    submit = SubmitField('Submit')
   
# up to date 12/1/16
class PublicationForm(Form):
    
    source_type = QuerySelectField('Source Type',
            query_factory=lambda: SourceType.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:'{} - {}'.format(a.source_name, a.source_description))	
    authors = StringField('Publication Authors *', validators=[Required()])
    editors = StringField('Publication Editors')
    journal_name = StringField('Journal/Publication Title (ie J Ecol) *', validators=[Required()])
    journal_book_conf = StringField('Journal/Book Conf')
    year = IntegerField('Year Publication Published *', validators=[Required()])
    volume = StringField('Journal/Publication Volume')
    pages  = StringField('Publication Pages')
    publisher = StringField('Publication Publisher')
    city = StringField('Publication City')
    country = StringField('Publication Country')
    institution = StringField('Publication Institution')
    DOI_ISBN = StringField('DOI/ISBN')
    pub_title = StringField('Publication_title')
    #corresponding_author = StringField('Corresponding Author')
    #email = StringField('Email Address', validators=[Email(),Optional()])
    #purposes = QuerySelectField('Purposes',query_factory=lambda: Purpose.query.all(), get_pk=lambda a: a.id,get_label=lambda a:'{} - {}'.format(a.purpose_name, a.purpose_description))
    purposes = QuerySelectMultipleField(query_factory=lambda: Purpose.query.all(), get_pk=lambda a: a.id,get_label=lambda a:'{} - {}'.format(a.purpose_name, a.purpose_description))
    date_digitised = DateField('Date digitized',validators=[Optional()])
    embargo = DateField('Embargo',validators=[Optional()])
    #missing_data = QuerySelectField('Missing Data',query_factory=lambda: MissingData.query.all(), get_pk=lambda a: a.id,get_label=lambda a:'{} - {}'.format(a.missing_code, a.missing_description))
    additional_source_string = StringField('Additional Source')
    study_notes = StringField('Additional notes')
    student = StringField('Student')
    # author_contacts # Fkey#additional_sources # Fkey
    submit = SubmitField('Submit')

# population form, up to date
class PopulationForm(Form):
    
    species_author = StringField('Species Author')
    population_name = StringField('Population Name *', validators=[Required()])
    ecoregion = QuerySelectField('Ecoregion',
            query_factory=lambda: Ecoregion.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:'{} - {}'.format(a.ecoregion_code, a.ecoregion_description))
    country = StringField('Country')
    population_nautical_miles = IntegerField('Population nautical miles',validators=[Optional()])
    continent = QuerySelectField('Continent',
            query_factory=lambda: Continent.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:a.continent_name)
    lat_ns = StringField('Latitude N or S',validators=[Optional()])
    lat_deg = IntegerField('Latitude degrees',validators=[Optional()])
    lat_min = IntegerField('Latitude minutes',validators=[Optional()])
    lat_sec = IntegerField('Latitude seconds',validators=[Optional()])
    lon_ew = StringField('Longitude E or W',validators=[Optional()])
    lon_deg = IntegerField('Longitude degrees',validators=[Optional()])
    lon_min = IntegerField('Longitude minutes',validators=[Optional()])
    lon_sec = IntegerField('Longitude seconds',validators=[Optional()])
    altitude = FloatField('Altitude in metres',validators=[Optional()])
    within_site_replication = StringField('Within site replication')
    study_start = IntegerField('Study start (year)',validators=[Optional()])
    study_end = IntegerField('Study end (year)',validators=[Optional()])
    invasive_status_study = QuerySelectField('Invasive status in study',
            query_factory=lambda: InvasiveStatusStudy.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:a.status_description)
    invasive_status_elsewhere = QuerySelectField('Invasive status elsewhere',
            query_factory=lambda: InvasiveStatusElsewhere.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:a.status_description)
    purpose_endangered = QuerySelectField('Purpose endangered',
            query_factory=lambda: PurposeEndangered.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:a.purpose_description)
    purpose_weed = QuerySelectField('Purpose weed',
            query_factory=lambda: PurposeWeed.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:a.purpose_description)
    database_source = QuerySelectField('Database source',query_factory=lambda: Database.query.all(), get_pk=lambda a: a.id,get_label=lambda a:a.database_description)
    submit = SubmitField('Submit')


#  matrix form, not up to date    
class MatrixForm(Form):
    
    treatment = QuerySelectField('Matrix Treatment *',
            query_factory=lambda: Treatment.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:a.treatment_name, validators=[Required()])
    matrix_split = BooleanField('Matrix Split')
    matrix_composition = QuerySelectField('Matrix Composition *',
            query_factory=lambda: MatrixComposition.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:a.comp_name, validators=[Required()])
    seasonal = BooleanField('Seasonal')
    n_intervals = IntegerField('Number of Intervals', validators=[Optional()])
    periodicity = FloatField('Periodicity')
    matrix_criteria_size = StringField('Matrix Criteria Size')
    matrix_criteria_ontogeny = BooleanField('Matrix Criteria Ontogeny')
    matrix_criteria_age = BooleanField('Matrix Criteria Age')
    matrix_start_year = IntegerField('Start Year', validators=[Optional()])
    matrix_start_month = IntegerField('Start Month', validators=[Optional()])
    matrix_end_year = IntegerField('End Year', validators=[Optional()])
    matrix_end_month = IntegerField('End Month', validators=[Optional()])
    matrix_start_season = QuerySelectField('Matrix Start Season',
            query_factory=lambda: StartSeason.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:'{} - {}'.format(a.season_id, a.season_name))
    matrix_end_season = QuerySelectField('Matrix End Season',
            query_factory=lambda: EndSeason.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:'{} - {}'.format(a.season_id, a.season_name))
    matrix_fec = BooleanField('Matrix Fecundity')
    matrix_dimension = IntegerField('Matrix Dimension *', validators=[Required()])
    matrix_a_string = TextAreaField('Matrix A String *', validators=[Required()]) #Must be in specific format
    matrix_u_string = TextAreaField('Matrix U String *', validators=[Required()]) #Must be in specific format
    matrix_f_string = TextAreaField('Matrix F String *', validators=[Required()]) #Must be in specific format
    matrix_c_string = TextAreaField('Matrix C String *', validators=[Required()]) #Must be in specific format
    matrix_difficulty = StringField('Matrix Difficulty')
    matrix_complete = BooleanField('Matrix complete')
    independence_origin = StringField('Independence origin')
    studied_sex = QuerySelectField('Studied Sex',
            query_factory=lambda: StudiedSex.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:'{} - {}'.format(a.sex_code, a.sex_description))
    captivity_id = QuerySelectField('Matrix Captivity',
            query_factory=lambda: Captivity.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:'{} - {}'.format(a.cap_code, a.cap_description))

    observations = TextAreaField('Observations')
    class_organized = StringField('Class organized')
    class_author = StringField('Class as described by the author')
    class_number = StringField('Class number')
    independent = BooleanField('Independent')
    non_independence = StringField('Non independence')
    non_independence_author = StringField('Author of non-independence')
    submit = SubmitField('Submit')
    
class FixedForm(Form):
    vector_str = StringField('Vector String')
    vector_present = BooleanField('Vector present')
    total_pop_no = IntegerField('Total population number', validators=[Optional()])
    smalls = QuerySelectField('Smalls',
            query_factory=lambda: Small.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:'{} - {}'.format(a.small_name, a.small_description))
    census_timing = QuerySelectField('Census timing',
            query_factory=lambda: CensusTiming.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:'{} - {}'.format(a.census_name, a.census_description))
    seed_stage_error = BooleanField('Seed stage error')
    private = BooleanField('Private')
    vectors_includes_na = BooleanField('Vectors includes NA')
    vectors_proportional = StringField('Vectors proportional')
    vector_class_names = StringField('Vector class names')
    submit = SubmitField('Submit')
    
    
# delete form   
class DeleteForm(Form):
    submit = SubmitField('Submit')







