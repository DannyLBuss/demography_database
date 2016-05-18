class Entry:
	def __init__(self, publication, study, population, taxonomy, plant_trait, matrix):
		self.publication = publication
		self.study = study
		self.population = population
		self.taxonomy = taxonomy
		self.plant_trait = plant_trait
		self.matrix = matrix

	# Submit to the database
	def submit_to_database(self):
	    import json, re

	    ''' Species '''
	    species = Species.query.filter_by(species_accepted=self.taxonomy.species_accepted).first()
	    if species == None:
	        species = Species(species_accepted=self.taxonomy.species_accepted)
	    db.session.add(species)
	    db.session.commit()

	    ''' Publication '''
	    publication = Publication.query.filter_by(DOI_ISBN=self.publication.DOI_ISBN).first()
	    if publication == None:
	        publication = Publication()
	        publication.authors = self.publication.authors
	        publication.year = self.publication.year
	        publication.DOI_ISBN = self.publication.DOI_ISBN
	        publication.additional_source_string = self.publication.additional_source_string
	        publication.pub_title = self.publication.pub_name
	        db.session.add(publication)
	        db.session.commit()

	    ''' Plant Trait '''
	    trait = PlantTrait.query.filter_by(species_id=species.id).first()
	    if trait == None:
	        trait = PlantTrait()
	        growth_type = GrowthType.query.filter_by(type_name=self.plant_trait.growth_type_id).first()
	        if growth_type != None:
	            trait.growth_type_id = growth_type.id
	        dicot_monoc = DicotMonoc.query.filter_by(dicot_monoc_name=self.plant_trait.dicot_monoc_id).first()
	        if dicot_monoc != None:
	            trait.dicot_monoc_id = dicot_monoc.id
	        angio_gymno = AngioGymno.query.filter_by(angio_gymno_name=self.plant_trait.angio_gymno_id).first()
	        if angio_gymno != None:
	            trait.angio_gymno_id = angio_gymno.id
	        trait.species_id = species.id
	        db.session.add(trait)
	        db.session.commit()

	    ''' Study '''
	    study = Study.query.filter_by(publication_id=publication.id, study_start=self.study.study_start, study_end=self.study.study_end).first()
	    if study == None:
	        study = Study()
	        if self.study.study_duration != 'NA':
	            study.study_duration = self.study.study_duration

	        if self.study.study_start != 'NA':
	            study.study_start = self.study.study_start

	        if self.study.study_end != 'NA':
	            study.study_end = self.study.study_end

	        study.publication_id = publication.id
	        db.session.add(study)
	        db.session.commit()

	    ''' Population '''
	    pop = Population.query.filter_by(geometries=json.dumps(self.population.geometries), species_id=species.id, publication_id=publication.id).first()
	    if pop == None:
	        pop = Population()
	        pop.species_author = self.population.species_author
	        pop.name = self.population.name.encode('utf-8')   
	        ecoregion = Ecoregion.query.filter_by(ecoregion_code=self.population.ecoregion_id).first()
	        if ecoregion != None:
	            pop.ecoregion_id = ecoregion.id
	        pop.country = self.population.country    
	        continent = Continent.query.filter_by(continent_name=self.population.continent_id).first()
	        if continent != None:
	            pop.continent_id = continent.id
	        pop.geometries = json.dumps(self.population.geometries)
	        pop.species_id = species.id
	        pop.publication_id = publication.id
	        pop.study_id = study.id
	        db.session.add(pop)
	        db.session.commit()

	    ''' Taxonomy '''
	    tax = Taxonomy.query.filter_by(species_id=species.id).first()
	    if tax == None:
	        tax = Taxonomy()
	        tax.species_author = self.taxonomy.species_author
	        tax.species_accepted = self.taxonomy.species_accepted
	        tax.authority = self.taxonomy.authority
	        tax.tpl_version = self.taxonomy.tpl_version    
	        tax_status = TaxonomicStatus.query.filter_by(status_name=self.taxonomy.taxonomic_status_id).first()
	        if tax_status != None:
	            tax.taxonomic_status_id = tax_status.id
	        tax.infraspecies_accepted = self.taxonomy.infraspecies_accepted
	        tax.species_epithet_accepted = self.taxonomy.species_epithet_accepted
	        tax.genus_accepted = self.taxonomy.genus_accepted
	        tax.genus = self.taxonomy.genus
	        tax.family = self.taxonomy.family
	        tax.tax_order = self.taxonomy.tax_order
	        tax.tax_class = self.taxonomy.tax_class
	        tax.phylum = self.taxonomy.phylum
	        tax.kingdom = self.taxonomy.kingdom
	        tax.species_id = species.id
	        tax.publication_id = publication.id
	        db.session.add(tax)
	        db.session.commit()

	    ''' Matrix '''
	    matrix = Matrix()
	    treatment_type = TreatmentType.query.filter_by(type_name=self.matrix.treatment_id).first()
	    if treatment_type == None:
	        treatment_type = TreatmentType(type_name=self.matrix.treatment_id)
	        db.session.add(treatment_type)
	        db.session.commit()
	    matrix.treatment_id = treatment_type.id
	    matrix.treatment_type_id = treatment_type.id
	    matrix.matrix_split = coerce_boolean(self.matrix.matrix_split)
	    comp_id = MatrixComposition.query.filter_by(comp_name=self.matrix.matrix_composition_id).first()
	    if comp_id != None:
	        matrix.matrix_composition_id = comp_id.id  

	    if self.matrix.survival_issue != 'NA':  
	        matrix.survival_issue = float(self.matrix.survival_issue)
	    
	    matrix.periodicity = self.matrix.periodicity
	    matrix.matrix_criteria_size = coerce_boolean(self.matrix.matrix_criteria_size)
	    matrix.matrix_criteria_ontogeny = coerce_boolean(self.matrix.matrix_criteria_ontogeny)
	    matrix.matrix_criteria_age = coerce_boolean(self.matrix.matrix_criteria_age) 
	    matrix.matrix_start = coerce_date(self.matrix.matrix_start, 'start') #Coerced into date conidering NA
	    matrix.matrix_end = coerce_date(self.matrix.matrix_end , 'end') #Coerced into date considering NA
	    start_id = Season.query.filter_by(season_name=self.matrix.matrix_start_season_id).first()


	    if self.matrix.matrix_start_season_id != 'NA':
	        try:
	            start_id = Season.query.filter_by(season_id=int(self.matrix.matrix_start_season_id)).first()
	        except ValueError:
	            pass

	    if start_id != None:
	        matrix.matrix_start_season_id = start_id.id

	    if self.matrix.matrix_end_season_id != 'NA':
	        try:
	            end_id = Season.query.filter_by(season_id=int(self.matrix.matrix_end_season_id)).first()
	        except ValueError:
	            pass
	    
	    end_id = Season.query.filter_by(season_name=self.matrix.matrix_end_season_id).first()
	    if end_id != None:
	        matrix.matrix_end_season_id = end_id.id
	        
	    matrix.matrix_fec = coerce_boolean(self.matrix.matrix_fec)
	    matrix.matrix_a_string = self.matrix.matrix_a_string
	    matrix.matrix_class_string = self.matrix.matrix_class_string
	    sex_id = StudiedSex.query.filter_by(sex_code=self.matrix.studied_sex_id).first()
	    if sex_id != None:
	        matrix.studied_sex_id = sex_id.id
	    cap_id = Captivity.query.filter_by(cap_code=self.matrix.captivity_id).first()
	    if cap_id != None:
	        matrix.captivity_id = cap_id.id
	    matrix.matrix_dimension = int(self.matrix.matrix_dimension)
	    matrix.observations = self.matrix.observations
	    matrix.population_id = pop.id
	    matrix.study_id = study.id
	    db.session.add(matrix)   
	    db.session.commit()
	    matrix.create_uid()

	    return 

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
	def __init__(self, authors, year, DOI_ISBN, additional_source_string, taxonomy, population, plant_trait, study, pub_name):
		self.authors = authors
		self.year = year
		self.DOI_ISBN = DOI_ISBN
		self.additional_source_string = additional_source_string
		self.taxonomy = taxonomy
		self.population = population
		self.plant_trait = plant_trait
		self.study = study
		self.pub_name = pub_name
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

class Species:
	def __init__(self, name):
		self.name = name

	def __repr__(self):
		return '<Species %r>' % vars(self)



