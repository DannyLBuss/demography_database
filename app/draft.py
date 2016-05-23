''' Species '''
dict['SpeciesAccepted']
dict['IUCNStatus']
dict['ESAStatus']
dict['InvasiveStatus']
dict['SpeciesAuthor']
# taxonomies
# plant_traits
# populations
# stages

species_accepted
iucn_status # Fkey
esa_status # Fkey
invasive_status # Boolean
user_created # Fkey
user_created_id # Fkey
user_modified # Fkey
user_modified_id # Fkey
taxonomies # Fkey
plant_traits # Fkey
populations # Fkey
stages # Fkey


''' Taxonomy '''
dict['SpeciesAccepted']
dict['Kingdom']
dict['SpeciesEpithetAccepted']
dict['TaxonomicStatus']
dict['GenusAccepted']
dict['Family']
dict['Phylum']
dict['TPLVersion']
dict['InfraspecificAccepted']
dict['Genus']
dict['Order']
dict['Class']
dict['Authority']

species # Fkey
publication # Fkey
species_author
species_accepted
authority
taxonomic_status # Fkey
tpl_version
infraspecies_accepted
species_epithet_accepted
genus_accepted
genus
family
tax_order
tax_class
phylum
kingdom

''' Publication '''

source_type # FKey
authors
editors
pub_title
journal_book_conf
year
volume
pages
publisher
city
country
institution
DOI_ISBN
name
corresponding_author
email
purposes # Fkey
embargo # Date
missing_data # Fkey
additional_source_string

user_created # Fkey
user_modified # Fkey

author_contacts # Fkey
additional_sources # Fkey
populations #Fkey
stages #Fkey
treatments #Fkey
taxonomies #Fkey
studies #Fkey


dict['AdditionalSource']
dict['Journal']
dict['DOI.ISBN']
dict['Authors']
dict['YearPublication']

''' Study '''
publication #Fkey
study_duration 
study_start 
study_end 

matrices # Fkey
populations #Fkey
number_populations #could verify with populations.count()

dict['StudyDuration']
dict['StudyStart']
dict['StudyEnd']
dict['NumberPopulations']

''' Population '''
species #Fkey
publication #Fkey
study #Fkey
species_author
name 
ecoregion #Fkey
country
continent #Fkey
geometries #Object
matrices #Fkey

dict['MatrixPopulation']
dict['LatSec']
dict['LonWE']
dict['LatNS']
dict['LonMin']
dict['LonSec']
dict['Altitude']
dict['LatMin']
dict['Country']
dict['LatDeg']
dict['LonDeg']
dict['Continent']
dict['Ecoregion']

''' Plant Traits '''
species #Fkey
max_height
growth_type #Fkey
growth_form_raunkiaer #Fkey
reproductive_repetition #Fkey
dicot_monoc #Fkey
angio_gymno #Fkey

dict['GrowthType']
dict['DicotMonoc']
dict['AngioGymno']

''' Matrix '''
uid # Generated
population # Fkey
treatment #Fkey (not set)
matrix_split
matrix_composition #Fkey
survival_issue
n_intervals 
periodicity 
matrix_criteria_size
matrix_criteria_ontogeny
matrix_criteria_age
study # Fkey
matrix_start 
matrix_end 
matrix_start_season_id #Fkey
matrix_end_season_id #Fkey
matrix_end_season #Fkey
matrix_fec
matrix_a_string 
matrix_class_string
n_plots 
plot_size
n_individuals
studied_sex #Fkey
captivity #Fkey
matrix_dimension
observations

intervals #Fkey
matrix_values #Fkey
matrix_stages #Fkey
fixed #Fkey
seeds #Fkey

dict['MatrixEndSeason']
dict['matrixC']
dict['matrixA']
dict['matrixA']
dict['MatrixStartYear']
dict['MatrixFec']
dict['CriteriaSize']
dict['MatrixStartMonth']
dict['MatrixDimension']
dict['Observation']
dict['SurvivalIssue']
dict['CriteriaOntogeny']
dict['AnnualPeriodicity']
dict['MatrixEndYear']
dict['StudiedSex']
dict['MatrixEndMonth']
dict['MatrixComposite']
dict['matrixF']
dict['MatrixStartSeason']
dict['MatrixTreatment']
dict['classnames']
dict['CriteriaAge']
dict['MatrixCaptivity']
dict['matrixU']
dict['MatrixSplit']