class Entry:
	def __init__(self, publication, study, population, taxonomy, plant_trait, matrix):
		self.publication = publication
		self.study = study
		self.population = population
		self.taxonomy = taxonomy
		self.plant_trait = plant_trait
		self.matrix = matrix

	def __repr__(self):
		return '<Entry %r>' % vars(self)

class Taxonomy:
	def __init__(self, species_author, species_accepted, authority, tpl_version, taxonomic_status_id, infraspecies_accepted, species_epithet_accepted, genus_accepted, genus, family, tax_order, tax_class, phylum, kingdom):
		self.species_author = species_author
		self.species_accepted = species_accepted
		self.authority = authority
		self.tpl_version = tpl_version
		self.taxonomic_status_id = taxonomic_status_id
		self.infraspecies_accepted = infraspecies_accepted
		self.species_epithet_accepted = species_epithet_accepted
		self.genus_accepted = genus_accepted
		self.genus = genus
		self.family = family
		self.tax_order = tax_order
		self.tax_class = tax_class
		self.phylum = phylum
		self.kingdom = kingdom

	def __repr__(self):
		return '<Taxonomy %r>' % vars(self)


class Publication:
	def __init__(self, authors, year, DOI_ISBN, additional_source_string, taxonomy, population, plant_trait, study):
		self.authors = authors
		self.year = year
		self.DOI_ISBN = DOI_ISBN
		self.additional_source_string = additional_source_string
		self.taxonomy = taxonomy
		self.population = population
		self.plant_trait = plant_trait
		self.study = study
		# studies

	def __repr__(self):
		return '<Publication %r>' % vars(self)

class Population:
	def __init__(self, species_author, name, geometries_lat_min, geometries_lon_deg, geometries_lat_ns, geometries_lat_we, geometries_lat_sec, geometries_lon_sec, geometries_lon_min, geometries_lat_deg, geometries_altitude, ecoregion_id, country, continent_id, matrix):
		self.species_author = species_author
		self.name = name
		self.ecoregion_id = ecoregion_id
		self.country = country
		self.continent_id = continent_id
		self.geometries = {'lat_min' : geometries_lat_min, 'lon_deg': geometries_lon_deg, 'lat_ns': geometries_lat_ns, 'lat_we': geometries_lat_we, 'lat_sec' : geometries_lat_sec, 'lon_sec' : geometries_lon_sec, 'lon_min' : geometries_lon_min, 'lat_deg' : geometries_lat_deg, 'altitude' : geometries_altitude}
		self.matrix = matrix

	def __repr__(self):
		return '<Population %r>' % vars(self)

class PlantTrait:
	def __init__(self, growth_type_id, dicot_monoc_id, angio_gymno_id):
		self.growth_type_id = growth_type_id
		self.dicot_monoc_id = dicot_monoc_id
		self.angio_gymno_id = angio_gymno_id

	def __repr__(self):
		return '<Plant Trait %r>' % vars(self)

class Matrix:
	def __init__(self, treatment_id, matrix_split, matrix_composition_id, survival_issue, periodicity, matrix_criteria_size, matrix_criteria_ontogeny, matrix_criteria_age, matrix_start_month, matrix_start_year, matrix_end_month, matrix_end_year, matrix_start_season_id, matrix_end_season_id, matrix_fec, matrix_a_string, matrix_class_string, studied_sex_id, captivity_id, matrix_dimension, observations):
		self.treatment_id = treatment_id
		self.matrix_split = matrix_split
		self.matrix_composition_id = matrix_composition_id
		self.survival_issue = survival_issue
		self.periodicity = periodicity
		self.matrix_criteria_size = matrix_criteria_size
		self.matrix_criteria_ontogeny = matrix_criteria_ontogeny
		self.matrix_criteria_age = matrix_criteria_age
		self.matrix_start = {'matrix_start_month': matrix_start_month, 'matrix_start_year': matrix_start_year}
		self.matrix_end = {'matrix_end_month': matrix_end_month, 'matrix_end_year': matrix_end_year}
		self.matrix_start_season_id = matrix_start_season_id
		self.matrix_end_season_id = matrix_end_season_id
		self.matrix_fec = matrix_fec
		self.matrix_a_string = matrix_a_string
		self.matrix_class_string = matrix_class_string
		self.studied_sex_id = studied_sex_id
		self.captivity_id = captivity_id
		self.matrix_dimension = matrix_dimension
		self.observations = observations
	
	def __repr__(self):
			return '<Matrix %r>' % vars(self)

class Study:
	def __init__(self, study_duration, study_start, study_end):
		self.study_duration = study_duration
		self.study_start = study_start
		self.study_end = study_end

	def __repr__(self):
			return '<Study %r>' % vars(self)



