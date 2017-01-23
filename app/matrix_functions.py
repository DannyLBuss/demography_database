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
    
