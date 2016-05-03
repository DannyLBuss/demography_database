#!/usr/bin/python
# -*- coding: utf-8 -*-
import hashlib
from difflib import SequenceMatcher

salsola = { 
	"species_author" : "Salsola_australis", 
	"authority" : "L.", 
	"taxanomic_status" : "Synonym", 
	"growth_type" : "Annual", 
	"authors" : "Borger; Scott; Renton; Walsh; Powles", 
	"journal" : "Weed Res", 
	"year_pub" : "2009", 
	"doi_isbn" : "10.1111/j.1365-3180.2009.00703.x",
	"additional_source" : "NA",
	"study_duration" : "3", 
	"study_start" : "2004" , 
	"study_end" : "2006", 
	"annual_peroid" : "2", 
	"number_populations" : "NA", 
	"criteria_size" : "NA", 
	"criteria_ontogeny" : "NA", 
	"criteria_age" : "NA", 
	"matrix_population" : "NA", 
	"ecoregion" : "MED", 
	"matrix_composite" : "Mean", 
	"matrix_treatment" : "Unmanipulated", 
	"matrix_start_year" : "2004", 
	"matrix_start_month" : "NA", 
	"matrix_end_year" : "2006", 
	"matrix_end_month" : "NA", 
	"matrix_split" : "Divided", 
	"observation" : "NA", 
	"matrix_dimension" : "7", 
	"survival_issue" : "0.974", 
	"classnames" : "NA",
	"growth_type_2" : "Trees",
	"vector_y_n" : "1",
	"completed" : "Complete",
	"notes" : "NA",
	"availability_stage" : "SN",
	"availability_notes" : 	"NA",
	"population_info" : "NA",

}

aspasia = { 
	"species_author" : "Aspasia_principissa", 
	"authority" : "Rchb.f.", 
	"taxanomic_status" : "Accepted", 
	"growth_type" : "Epiphyte", 
	"authors" : "Zotz; Schmidt", 
	"journal" : "Biol Cons", 
	"year_pub" : "2006", 
	"doi_isbn" : "10.1016/j.biocon.2005.07.022",
	"additional_source" : "Ellis Ecol 2013; Ellis J Ecol 2013",
	"study_duration" : "8", 
	"study_start" : "1997" , 
	"study_end" : "2004", 
	"annual_peroid" : "1", 
	"number_populations" : "1", 
	"criteria_size" : "Yes", 
	"criteria_ontogeny" : "No", 
	"criteria_age" : "No", 
	"matrix_population" : "Barro Colorado Island", 
	"ecoregion" : "TMB", 
	"matrix_composite" : "Mean", 
	"matrix_treatment" : "Unmanipulated", 
	"matrix_start_year" : "1997", 
	"matrix_start_month" : "NA", 
	"matrix_end_year" : "2004", 
	"matrix_end_month" : "NA", 
	"matrix_split" : "Divided", 
	"observation" : "NA", 
	"matrix_dimension" : "7", 
	"survival_issue" : "0.93", 
	"classnames" : "NA",
	"growth_type_2" : "Shrubs",
	"vector_y_n" : "1",
	"completed" : "Complete",
	"notes" : "NA",
	"availability_stage" : "M, SN",
	"availability_notes" : 	"90 study sites & 7 years data all pooled together",
	"population_info" : "NA",

}

catopsis_1 = { 
	"species_author" : "Catopsis_compacta", 
	"authority" : "Mez", 
	"taxanomic_status" : "Accepted", 
	"growth_type" : "Epiphyte", 
	"authors" : "del Castillo; Trujillo-Argueta; Rivera-Garcia; G_mez-Ocampo; Mondrag_n-Chaparro",
	"journal" : "Ecol and Evol", 
	"year_pub" : "2013", 
	"doi_isbn" : "10.1002/ece3.765",
	"additional_source" : "NA",
	"study_duration" : "4", 
	"study_start" : "2005" , 
	"study_end" : "2008", 
	"annual_peroid" : "1", 
	"number_populations" : "1", 
	"criteria_size" : "Yes", 
	"criteria_ontogeny" : "Yes", 
	"criteria_age" : "No", 
	"matrix_population" : "Santa Catarina", 
	"ecoregion" : "TSC", 
	"matrix_composite" : "Individual", 
	"matrix_treatment" : "Unmanipulated", 
	"matrix_start_year" : "2005", 
	"matrix_start_month" : "NA", 
	"matrix_end_year" : "2006", 
	"matrix_end_month" : "NA", 
	"matrix_split" : "Divided", 
	"observation" : "Stage 1-4 cannot be sexed, Stage 5 (adult) is only female", 
	"matrix_dimension" : "5", 
	"survival_issue" : "0.934", 
	"classnames" : "NA",
	"growth_type_2" : "Forest Herbs",
	"vector_y_n" : "1",
	"completed" : "NA",
	"notes" : "NA",
	"availability_stage" : "SN",
	"availability_notes" : 	"All available stage data had zero for seedlings",
	"population_info" : "NA",

}

