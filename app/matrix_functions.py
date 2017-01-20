import numpy as np

def calc_lambda(matA):
    w, v = np.linalg.eig(matA)
    return float(max(w))

def calc_surv_issue(matU):
    column_sums = [sum([row[i] for row in matU]) for i in range(0,len(matU[0]))]
    return max(column_sums)

def is_matrix_irreducible(matA):
    # original R code is commented
    order = np.shape(matA)[0]
    I = np.matrix(np.identity(order))
    IplusA = I + matA
    powermatrix = np.linalg.matrix_power(matA, (order - 1))
    minval = np.matrix(powermatrix).min()
    if minval > 0:
        return(1)
    else:
        return(0)

def is_matrix_primitive(matA):
    order = np.shape(matA)[0]
    powermatrix = np.linalg.matrix_power(matA,((order ** 2) - (2 * order) + 2))
    minval = np.matrix(powermatrix).min()
    if minval > 0:
        return(1)
    else:
        return(0)

def is_matrix_ergodic(matA):
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
    
