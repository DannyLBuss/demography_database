from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField, DecimalField, IntegerField, DateField,\
    FormField
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError
from flask.ext.pagedown.fields import PageDownField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from ..models import IUCNStatus, ESAStatus, TaxonomicStatus, GrowthType, GrowthFormRaunkiaer, ReproductiveRepetition, \
    DicotMonoc, AngioGymno, SourceType, Database, Purpose, MissingData, ContentEmail, Ecoregion, Continent, StageTypeClass, \
    TransitionType, MatrixComposition, Season, StudiedSex, Captivity, Species, Taxonomy, PlantTrait, \
    Publication, Study, AuthorContact, AdditionalSource, Population, Stage, StageType, Treatment, TreatmentType, \
    MatrixStage, MatrixValue, Matrix, Interval, Fixed, VectorAvailability, StageClassInfo, Small

# THE SUPERFORM
class SpeciesForm(Form):
	species_accepted = StringField('Species Accepted *', validators=[Required(), Length(1, 64)])
	iucn_status = QuerySelectField('IUCN Status',
            query_factory=lambda: IUCNStatus.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:'{} - {} ({})'.format(a.status_code, a.status_name, a.status_description))
	esa_status = QuerySelectField('ESA Status',
            query_factory=lambda: ESAStatus.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:'{} - {}'.format(a.status_code, a.status_name))
	invasive_status = BooleanField('Invasive Status')

	submit = SubmitField('Submit')

class TaxonomyForm(Form):
	species_author = StringField('Species Author *', validators=[Required(), Length(1, 64)])
	authority = StringField('Authority', validators=[Length(1, 64)])
	taxonomic_status = QuerySelectField('Taxonomic Status',
            query_factory=lambda: TaxonomicStatus.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:'{} - {}'.format(a.status_name, a.status_description))
	tpl_version = DecimalField('TPL Version')
	infraspecies_accepted = StringField('Infraspecies Accepted', validators=[Length(1, 64)])
	species_epithet_accepted = StringField('Species Epithet Accepted', validators=[Length(1, 64)])
	genus_accepted = StringField('Genus Accepted', validators=[Length(1, 64)])
	genus = StringField('Genus', validators=[Length(1, 64)])
	family = StringField('Family', validators=[Length(1, 64)])
	tax_order = StringField('Order', validators=[Length(1, 64)])
	tax_class = StringField('Class', validators=[Length(1, 64)])
	phylum = StringField('Phylum', validators=[Length(1, 64)])
	kingdom = StringField('Kingdom', validators=[Length(1, 64)])

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
	email = StringField('Email Address', validators=[Email()])
	purposes = QuerySelectField('Purposes',
            query_factory=lambda: Purpose.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:'{} - {}'.format(a.purpose_name, a.purpose_description))
	embargo = DateField('Embargo')
	missing_data = QuerySelectField('Missing Data',
            query_factory=lambda: MissingData.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:'{} - {}'.format(a.missing_code, a.missing_description))
	additional_source_string = StringField('Additional Source')
	# author_contacts # Fkey
	# additional_sources # Fkey	

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

class PlantTraitForm(Form):
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

class MatrixForm(Form):
	treatment = StringField('Treatment *', validators=[Required()]) #Fkey (not set)
	matrix_split = IntegerField('Matrix Split')
	matrix_composition = QuerySelectField('Matrix Composition *',
            query_factory=lambda: MatrixComposition.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:a.comp_name, validators=[Required()])
	survival_issue = DecimalField('Survival Issue')
	n_intervals = DecimalField('Number of Intervals')
	periodicity = IntegerField('Periodicity')
	matrix_criteria_size = IntegerField('Matrix Criteria Size')
	matrix_criteria_ontogeny = IntegerField('Matrix Criteria Ontogeny')
	matrix_criteria_age = IntegerField('Matrix Criteria Age')
	matrix_start = StringField('Matrix Start *', validators=[Required(), Regexp('^(\d{1}[/-]\d{1,4})*$', 0, 'Must be M/YYYY')])
	matrix_end = StringField('Matrix End')
	matrix_start_season = QuerySelectField('Matrix Start Season',
            query_factory=lambda: Season.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:'{} - {}'.format(a.season_id, a.season_name))
	matrix_end_season = QuerySelectField('Matrix End Season',
            query_factory=lambda: Season.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:'{} - {}'.format(a.season_id, a.season_name))
	matrix_fec = IntegerField('Matrix Fecundity')
	matrix_a_string = TextAreaField('Matrix String *', validators=[Required()]) #Must be in specific format
	matrix_class_string = TextAreaField('Matrix Class Names String *', validators=[Required()]) #Must be in specific format
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
	observations = TextAreaField('Observations *', validators=[Required()])

