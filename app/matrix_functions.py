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
#####Count Matrix Functions######
###UnReleased and Unfinished### - Note these won't work yet until database is in the Population.model which it isn't atm

##Matrices that are unreleased and unfinished (amber)##
def all_matrices_unreleased():
    all_matrices_unreleased = Matrix.query.join(Version).join(Version.statuses).filter(Status.status_name=="Amber").join(Population).join(Population.database).filter(Database.database_name=="Unreleased").count()
    return all_matrices_unreleased

##Populations that are unreleased and unfinished (amber)##
def all_populations_unreleased():
    all_populations_unreleased = Population.query.join(Version).join(Version.statuses).filter(Status.status_name=="Amber").join(Database).filter(Database.database_name=="Unreleased").count()
    return all_populations_unreleased

##Species that are unreleased and unfinished (amber)##
def all_species_unreleased():
    all_species_unreleased = Species.query.join(Version).join(Version.statuses).filter(Status.status_name=="Amber").join(Population).join(Population.database).filter(Database.database_name=="Unreleased").count()
    return all_species_unreleased

##Matrices that are unreleased and ready to be deployed (Green)##
def all_matrices_unreleased_complete():
    all_matrices_unreleased_complete = Matrix.query.join(Version).join(Version.statuses).filter(Status.status_name=="Green").join(Population).join(Population.database).filter(Database.database_name=="Unreleased").count()
    return all_matrices_unreleased_complete
    ##Populations##
def all_populations_unreleased_complete():
    all_populations_unreleased_complete = Population.query.join(Version).join(Version.statuses).filter(Status.status_name=="Green").join(Database).filter(Database.database_name=="Unreleased").count()
    return all_populations_unreleased_complete
        ##Species##
def all_species_unreleased_complete():
    all_species_unreleased_complete = Species.query.join(Version).join(Version.statuses).filter(Status.status_name=="Green").join(Population).join(Population.database).filter(Database.database_name=="Unreleased").count()
    return all_species_unreleased_complete

###Green Flags and Released### 
    ##COMPADRE##
        ##Matrices##
def all_matrices_released_compadre():
    all_matrices_released_2 = Matrix.query.join(Version).join(Version.statuses).filter(Status.status_name=="Green").join(Population).join(Population.database).filter(Database.database_name=="3.2.1").count()
    all_matrices_released_3 = Matrix.query.join(Version).join(Version.statuses).filter(Status.status_name=="Green").join(Population).join(Population.database).filter(Database.database_name=="4.0.1").count()
    all_matrices_released_4 = Matrix.query.join(Version).join(Version.statuses).filter(Status.status_name=="Green").join(Population).join(Population.database).filter(Database.database_name=="3.0.0").count()
    all_matrices_released_compadre = all_matrices_released_2 + all_matrices_released_3 + all_matrices_released_4
    return all_matrices_released_compadre
        ##Population##
def all_populations_released_compadre():
    all_populations_released_2 = Population.query.join(Version).join(Version.statuses).filter(Status.status_name=="Green").join(Database).filter(Database.database_name=="3.2.1").count()
    all_populations_released_3 = Population.query.join(Version).join(Version.statuses).filter(Status.status_name=="Green").join(Database).filter(Database.database_name=="4.0.1").count()
    all_populations_released_4 = Population.query.join(Version).join(Version.statuses).filter(Status.status_name=="Green").join(Database).filter(Database.database_name=="3.0.0").count()
    all_populations_released_compadre = all_populations_released_2 + all_populations_released_3 + all_populations_released_4
    return all_populations_released_compadre
        ##Species##
def all_species_released_compadre():
    all_species_released_2 = Species.query.join(Version).join(Version.statuses).filter(Status.status_name=="Green").join(Population).join(Population.database).filter(Database.database_name=="3.2.1").count()
    all_species_released_3 = Species.query.join(Version).join(Version.statuses).filter(Status.status_name=="Green").join(Population).join(Population.database).filter(Database.database_name=="4.0.1").count()
    all_species_released_4 = Species.query.join(Version).join(Version.statuses).filter(Status.status_name=="Green").join(Population).join(Population.database).filter(Database.database_name=="3.0.0").count()
    all_species_released_compadre = all_matrices_released_2 + all_matrices_released_3 + all_matrices_released_4
    return all_species_released_compadre

    ##COMADRE##
        ##Matrices##
def all_matrices_released_comadre():
    all_matrices_released_5 = Matrix.query.join(Version).join(Version.statuses).filter(Status.status_name=="Green").join(Population).join(Population.database).filter(Database.database_name=="2.0.1").count()
    all_matrices_released_6 = Matrix.query.join(Version).join(Version.statuses).filter(Status.status_name=="Green").join(Population).join(Population.database).filter(Database.database_name=="1.0.0").count()
    all_matrices_released_comadre = all_matrices_released_5 + all_matrices_released_6
    return all_matrices_released_comadre
        ##Population##
def all_populations_released_comadre():
    all_populations_released_5 = Population.query.join(Version).join(Version.statuses).filter(Status.status_name=="Green").join(Database).filter(Database.database_name=="2.0.1").count()
    all_populations_released_6 = Population.query.join(Version).join(Version.statuses).filter(Status.status_name=="Green").join(Database).filter(Database.database_name=="1.0.0").count()
    all_populations_released_comadre = all_populations_released_5 + all_populations_released_6
    return all_populations_released_comadre
        ##Species##
