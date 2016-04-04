import csv

def convert_all_headers(dict):
    new_dict = {}
    new_dict['additional_source_string'] = dict['AdditionalSource']
    new_dict['matrix_end_season_id'] = dict['MatrixEndSeason']
    new_dict['growth_type_id'] = dict['GrowthType']
    new_dict['geometries_lat_sec'] = dict['LatSec']
    new_dict['study_duration'] = dict['StudyDuration']
    # new_dict['matrix_values_c'] = dict['matrixC']
    new_dict['geometries_lat_we'] = dict['LonWE']
    new_dict['infraspecies_accepted'] = dict['InfraspecificAccepted']
    # new_dict['matrix_values_a'] = dict['matrixA']
    # new_dict['matrix_a_string'] = dict['matrixA']
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
    # new_dict['matrix_values_a'] = dict['matrixF']
    new_dict['matrix_start_season_id'] = dict['MatrixStartSeason']
    new_dict['populations_name'] = dict['MatrixPopulation']
    new_dict['species_author'] = dict['SpeciesAuthor']
    new_dict['tax_class'] = dict['Class']
    new_dict['continent_id'] = dict['Continent']
    new_dict['treatment_id'] = dict['MatrixTreatment']
    new_dict['matrix_class_string'] = dict['Classes']
    new_dict['phylum'] = dict['Phylum']
    new_dict['tpl_version'] = dict['TPLVersion']
    new_dict['matrix_criteria_age'] = dict['CriteriaAge']
    new_dict['study_end'] = dict['StudyEnd']
    new_dict['captivity_id'] = dict['MatrixCaptivity']
    new_dict['ecoregion_id'] = dict['Ecoregion']
    new_dict['matrix_values_a'] = dict['PPMS']
    new_dict['authority'] = dict['Authority']
    new_dict['matrix_split'] = dict['MatrixSplit']
    new_dict['seasonal'] = dict['Seasonal']
    new_dict['seasonal'] = dict['Seasonal']
    new_dict['doi_season'] = dict['DOISeason']
    new_dict['id'] = dict['ID']

    return new_dict


f = open("app/compadre/danny.csv", "rU")
input_file = csv.DictReader(f)


output_file = open("app/compadre/danny_2.csv", "rU")
input_file_2 = csv.DictReader(output_file)

dois = {}
all_data = []

for i, row in enumerate(input_file):
	data = convert_all_headers(row)
	pub_doi = data['DOI_ISBN']
	
	if pub_doi in dois:
		if data['seasonal'] == "TRUE":
			dois[pub_doi] += 1

	else:
		dois[pub_doi] = 0
		if data['seasonal'] == "TRUE":
			dois[pub_doi] += 1


for i, r in enumerate(input_file_2):
	data = convert_all_headers(r)
	publ_doi = data['DOI_ISBN']

	if publ_doi in dois:
		d_count = int(dois[publ_doi])

		if d_count > 0:
			array = [data['id'], data['DOI_ISBN'], True, data['seasonal']]
		else:
			array = [data['id'], data['DOI_ISBN'], False, data['seasonal']]

	all_data.append(array)


print all_data

with open('app/compadre/seasonal_corrected.csv', 'w') as fp:
    a = csv.writer(fp, delimiter=',')
    a.writerows(all_data)

print "DONE"













