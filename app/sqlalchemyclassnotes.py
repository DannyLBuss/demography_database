>>> from sqlalchemy.orm.query import Query
>>>

>>> class VersionQuery(Query):
...     def __iter__(self):
...             return Query.__iter__(self.original())
...     def original(self):
...             mzero = self._mapper_zero()
...             if mzero is not None:
...                     # crit = mzero.class_.version.version_number == 0
...                     return self.enable_assertions(False).filter(Version.version_number == 0)
...             else:
...                     return self
... 

>>> from sqlalchemy import *
>>> from sqlalchemy.orm import *
>>> from sqlalchemy.ext.declarative import declarative_base
>>> Base = declarative_base()
>>> 
>>> engine = create_engine('mysql://root:jeh5t@localhost/demog_compadre', echo=True)
>>> Base.metadata.create_all(engine)
>>> Session = sessionmaker(bind=engine, query_cls=VersionQuery)
>>> sess = Session()
>>> species = sess.query(Species).filter_by(species_accepted='Alaria nana').original()

>>> for s in species:
...     s
... 
2016-12-16 14:35:36,347 INFO sqlalchemy.engine.base.Engine BEGIN (implicit)
2016-12-16 14:35:36,351 INFO sqlalchemy.engine.base.Engine SELECT species.id AS species_id, species.species_accepted AS species_species_accepted, species.species_common AS species_species_common, species.iucn_status_id AS species_iucn_status_id, species.esa_status_id AS species_esa_status_id, species.invasive_status AS species_invasive_status, species.gbif_taxon_key AS species_gbif_taxon_key, species.image_path AS species_image_path, species.image_path2 AS species_image_path2 
FROM species, versions 
WHERE species.species_accepted = %s AND versions.version_number = %s AND versions.version_number = %s
2016-12-16 14:35:36,351 INFO sqlalchemy.engine.base.Engine ('Alaria nana', 0, 0)
<Species 1L>
>>> species[0].version.version_number
2016-12-16 14:35:54,461 INFO sqlalchemy.engine.base.Engine SELECT species.id AS species_id, species.species_accepted AS species_species_accepted, species.species_common AS species_species_common, species.iucn_status_id AS species_iucn_status_id, species.esa_status_id AS species_esa_status_id, species.invasive_status AS species_invasive_status, species.gbif_taxon_key AS species_gbif_taxon_key, species.image_path AS species_image_path, species.image_path2 AS species_image_path2 
FROM species, versions 
WHERE species.species_accepted = %s AND versions.version_number = %s AND versions.version_number = %s 
 LIMIT %s
2016-12-16 14:35:54,461 INFO sqlalchemy.engine.base.Engine ('Alaria nana', 0, 0, 1)
2016-12-16 14:35:54,466 INFO sqlalchemy.engine.base.Engine SELECT versions.id AS versions_id, versions.version_number AS versions_version_number, versions.version_of_id AS versions_version_of_id, versions.version_date_added AS versions_version_date_added, versions.version_timestamp_created AS versions_version_timestamp_created, versions.version_uid AS versions_version_uid, versions.checked AS versions_checked, versions.status_id AS versions_status_id, versions.checked_count AS versions_checked_count, versions.version_user_id AS versions_version_user_id, versions.database_id AS versions_database_id, versions.species_id AS versions_species_id, versions.taxonomy_id AS versions_taxonomy_id, versions.trait_id AS versions_trait_id, versions.publication_id AS versions_publication_id, versions.study_id AS versions_study_id, versions.population_id AS versions_population_id, versions.matrix_id AS versions_matrix_id, versions.fixed_id AS versions_fixed_id, versions.stage_id AS versions_stage_id, versions.stage_type_id AS versions_stage_type_id, versions.matrix_stage_id AS versions_matrix_stage_id, versions.matrix_value_id AS versions_matrix_value_id, versions.author_contact_id AS versions_author_contact_id, versions.additional_source_id AS versions_additional_source_id 
FROM versions 
WHERE %s = versions.species_id AND versions.version_number = %s
2016-12-16 14:35:54,467 INFO sqlalchemy.engine.base.Engine (1L, 0)
0L
>>> 


