from models import Permission, Role, User, IUCNStatus, OrganismType, GrowthFormRaunkiaer, ReproductiveRepetition, \
                    DicotMonoc, AngioGymno, SpandExGrowthType, SourceType, Database, Purpose, MissingData, ContentEmail, Ecoregion, Continent, InvasiveStatusStudy, InvasiveStatusElsewhere, StageTypeClass, \
                    TransitionType, MatrixComposition, StartSeason, EndSeason, StudiedSex, Captivity, Species, Taxonomy, PurposeEndangered, PurposeWeed, Trait, \
                    Publication, AuthorContact, AdditionalSource, Population, Stage, StageType, Treatment, \
                    MatrixStage, MatrixValue, Matrix, Interval, Fixed, Small, CensusTiming, Institute, Status, Version, ChangeLogger
import numpy as np

#mat_str = "[0 0 2.81;0.5 0 0;0 0.45 0.45]" # for testing

def as_array(mat_str):
    # input: matlab format matrix
    # output: 
    try:
        mat_str = mat_str[1:(len(mat_str)-1)].replace(";"," ").split()
        mat_str = [float(i) for i in mat_str]
        mat_str = np.array(mat_str)
        order = int(np.sqrt(len(mat_str)))
        shape = (order,order)
        try:
            mat_str = mat_str.reshape(shape)
            return(mat_str)
        except ValueError:
            return("NA")
    except:
        return("NA")
    

def calc_lambda(matA):
    matA = as_array(matA)
    # input: matrix in string matlab format
    # output: float
    if matA != "NA":
        w, v = np.linalg.eig(matA)
        return float(max(w))
    else: 
        return(None)

def calc_surv_issue(matU):
    matU = as_array(matU)
    # input: matrix in string matlab format
    # output: float
    if matU != "NA":
        column_sums = [sum([row[i] for row in matU]) for i in range(0,len(matU[0]))]
        return max(column_sums)
    else:
        return(None)

def is_matrix_irreducible(matA):
    matA = as_array(matA)
    # input: matrix in string matlab format
    # output: 0 or 1
    if matA != "NA":
        order = np.shape(matA)[0]
        I = np.matrix(np.identity(order))
        IplusA = I + matA
        powermatrix = np.linalg.matrix_power(IplusA, (order - 1))
        minval = powermatrix.min()
        if minval > 0:
            return(1)
        else:
            return(0)
    else:
        return(None)

def is_matrix_primitive(matA):
    matA = as_array(matA)
    # input: matrix in string matlab format
    # output: 0 or 1
    if matA != "NA":
        order = np.shape(matA)[0]
        powermatrix = np.linalg.matrix_power(matA,((order ** 2) - (2 * order) + 2))
        minval = powermatrix.min()
        if minval > 0:
            return(1)
        else:
            return(0)
    else:
        return(None)

def is_matrix_ergodic(matA):
    matA = as_array(matA)
    # input: matrix in string matlab format
    # output: 0 or 1
    if matA != "NA":
        digits = 12
        order = np.shape(matA)[0] 
        lw, lv = np.linalg.eig(np.transpose(matA))
        lmax = lw.tolist().index(max(lw))
        v = lv[:,lmax]
        Rev = abs(np.real(v))
        Rev = np.round(Rev,decimals = digits)
        if min(Rev) > 0:
            return(1)
        else:
            return(0)
    else:
        return(None)
    
###### Some functions to create summary statistics on the front-end
####Structure of functions
###a. unreleased and incomplete
###b. unreleased and complete aka. ready for release
###c. released and complete 
###d. released but missing stuff
##Each of these 4 categories is split into 3 subsections (all; compadre; comadre)
#Each of these 3 subsections is split into 3 sections (species;populations;matrices)

##### a. unreleased and incomplete (amber) ######
###Note these won't work yet until database is related to the Population.model which it isn't atm
## All ##
# #Species
# def all_species_unreleased():
#     all_species_unreleased = Population.query.join(Database).filter(Database.database_master_version=="X").count()
#     return all_species_unreleased

# #Populations
# def all_populations_unreleased():
#     all_populations_unreleased = Population.query.join(Database).filter(Database.database_master_version=="X").count()
#     return all_populations_unreleased

# #Matrices
# def all_matrices_unreleased():
#     all_matrices_unreleased = Population.query.join(Database).filter(Database.database_master_version=="X").count()
#     return all_matrices_unreleased

## COMPADRE ##
#Species.join(Population.species).join(Species.taxonomy).filter(Taxonomy.kingdom == "Plantae").count()
#def compadre_species_unreleased():   
#    compadre_species_unreleased = Species.query.join(Version).join(Version.statuses).filter(Status.status_name=="Amber").join.(Species.taxonomy).filter(Taxonomy.kingdom == "Plantae").join(Population).join(Population.database).filter(Database.database_name=="Unreleased").count()
#    return compadre_species_unreleased