def all_species_released_comadre():
    all_species_released_5 = Species.query.join(Version).join(Version.statuses).filter(Status.status_name=="Green").join(Population).join(Population.database).filter(Database.database_name=="2.0.1").count()
    all_species_released_6 = Species.query.join(Version).join(Version.statuses).filter(Status.status_name=="Green").join(Population).join(Population.database).filter(Database.database_name=="1.0.0").count()
    all_species_released_comadre = all_matrices_released_5 + all_matrices_released_6
    return all_species_released_comadre

###Green Flags###
##Count all populations with green flag, for user and compadrino areas
def all_matrices_green():
    all_matrices_green = Matrix.query.join(Version).join(Version.statuses).filter(Status.status_name=="Green").count()
    return all_matrices_green

def all_matrices_green_plants():
    all_matrices_green_plants = Matrix.query.join(Matrix.population).join(Population.species).join(Species.taxonomy).filter(Taxonomy.kingdom == "Plantae").join(Version).join(Version.statuses).filter(Status.status_name=="Green").count()
    return all_matrices_green_plants

def all_matrices_green_animals():
    all_matrices_green_animals = Matrix.query.join(Matrix.population).join(Population.species).join(Species.taxonomy).filter(Taxonomy.kingdom == "Plantae").join(Version).join(Version.statuses).filter(Status.status_name=="Green").count()
    return all_matrices_green_animals

def all_pops_green():
    all_pops_green = Population.query.join(Version).join(Version.statuses).filter(Status.status_name=="Green").count()
    return all_pops_green

def all_species_green():
    all_species_green = Species.query.join(Version).join(Version.statuses).filter(Status.status_name=="Green").count()
    return all_species_green

###Count function for admin areas###
def all_matrices():
    all_matrices_count = Matrix.query.count()
    return all_matrices_count

##All_populations
def all_pops():
    all_pops_count = Population.query.count()
    return all_pops_count
##No. matrices in compadre (plants only)
def count_plants():
     count_plants = Matrix.query.join(Matrix.population).join(Population.species).join(Species.taxonomy).filter(Taxonomy.kingdom == "Plantae").count()
     return count_plants

##No. matrices in compadre (plants, fungi and algae)
def count_compadre():
     count_fungi = Matrix.query.join(Matrix.population).join(Population.species).join(Species.taxonomy).filter(Taxonomy.kingdom == "Plantae").count()
     count_chromista = Matrix.query.join(Matrix.population).join(Population.species).join(Species.taxonomy).filter(Taxonomy.kingdom == "Chromista").count()
     count_chromalveolata = Matrix.query.join(Matrix.population).join(Population.species).join(Species.taxonomy).filter(Taxonomy.kingdom == "Chromalveolata").count()
     count_compadre = count_plants() + count_fungi + count_chromista + count_chromalveolata
     return count_compadre

##No. matrices in comadre (Animalia)
def count_comadre():
    count_comadre = Matrix.query.join(Matrix.population).join(Population.species).join(Species.taxonomy).filter(Taxonomy.kingdom == "Animalia").count()
    return count_comadre

#####Count Populations Functions######
##No. populations in compadre (plants only)
def count_plants_pop():
    count_plants_pop = Population.query.join(Species).join(Species.taxonomy).filter(Taxonomy.kingdom == "Plantae").count()
    return count_plants_pop

##No. populations in compadre (plants only)
def count_compadre_pop():
    count_chromista_pop = Population.query.join(Species).join(Species.taxonomy).filter(Taxonomy.kingdom == "Chromista").count()
    count_chromalveolta_pop = Population.query.join(Species).join(Species.taxonomy).filter(Taxonomy.kingdom == "Chromalveolata").count()
    count_fungi_pop = Population.query.join(Species).join(Species.taxonomy).filter(Taxonomy.kingdom == "Fungi").count()
    count_compadre_pop = count_plants_pop() + count_chromalveolta_pop + count_chromista_pop + count_fungi_pop
    return count_compadre_pop

##No. populations in comadre (animalia only)
def count_comadre_pop():
    count_comadre_pop = Population.query.join(Species).join(Species.taxonomy).filter(Taxonomy.kingdom == "Animalia").count()
    return count_comadre_pop

def count_comadre_pop_green():
    count_comadre_pop_green = Population.query.join(Version).join(Version.statuses).filter(Status.status_name=="Green").join(Population.species).join(Species.taxonomy).filter(Taxonomy.kingdom=="Animalia").count()
    return count_comadre_pop_green

#####Count Species Functions######
##All species
def species_total_count():
    species_total_count = Species.query.count()
    return species_total_count

##No. plant species
def species_plant_count():
    species_plant_count = Species.query.join(Taxonomy).filter(Taxonomy.kingdom == "Plantae").count()
    return species_plant_count

##No. compadre species inc. fungi, algae, etc.
def species_compadre_count():
    species_chromista_count = Species.query.join(Taxonomy).filter(Taxonomy.kingdom == "Chromista").count()
    species_chromalveolta_count = Species.query.join(Taxonomy).filter(Taxonomy.kingdom == "Chromalveolta").count()
    species_fungi_count = Species.query.join(Taxonomy).filter(Taxonomy.kingdom == "Fungi").count()
    species_compadre_count = species_plant_count() + species_chromalveolta_count + species_chromista_count + species_fungi_count
    return species_compadre_count

##No. comadre species 
def species_comadre_count():
    species_comadre_count = Species.query.join(Taxonomy).filter(Taxonomy.kingdom == "Animalia").count()
    return species_comadre_count

##No. comadre species 
def species_comadre_count_green():
    species_comadre_count_green = Species.query.join(Version).join(Version.statuses).filter(Status.status_name=="Green").join(Population.species).join(Species.taxonomy).filter(Taxonomy.kingdom=="Animalia").count()
    return species_comadre_count_green