class EntryForm(Form):
	# Species
	species_accepted = StringField('Species Accepted *', validators=[Required(), Length(1, 64)])
	iucn_status = QuerySelectField('IUCN Status',
            query_factory=lambda: IUCNStatus.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:'{} - {} ({})'.format(a.status_code, a.status_name, a.status_description))
	esa_status = QuerySelectField('ESA Status',
            query_factory=lambda: ESAStatus.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:'{} - {}'.format(a.status_code, a.status_name))
	invasive_status = BooleanField('Invasive Status')

	# Taxonomy
	species_author = StringField('Species Author *', validators=[Required(), Length(1, 64)])
	authority = StringField('Authority', validators=[Length(1, 64)])
	taxonomic_status = QuerySelectField('Taxonomic Status',
            query_factory=lambda: TaxonomicStatus.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:'{} - {}'.format(a.status_name, a.status_description))
	tpl_version = DecimalField('TPL Version')
	infraspecies_accepted = StringField('Infraspecies Accepted', validators=[Length(1, 64)])
	species_epithet_accepted = StringField('Species Epithet Accepted', validators=[Length(1, 64)])
	genus_accepted = StringField('Genus Accepted', validators=[Length(1, 64)])
	genus = StringField('Genus', validators=[Length(1, 64)])
	family = StringField('Family', validators=[Length(1, 64)])
	tax_order = StringField('Order', validators=[Length(1, 64)])
	tax_class = StringField('Class', validators=[Length(1, 64)])
	phylum = StringField('Phylum', validators=[Length(1, 64)])
	kingdom = StringField('Kingdom', validators=[Length(1, 64)])

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

	#Publication form
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
	treatment = StringField('Treatment *', validators=[Required()]) #Fkey (not set)
	matrix_split = IntegerField('Matrix Split')
	matrix_composition = QuerySelectField('Matrix Composition *',
            query_factory=lambda: MatrixComposition.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:a.comp_name, validators=[Required()])
	survival_issue = DecimalField('Survival Issue')
	n_intervals = DecimalField('Number of Intervals')
	periodicity = IntegerField('Periodicity')
	matrix_criteria_size = IntegerField('Matrix Criteria Size')
	matrix_criteria_ontogeny = IntegerField('Matrix Criteria Ontogeny')
	matrix_criteria_age = IntegerField('Matrix Criteria Age')
	matrix_start = StringField('Matrix Start *', validators=[Required(), Regexp('^(\d{1}[/-]\d{1,4})*$', 0, 'Must be M/YYYY')])
	matrix_end = StringField('Matrix End', validators=[Regexp('(?<=\[).+(?=\])', 0, 'Must be M/YYYY')])
	matrix_start_season = QuerySelectField('Matrix Start Season',
            query_factory=lambda: Season.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:'{} - {}'.format(a.season_id, a.season_name))
	matrix_end_season = QuerySelectField('Matrix End Season',
            query_factory=lambda: Season.query.all(), get_pk=lambda a: a.id,
                            get_label=lambda a:'{} - {}'.format(a.season_id, a.season_name))
	matrix_fec = IntegerField('Matrix Fecundity')
	matrix_a_string = TextAreaField('Matrix String *', validators=[Required(), Regexp('^\[.*\]$', 0, 'Matrix must be a vector, contained within []')]) #Must be in specific format
	matrix_class_string = TextAreaField('Matrix Class Names String * (stages to be seperated by pipe |)', validators=[Required()]) #Must be in specific format
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
	observations = TextAreaField('Observations *', validators=[Required()])

	# Study Form
	study_duration = IntegerField('Study Duration')
	study_start = IntegerField('Study Start')
	study_end = IntegerField('Study End')

	submit = SubmitField('Submit')
	