catopsis_2 = { 
	"species_author" : "Catopsis_compacta", 
	"authority" : "Mez", 
	"taxanomic_status" : "Accepted", 
	"growth_type" : "Epiphyte", 
	"authors" : "del Castillo; Trujillo-Argueta; Rivera-Garcia; G_mez-Ocampo; Mondrag_n-Chaparro", 
	"journal" : "Ecol and Evol", 
	"year_pub" : "2013", 
	"doi_isbn" : "10.1002/ece3.765",
	"additional_source" : "NA",
	"study_duration" : "4", 
	"study_start" : "2005" , 
	"study_end" : "2008", 
	"annual_peroid" : "1", 
	"number_populations" : "1", 
	"criteria_size" : "Yes", 
	"criteria_ontogeny" : "Yes", 
	"criteria_age" : "No", 
	"matrix_population" : "Santa Catarina", 
	"ecoregion" : "TSC", 
	"matrix_composite" : "Individual", 
	"matrix_treatment" : "Unmanipulated", 
	"matrix_start_year" : "2006", 
	"matrix_start_month" : "NA", 
	"matrix_end_year" : "2007", 
	"matrix_end_month" : "NA", 
	"matrix_split" : "Divided", 
	"observation" : "Stage 1-4 cannot be sexed, Stage 5 (adult) is only female", 
	"matrix_dimension" : "5", 
	"survival_issue" : "0.933", 
	"classnames" : "NA",
	"growth_type_2" : "Open Herbs",
	"vector_y_n" : "1",
	"completed" : "NA",
	"notes" : "NA",
	"availability_stage" : "SN",
	"availability_notes" : 	"All available stage data had zero for seedlings",
	"population_info" : "NA",

}

catopsis_3 = { 
	"species_author" : "Catopsis_compacta", 
	"authority" : "Mez", 
	"taxanomic_status" : "Accepted", 
	"growth_type" : "Epiphyte", 
	"authors" : "del Castillo; Trujillo-Argueta; Rivera-Garcia; G_mez-Ocampo; Mondrag_n-Chaparro", 
	"journal" : "Ecol and Evol", 
	"year_pub" : "2013", 
	"doi_isbn" : "10.1002/ece3.765",
	"additional_source" : "NA",
	"study_duration" : "4", 
	"study_start" : "2005" , 
	"study_end" : "2008", 
	"annual_peroid" : "1", 
	"number_populations" : "1", 
	"criteria_size" : "Yes", 
	"criteria_ontogeny" : "Yes", 
	"criteria_age" : "No", 
	"matrix_population" : "Santa Catarina", 
	"ecoregion" : "TSC", 
	"matrix_composite" : "Individual", 
	"matrix_treatment" : "Unmanipulated", 
	"matrix_start_year" : "2007", 
	"matrix_start_month" : "NA", 
	"matrix_end_year" : "2008", 
	"matrix_end_month" : "NA", 
	"matrix_split" : "Divided", 
	"observation" : "Stage 1-4 cannot be sexed, Stage 5 (adult) is only female", 
	"matrix_dimension" : "5", 
	"survival_issue" : "1", 
	"classnames" : "NA",
	"growth_type_2" : "Monocarpic Perennial",
	"vector_y_n" : "1",
	"completed" : "NA",
	"notes" : "NA",
	"availability_stage" : "SN",
	"availability_notes" : 	"All available stage data had zero for seedlings",
	"population_info" : "NA",

}

def return_con(obj):
	return ''.join([value for key, value in obj.items()])

def similar(a, b):
	return SequenceMatcher(None, a, b).ratio()

species = [return_con(salsola), return_con(aspasia), return_con(catopsis_1), return_con(catopsis_2), return_con(catopsis_3)]

species_hashed = []

for s in species:
	hashed = hashlib.md5(s).hexdigest()
	species_hashed.append(hashed)

print "Salsola_australis vs Aspasia_principissa unhashed: ", similar(species[0], species[1])
print "Salsola_australis vs Aspasia_principissa hashed: ", similar(species_hashed[0], species_hashed[1])
print "-----"
print "Catopsis_compacta 2005-2006 vs Catopsis_compacta 2006-2007 unhashed:", similar(species[2], species[3])
print "Catopsis_compacta 2005-2006 vs Catopsis_compacta 2006-2007 hashed:", similar(species_hashed[2], species_hashed[3])
print "-----"
print "Catopsis_compacta 2006-2007 vs Catopsis_compacta 2007-2008 unhashed:", similar(species[3], species[4])
print "Catopsis_compacta 2006-2007 vs Catopsis_compacta 2007-2008 hashed:", similar(species_hashed[3], species_hashed[4])
print "-----"
print "Catopsis_compacta 2005-2006 vs Catopsis_compacta 2007-2008 unhashed:", similar(species[2], species[4])
print "Catopsis_compacta 2005-2006 vs Catopsis_compacta 2007-2008 hashed:", similar(species_hashed[2], species_hashed[4])

