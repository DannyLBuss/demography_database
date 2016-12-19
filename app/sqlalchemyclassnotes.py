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
        return self.enable_assertions(True).filter(Version.version_number == 0)

 
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

engine = create_engine('mysql://root:jeh5t@localhost/demog_compadre', echo=False)
Base.metadata.create_all(engine)
Session = scoped_session(sessionmaker(bind=engine, query_cls=VersionQuery))
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

import time 
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.query import Query
from sqlalchemy import or_

class VersionQuery(Query):
    def __iter__(self):
            return Query.__iter__(self)
    def all(self):
            status = Status.query.filter(Status.status_name=='Green').first()
            return [s for s in self.filter(Version.statuses == status).filter(Version.checked == True).order_by(Version.version_number.desc())]
    def original(self):
            return self.filter(Version.version_number == 0)[0]
    def latest(self):
            status = Status.query.filter(Status.status_name=='Green').first()
            return self.filter(Version.statuses == status).filter(Version.checked == True).order_by(Version.version_number.desc())[0]
    def all_checked(self):
            amber = Status.query.filter(Status.status_name=='Amber').first()
            green = Status.query.filter(Status.status_name=='Green').first()
            return self.filter(or_(Version.statuses == amber, Version.statuses == green)).filter(Version.checked == True).order_by(Version.version_number.desc())]
    def all_checked_unchecked(self):
            amber = Status.query.filter(Status.status_name=='Amber').first()
            green = Status.query.filter(Status.status_name=='Green').first()
            return [s for s in self.filter(or_(Version.statuses == amber, Version.statuses == green)).order_by(Version.version_number.desc())]
    def all_v(self):
            return [s for s in self.all()]
    def get_version(self, id):
            return self.filter(Version.version_number == id)[0]

Base = declarative_base()
engine = create_engine('mysql://root:jeh5t@localhost/demog_compadre', echo=False)
Base.metadata.create_all(engine)
Session = scoped_session(sessionmaker(bind=engine, query_cls=VersionQuery))
sess = Session()

sess.query(Species).all_v()

def session_original_query():
    start_time = time.time()
    [s for s in sess.query(Species).original()]
    print("--- Custom Query Loop Original %s seconds ---" % (time.time() - start_time))

session_original_query()

def session_loop_manually():
    start_time = time.time()
    [s for s in Species.query.filter(Version.version_number == 0)]
    print("--- Manual Query Loop Original %s seconds ---" % (time.time() - start_time))

session_loop_manually()



normal_query()
session_all_query()
session_original_query()