#Populations


#Matrices

## COMADRE ##
#Species
#def comadre_species_unreleased():   
#    comadre_species_unreleased = Species.query.join(Version).join(Version.statuses).filter(Status.status_name=="Amber").join.(Species.taxonomy).filter(Taxonomy.kingdom == "Animalia").join(Population).join(Population.database).filter(Database.database_name=="Unreleased").count()
#     return comadre_species_unreleased

#Populations


#Matrices

# ##### b. unreleased and complete aka. ready for release (green) ######
# ## All ##
# #Species
# def all_species_unreleased_complete():
#     all_species_unreleased_complete = Population.query.join(Database).filter(Database.database_master_version=="X").count()
#     return all_species_unreleased_complete

# #Populations
# def all_populations_unreleased_complete():
#     all_populations_unreleased_complete = Population.query.join(Database).filter(Database.database_master_version=="X").count()
#     return all_populations_unreleased_complete

# #Matrices
# def all_matrices_unreleased_complete():
#     all_matrices_unreleased_complete = Population.query.join(Database).filter(Database.database_master_version=="X").count()
#     return all_matrices_unreleased_complete

## COMPADRE ##
#Species


#Populations


#Matrices

## COMADRE ##
#Species


# #Populations


# #Matrices

# ###c. released and complete 

# ## ALL ##
# #Species
# def all_species_released_complete():
#     all_species_released_complete = Population.query.join(Database).filter(Database.database_master_version=="X").count()
#     return all_species_released_complete

# #Populations
# def all_populations_released_complete():
#     all_populations_released_complete = Population.query.join(Database).filter(Database.database_master_version=="X").count()
#     return all_populations_released_complete


# #Matrices
# def all_matrices_released_complete():
#     all_matrices_released_complete = Population.query.join(Database).filter(Database.database_master_version=="X").count()
#     return all_matrices_released_complete    

# ## COMPADRE ## - when new versions of COMPADRE come out, these will need new versions added to get an accurate summary
# #Species
# def all_species_released_compadre():
# #    all_species_released_2 = Species.query.join(Version).join(Version.statuses).filter(Status.status_name=="Green").join(Population).join(Population.database).filter(Database.database_name=="3.2.1").count()
# #    all_species_released_3 = Species.query.join(Version).join(Version.statuses).filter(Status.status_name=="Green").join(Population).join(Population.database).filter(Database.database_name=="4.0.1").count()
# #    all_species_released_4 = Species.query.join(Version).join(Version.statuses).filter(Status.status_name=="Green").join(Population).join(Population.database).filter(Database.database_name=="3.0.0").count()
#     all_species_released_compadre = Population.query.join(Database).filter(Database.database_master_version=="X").count()
#     return all_species_released_compadre

# #Populations
# def all_populations_released_compadre():

#     all_populations_released_compadre = Population.query.join(Database).filter(Database.database_master_version=="X").count()
#     return all_populations_released_compadre

# #Matrices
# def all_matrices_released_compadre():
# #    all_matrices_released_2 = Matrix.query.join(Version).join(Version.statuses).filter(Status.status_name=="Green").join(Population).join(Population.database).filter(Database.database_name=="3.2.1").count()
# #    all_matrices_released_3 = Matrix.query.join(Version).join(Version.statuses).filter(Status.status_name=="Green").join(Population).join(Population.database).filter(Database.database_name=="4.0.1").count()
# #    all_matrices_released_4 = Matrix.query.join(Version).join(Version.statuses).filter(Status.status_name=="Green").join(Population).join(Population.database).filter(Database.database_name=="3.0.0").count()
#     all_matrices_released_compadre = Population.query.join(Database).filter(Database.database_master_version=="X").count()
#     return all_matrices_released_compadre
# ## COMADRE ##
# #Species
# def all_species_released_comadre():
# #    all_species_released_5 = Species.query.join(Version).join(Version.statuses).filter(Status.status_name=="Green").join(Population).join(Population.database).filter(Database.database_name=="2.0.1").count()
# #    all_species_released_6 = Species.query.join(Version).join(Version.statuses).filter(Status.status_name=="Green").join(Population).join(Population.database).filter(Database.database_name=="1.0.0").count()
#     all_species_released_comadre = Population.query.join(Database).filter(Database.database_master_version=="X").count()
#     return all_species_released_comadre

# #Populations
# def all_populations_released_comadre():
# #    all_populations_released_5 = Population.query.join(Version).join(Version.statuses).filter(Status.status_name=="Green").join(Database).filter(Database.database_name=="2.0.1").count()
# #    all_populations_released_6 = Population.query.join(Version).join(Version.statuses).filter(Status.status_name=="Green").join(Database).filter(Database.database_name=="1.0.0").count()
#     all_populations_released_comadre = Population.query.join(Database).filter(Database.database_master_version=="X").count()
#     return all_populations_released_comadre

