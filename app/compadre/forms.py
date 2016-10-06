from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField, DecimalField, IntegerField, DateField, FloatField, FormField
from wtforms.validators import Required, Length, Email, Regexp, Optional
from wtforms import ValidationError
from flask.ext.pagedown.fields import PageDownField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from ..models import IUCNStatus, ESAStatus, GrowthType, GrowthFormRaunkiaer, ReproductiveRepetition, \
    DicotMonoc, AngioGymno, DavesGrowthType, SourceType, Database, Purpose, MissingData, ContentEmail, Ecoregion, Continent, InvasiveStatusStudy, InvasiveStatusElsewhere, StageTypeClass, \
    TransitionType, MatrixComposition, Season, StudiedSex, Captivity, Species, Taxonomy, Trait, \
    Publication, Study, AuthorContact, AdditionalSource, Population, Stage, StageType, Treatment, TreatmentType, \
    MatrixStage, MatrixValue, Matrix, Interval, Fixed, Small, CensusTiming

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

class SpeciesForm(Form):
    species_accepted = StringField('Species Accepted', validators=[Required()])
    species_common = StringField('Species Common Name')
    iucn_status = QuerySelectField('IUCN Status',
            query_factory=lambda: IUCNStatus.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:'{} - {} ({})'.format(a.status_code, a.status_name, a.status_description))
    esa_status = QuerySelectField('ESA Status',
            query_factory=lambda: ESAStatus.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:'{} - {}'.format(a.status_code, a.status_name))
    GBIF_key = IntegerField('GBIF Taxon Key')
    image_path = StringField('Path to image')
    image_path2 = StringField('Path to image')
    invasive_status = BooleanField('Invasive Status')
    
    submit = SubmitField('Submit')

class TaxonomyForm(Form):
	species_author = StringField('Species Author *', validators=[Required(), ])
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

	submit = SubmitField('Submit')
    
class PublicationForm(Form):
    source_type = QuerySelectField('Source Type',
            query_factory=lambda: SourceType.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:'{} - {}'.format(a.source_name, a.source_description))	
    authors = StringField('Publication Authors *', validators=[Required()])
    editors = StringField('Publication Editors')
    pub_title = StringField('Jorunal/Publication Title (ie J Ecol) *', validators=[Required()])
    journal_book_conf = StringField('Journal/Book Conf')
    year = IntegerField('Year Publication Published *', validators=[Required()])
    volume = StringField('Journal/Publication Volume')
    pages  = StringField('Publication Pages')
    publisher = StringField('Publication Publisher')
    city = StringField('Publication City')
    country = StringField('Publication Country')
    institution = StringField('Publication Institution')
    DOI_ISBN = StringField('DOI/ISBN')
    pub_name = StringField('Publication Title')
    corresponding_author = StringField('Corresponding Author')
    email = StringField('Email Address', validators=[Email(),Optional()])
    purposes = QuerySelectField('Purposes',query_factory=lambda: Purpose.query.all(), get_pk=lambda a: a.id,get_label=lambda a:'{} - {}'.format(a.purpose_name, a.purpose_description))
    embargo = DateField('Embargo',validators=[Optional()])
    missing_data = QuerySelectField('Missing Data',query_factory=lambda: MissingData.query.all(), get_pk=lambda a: a.id,get_label=lambda a:'{} - {}'.format(a.missing_code, a.missing_description))
    additional_source_string = StringField('Additional Source')
    # author_contacts # Fkey#additional_sources # Fkey
    submit = SubmitField('Submit')

    
    
    
    
class StudyForm(Form):
	study_duration = IntegerField('Study Duration')
	study_start = IntegerField('Study Start')
	study_end = IntegerField('Study End')

class PopulationForm(Form):
    name = StringField('Population Name *', validators=[Required()])
    ecoregion = QuerySelectField('Ecoregion',
            query_factory=lambda: Ecoregion.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:'{} - {}'.format(a.ecoregion_code, a.ecoregion_description))
    country = StringField('Country')
    continent = QuerySelectField('Continent',
            query_factory=lambda: Continent.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:a.continent_name)
    lat_sec = StringField('Lat Sec')
    lon_we = StringField('Lon WE')
    lat_ns = StringField('Lat NS')
    lon_min = StringField('Lon Min')
    lon_sec = StringField('Lon Sec')
    altitude = StringField('Altitude')
    lat_min = StringField('Lat Min')
    lat_deg = StringField('Lat Deg')
    lon_deg = StringField('Lon Deg')
    submit = SubmitField('Submit')

