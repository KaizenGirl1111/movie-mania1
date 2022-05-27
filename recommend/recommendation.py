import numpy as np
import pandas as pd
import scipy.optimize

from .models import Myrating


def normalize_ratings(myY, myR):
    # Supress/hide the warning
    np.seterr(invalid='ignore')
    # The mean is only counting movies that were rated
    Ymean = np.sum(myY, axis=1) / np.sum(myR, axis=1)
    Ymean = Ymean.reshape((Ymean.shape[0], 1))
    return myY - Ymean, Ymean


def flatten_params(myX, myTheta):
    return np.concatenate((myX.flatten(), myTheta.flatten()))


def reshape_params(flattened_XandTheta, mynm, mynu, mynf):
    assert flattened_XandTheta.shape[0] == int(mynm * mynf + mynu * mynf)
    reX = flattened_XandTheta[:int(mynm * mynf)].reshape((mynm, mynf))
    reTheta = flattened_XandTheta[int(mynm * mynf):].reshape((mynu, mynf))
    return reX, reTheta


def cofi_cost_func(myparams, myY, myR, mynu, mynm, mynf, mylambda=0.):
    myX, myTheta = reshape_params(myparams, mynm, mynu, mynf)
    term1 = myX.dot(myTheta.T)
    term1 = np.multiply(term1, myR)
    cost = 0.5 * np.sum(np.square(term1 - myY))
    # for regularization
    cost += (mylambda / 2.) * np.sum(np.square(myTheta))
    cost += (mylambda / 2.) * np.sum(np.square(myX))
    return cost


def cofi_grad(myparams, myY, myR, mynu, mynm, mynf, mylambda=0.):
    myX, myTheta = reshape_params(myparams, mynm, mynu, mynf)
    term1 = myX.dot(myTheta.T)
    term1 = np.multiply(term1, myR)
    term1 -= myY
    Xgrad = term1.dot(myTheta)
    Thetagrad = term1.T.dot(myX)
    # Adding Regularization
    Xgrad += mylambda * myX
    Thetagrad += mylambda * myTheta
    return flatten_params(Xgrad, Thetagrad)


def recommend_engine():
    df = pd.DataFrame(list(Myrating.objects.all().values()))
    mynu = df.user_id.unique().shape[0]
    mynm = df.movie_id.unique().shape[0]
    mynf = 10

    Y = np.zeros((mynm, mynu))
    for row in df.itertuples():
        # print("ROW VARIABLE====>", row)
        Y[row[2] - 1, row[4] - 1] = row[3]
    R = np.zeros((mynm, mynu))
    for i in range(Y.shape[0]):
        for j in range(Y.shape[1]):
            if Y[i][j] != 0:
                R[i][j] = 1

    Ynorm, Ymean = normalize_ratings(Y, R)
    X = np.random.rand(mynm, mynf)
    Theta = np.random.rand(mynu, mynf)
    myflat = flatten_params(X, Theta)
    mylambda = 12.2
    result = scipy.optimize.fmin_cg(cofi_cost_func, x0=myflat, fprime=cofi_grad,
                                    args=(Y, R, mynu, mynm, mynf, mylambda),
                                    maxiter=40, disp=False, full_output=True)
    resX, resTheta = reshape_params(result[0], mynm, mynu, mynf)
    prediction_matrix = resX.dot(resTheta.T)
    return prediction_matrix, Ymean