# #Matrices
# def all_matrices_released_comadre():
# #    all_matrices_released_5 = Matrix.query.join(Version).join(Version.statuses).filter(Status.status_name=="Green").join(Population).join(Population.database).filter(Database.database_name=="2.0.1").count()
# #    all_matrices_released_6 = Matrix.query.join(Version).join(Version.statuses).filter(Status.status_name=="Green").join(Population).join(Population.database).filter(Database.database_name=="1.0.0").count()
#     all_matrices_released_comadre = Population.query.join(Database).filter(Database.database_master_version=="X").count()
#     return all_matrices_released_comadre

# ###d. released but missing stuff


## ALL ##
#Species


#Populations


#Matrices

## COMPADRE ##
#Species


# #Populations


# #Matrices

# ## COMADRE ##
# #Species


# #Populations


# ######Admin Use Only#######
# ###Count function for admin areas - Total sums###
# def all_matrices():
#     all_matrices_count = Matrix.query.count()
#     return all_matrices_count

# ##All_populations
# def all_pops():
#     all_pops_count = Population.query.count()
#     return all_pops_count

# ##All_species
# def all_species():
#     all_species = Species.query.count()
#     return all_species

# ##All. matrices in compadre (plants only)
# def count_plants():
#      count_plants = Matrix.query.join(Matrix.population).join(Population.species).join(Species.taxonomy).filter(Taxonomy.kingdom == "Plantae").count()
#      return count_plants

# ##All. matrices in comadre (animalia only)
# def count_comadre():
#      count_comadre = Matrix.query.join(Matrix.population).join(Population.species).join(Species.taxonomy).filter(Taxonomy.kingdom == "Animalia").count()
#      return count_comadre

# ##No. matrices in compadre (plants, fungi and algae)
# def count_compadre():
#      count_fungi = Matrix.query.join(Matrix.population).join(Population.species).join(Species.taxonomy).filter(Taxonomy.kingdom == "Plantae").count()
#      count_chromista = Matrix.query.join(Matrix.population).join(Population.species).join(Species.taxonomy).filter(Taxonomy.kingdom == "Chromista").count()
#      count_chromalveolata = Matrix.query.join(Matrix.population).join(Population.species).join(Species.taxonomy).filter(Taxonomy.kingdom == "Chromalveolata").count()
#      count_compadre = count_plants() + count_fungi + count_chromista + count_chromalveolata
#      return count_compadre

# ##No. populations in compadre (plants only)
# def count_plants_pop():
#     count_plants_pop = Population.query.join(Species).join(Species.taxonomy).filter(Taxonomy.kingdom == "Plantae").count()
#     return count_plants_pop

# ##No. populations in compadre (plants, fungi and algae)
# def count_compadre_pop():
#     count_chromista_pop = Population.query.join(Species).join(Species.taxonomy).filter(Taxonomy.kingdom == "Chromista").count()
#     count_chromalveolta_pop = Population.query.join(Species).join(Species.taxonomy).filter(Taxonomy.kingdom == "Chromalveolata").count()
#     count_fungi_pop = Population.query.join(Species).join(Species.taxonomy).filter(Taxonomy.kingdom == "Fungi").count()
#     count_compadre_pop = count_plants_pop() + count_chromalveolta_pop + count_chromista_pop + count_fungi_pop
#     return count_compadre_pop

# ##No. populations in comadre (animalia only)
# def count_comadre_pop():
#     count_comadre_pop = Population.query.join(Species).join(Species.taxonomy).filter(Taxonomy.kingdom == "Animalia").count()
#     return count_comadre_pop

# ##No. compadre species inc. fungi, algae, etc. admin
# def species_compadre_count():
#     species_chromista_count = Species.query.join(Taxonomy).filter(Taxonomy.kingdom == "Chromista").count()
#     species_chromalveolta_count = Species.query.join(Taxonomy).filter(Taxonomy.kingdom == "Chromalveolta").count()
#     species_fungi_count = Species.query.join(Taxonomy).filter(Taxonomy.kingdom == "Fungi").count()
#     species_plant_count = Species.query.join(Taxonomy).filter(Taxonomy.kingdom == "Plantae").count()
#     species_compadre_count = Species.query.join(Taxonomy).filter(Taxonomy.kingdom == "Plantae").count()
#     return species_compadre_count

# ##No. comadre species admin
# def species_comadre_count():
#     species_comadre_count = Species.query.join(Taxonomy).filter(Taxonomy.kingdom == "Animalia").count()
#     return species_comadre_count