from sqlalchemy.orm.query import Query

class VersionQuery(Query):
    def __iter__(self):
        return Query.__iter__(self.original())
    def original(self):
        mzero = self._mapper_zero()
        if mzero is not None:
            # crit = mzero.class_.version.version_number == 0
            return self.enable_assertions(False).filter(Version.version_number == 0)
        else:
            return self

 
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

engine = create_engine('mysql://root:jeh5t@localhost/demog_compadre', echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine, query_cls=VersionQuery)
sess = Session()
species = sess.query(Species).filter_by(species_accepted='Alaria nana').original()

for s in species:
    s

2016-12-16 14:35:36,347 INFO sqlalchemy.engine.base.Engine BEGIN (implicit)
2016-12-16 14:35:36,351 INFO sqlalchemy.engine.base.Engine SELECT species.id AS species_id, species.species_accepted AS species_species_accepted, species.species_common AS species_species_common, species.iucn_status_id AS species_iucn_status_id, species.esa_status_id AS species_esa_status_id, species.invasive_status AS species_invasive_status, species.gbif_taxon_key AS species_gbif_taxon_key, species.image_path AS species_image_path, species.image_path2 AS species_image_path2 
FROM species, versions 
WHERE species.species_accepted = %s AND versions.version_number = %s AND versions.version_number = %s
2016-12-16 14:35:36,351 INFO sqlalchemy.engine.base.Engine ('Alaria nana', 0, 0)
<Species 1L>
species[0].version.version_number
2016-12-16 14:35:54,461 INFO sqlalchemy.engine.base.Engine SELECT species.id AS species_id, species.species_accepted AS species_species_accepted, species.species_common AS species_species_common, species.iucn_status_id AS species_iucn_status_id, species.esa_status_id AS species_esa_status_id, species.invasive_status AS species_invasive_status, species.gbif_taxon_key AS species_gbif_taxon_key, species.image_path AS species_image_path, species.image_path2 AS species_image_path2 
FROM species, versions 
WHERE species.species_accepted = %s AND versions.version_number = %s AND versions.version_number = %s 
 LIMIT %s
2016-12-16 14:35:54,461 INFO sqlalchemy.engine.base.Engine ('Alaria nana', 0, 0, 1)
2016-12-16 14:35:54,466 INFO sqlalchemy.engine.base.Engine SELECT versions.id AS versions_id, versions.version_number AS versions_version_number, versions.version_of_id AS versions_version_of_id, versions.version_date_added AS versions_version_date_added, versions.version_timestamp_created AS versions_version_timestamp_created, versions.version_uid AS versions_version_uid, versions.checked AS versions_checked, versions.status_id AS versions_status_id, versions.checked_count AS versions_checked_count, versions.version_user_id AS versions_version_user_id, versions.database_id AS versions_database_id, versions.species_id AS versions_species_id, versions.taxonomy_id AS versions_taxonomy_id, versions.trait_id AS versions_trait_id, versions.publication_id AS versions_publication_id, versions.study_id AS versions_study_id, versions.population_id AS versions_population_id, versions.matrix_id AS versions_matrix_id, versions.fixed_id AS versions_fixed_id, versions.stage_id AS versions_stage_id, versions.stage_type_id AS versions_stage_type_id, versions.matrix_stage_id AS versions_matrix_stage_id, versions.matrix_value_id AS versions_matrix_value_id, versions.author_contact_id AS versions_author_contact_id, versions.additional_source_id AS versions_additional_source_id 
FROM versions 
WHERE %s = versions.species_id AND versions.version_number = %s
2016-12-16 14:35:54,467 INFO sqlalchemy.engine.base.Engine (1L, 0)
0L