class TraitForm(Form):
    max_height = FloatField('Max Height')
    growth_type = QuerySelectField('Growth Type',
            query_factory=lambda: GrowthType.query.all(), get_pk=lambda a: a.id,
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
    submit = SubmitField('Submit')
    
class MatrixForm(Form):
    treatment = StringField('Treatment *', validators=[Required()])
    matrix_split = BooleanField('Matrix Split')
    matrix_composition = QuerySelectField('Matrix Composition *',
            query_factory=lambda: MatrixComposition.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:a.comp_name, validators=[Required()])
    survival_issue = DecimalField('Survival Issue')
    n_intervals = DecimalField('Number of Intervals')
    periodicity = IntegerField('Periodicity')
    matrix_criteria_size = BooleanField('Matrix Criteria Size')
    matrix_criteria_ontogeny = BooleanField('Matrix Criteria Ontogeny')
    matrix_criteria_age = BooleanField('Matrix Criteria Age')
    matrix_start = StringField('Matrix Start *')
    #not working
    #, validators=[Required(), Regexp('^(\d{1}[/-]\d{1,4})*$', 0, 'Must be M/YYYY')])
    matrix_end = StringField('Matrix End')
    matrix_start_season = QuerySelectField('Matrix Start Season',
            query_factory=lambda: Season.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:'{} - {}'.format(a.season_id, a.season_name))
    matrix_end_season = QuerySelectField('Matrix End Season',
            query_factory=lambda: Season.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:'{} - {}'.format(a.season_id, a.season_name))
    matrix_fec = BooleanField('Matrix Fecundity')
    matrix_dimension = IntegerField('Matrix Dimension')
    matrix_a_string = TextAreaField('Matrix A String *', validators=[Required()]) #Must be in specific format
    matrix_u_string = TextAreaField('Matrix U String *', validators=[Required()]) #Must be in specific format
    matrix_f_string = TextAreaField('Matrix F String *', validators=[Required()]) #Must be in specific format
    matrix_c_string = TextAreaField('Matrix C String *', validators=[Required()]) #Must be in specific format
    matrix_class_string = TextAreaField('Matrix Class Names String *', validators=[Required()]) #Must be in specific format
    n_plots = IntegerField('# Plots')
    plot_size = IntegerField('Plot Size')
    n_individuals = IntegerField('# Individuals')
    studied_sex = QuerySelectField('Studied Sex',
            query_factory=lambda: StudiedSex.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:'{} - {}'.format(a.sex_code, a.sex_description))
    captivity_id = QuerySelectField('Matrix Captivity',
            query_factory=lambda: Captivity.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:'{} - {}'.format(a.cap_code, a.cap_description))

    observations = TextAreaField('Observations *', validators=[Required()])
    submit = SubmitField('Submit')
    
class DeleteForm(Form):
    submit = SubmitField('Submit')

class EntryForm(Form):
	# Species
	species_accepted = StringField('Species Accepted *', validators=[Required()], default="Cytisus scoparius")
	iucn_status = QuerySelectField('IUCN Status',
            query_factory=lambda: IUCNStatus.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:'{} - {} ({})'.format(a.status_code, a.status_name, a.status_description))
	esa_status = QuerySelectField('ESA Status',
            query_factory=lambda: ESAStatus.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:'{} - {}'.format(a.status_code, a.status_name))
	invasive_status = BooleanField('Invasive Status')

	# Taxonomy
	species_author = StringField('Species Author *', validators=[Required()], default="Cytisus_scoparius")
	authority = StringField('Authority', validators=[])
	tpl_version = DecimalField('TPL Version')
	infraspecies_accepted = StringField('Infraspecies Accepted', validators=[])
	species_epithet_accepted = StringField('Species Epithet Accepted', validators=[])
	genus_accepted = StringField('Genus Accepted', validators=[])
	genus = StringField('Genus', validators=[])
	family = StringField('Family', validators=[])
	tax_order = StringField('Order', validators=[])
	tax_class = StringField('Class', validators=[])
	phylum = StringField('Phylum', validators=[])
	kingdom = StringField('Kingdom', validators=[])

	# Plant Traits
	max_height = StringField('Max Height')
	growth_type = QuerySelectField('Growth Type',
            query_factory=lambda: GrowthType.query.all(), get_pk=lambda a: a.id,
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

	# Population
	name = StringField('Population Name *', validators=[Required()], default="Johnson Prairie; Discovery Park; 13th Division Prairie; Weir Prairie; Magnuson Park; Montlake Fill")
	ecoregion = QuerySelectField('Ecoregion',
            query_factory=lambda: Ecoregion.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:'{} - {}'.format(a.ecoregion_code, a.ecoregion_description))
	country = StringField('Country')
	continent = QuerySelectField('Continent',
            query_factory=lambda: Continent.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:a.continent_name)
	lat_sec = StringField('Lat Sec')
	lon_we = StringField('Lon WE')
	lat_ns = StringField('Lat NS')
	lon_min = StringField('Lon Min')
	lon_sec = StringField('Lon Sec')
	altitude = StringField('Altitude')
	lat_min = StringField('Lat Min')
	lat_deg = StringField('Lat Deg')
	lon_deg = StringField('Lon Deg')

	#Publication form
	source_type = QuerySelectField('Source Type',
            query_factory=lambda: SourceType.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:'{} - {}'.format(a.source_name, a.source_description))	
	authors = StringField('Publication Authors *', validators=[Required()], default="Neubert; Parker")
	editors = StringField('Publication Editors')
	pub_title = StringField('Jorunal/Publication Title (ie J Ecol) *', validators=[Required()], default="Risk Anal")
	journal_book_conf = StringField('Journal/Book Conf')
	year = IntegerField('Year Publication Published *', validators=[Required()], default=2004)
	volume = StringField('Journal/Publication Volume')
	pages  = StringField('Publication Pages')
	publisher = StringField('Publication Publisher')
	city = StringField('Publication City')
	country = StringField('Publication Country')
	institution = StringField('Publication Institution')
	DOI_ISBN = StringField('DOI/ISBN')
	pub_name = StringField('Publication Title')
	corresponding_author = StringField('Corresponding Author')
	email = StringField('Email Address', validators=[Email()])
	purposes = QuerySelectField('Purposes',
            query_factory=lambda: Purpose.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:'{} - {}'.format(a.purpose_name, a.purpose_description))
	embargo = DateField('Embargo')
	missing_data = QuerySelectField('Missing Data',
            query_factory=lambda: MissingData.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:'{} - {}'.format(a.missing_code, a.missing_description))
	additional_source_string = StringField('Additional Source')

	# Matrix
	treatment = StringField('Treatment *', validators=[Required()], default="Unmanipulated") #Fkey (not set) it's not set mate
	matrix_split = IntegerField('Matrix Split')
	matrix_composition = QuerySelectField('Matrix Composition *',
            query_factory=lambda: MatrixComposition.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:a.comp_name, validators=[Required()], default=1)
	survival_issue = DecimalField('Survival Issue')
	n_intervals = DecimalField('Number of Intervals')
	periodicity = IntegerField('Periodicity')
	matrix_criteria_size = IntegerField('Matrix Criteria Size')
	matrix_criteria_ontogeny = IntegerField('Matrix Criteria Ontogeny')
	matrix_criteria_age = IntegerField('Matrix Criteria Age')
	matrix_start = StringField('Matrix Start *', validators=[Required(), Regexp('^(\d{1}[/-]\d{1,4})*$', 0, 'Must be M/YYYY')], default="M/1994")
	matrix_end = StringField('Matrix End', validators=[Regexp('(?<=\[).+(?=\])', 0, 'Must be M/YYYY')])
	matrix_start_season = QuerySelectField('Matrix Start Season',
            query_factory=lambda: Season.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:'{} - {}'.format(a.season_id, a.season_name))
	matrix_end_season = QuerySelectField('Matrix End Season',
            query_factory=lambda: Season.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:'{} - {}'.format(a.season_id, a.season_name))
	matrix_fec = IntegerField('Matrix Fecundity')
	matrix_a_string = TextAreaField('Matrix String *', validators=[Required(), Regexp('^\[.*\]$', 0, 'Matrix must be a vector, contained within []')], \
		default="[0.73 0 6.4 95.7 274 447.2 4074 2e-05 0.54 0 0 0 0 0 0 0.17 0.64 0 0 0 0 0 0 0.27 0.66 0 0 0 0 0 0 0.19 0.64 0 0 0 0 0 0 0.32 0.64 0 0 0 0 0 0 0.31 0.96]") 
	# ^[0-9]+([,.][0-9]+)?$ Must be in specific format
	matrix_class_string = TextAreaField('Matrix Class Names String * (stages to be seperated by pipe |)', validators=[Required()], default="Seeds| Seedlings| Juveniles| Small adults: <100 g| Medium adults: 100''400 g| Large adults: 400''900 g| Extra-large adults: >900 g") #Must be in specific format
	n_plots = IntegerField('# Plots')
	plot_size = IntegerField('Plot Size')
	n_individuals = IntegerField('# Individuals')
	studied_sex = QuerySelectField('Studied Sex',
            query_factory=lambda: StudiedSex.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:'{} - {}'.format(a.sex_code, a.sex_description))
	captivity = QuerySelectField('Matrix Captivity',
            query_factory=lambda: Captivity.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:'{} - {}'.format(a.cap_code, a.cap_description))
	matrix_dimension = IntegerField('Matrix Dimension')
	observations = TextAreaField('Observations *', validators=[Required()], default="Invasion stage: edge")

	# Study Form
	study_duration = IntegerField('Study Duration')
	study_start = IntegerField('Study Start')
	study_end = IntegerField('Study End')

	def validate(self):
		if not validate_dimension(self.matrix_a_string.data, self.matrix_class_string.data):
			self.matrix_a_string.errors = list(self.matrix_a_string.errors)
			self.matrix_a_string.errors.append('Matrix A String Vector and Class Names do not validate.\
				Please ensure they are formatted correctly.')
			self.matrix_a_string.errors = tuple(self.matrix_a_string.errors)
			self.matrix_class_string.errors = list(self.matrix_class_string.errors)
			self.matrix_class_string.errors.append('Matrix A String Vector and Class Names do not validate.\
				Please ensure they are formatted correctly.')
			self.matrix_class_string.errors = tuple(self.matrix_class_string.errors)
			return False
		else:
			return True


	submit = SubmitField('Submit')






