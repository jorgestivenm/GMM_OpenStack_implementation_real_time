"""
Created on Mon Feb 12 09:59:16 2018

@author: Tomas Arias - Universidad de Antioquia

Maximum A Posteriori adaptation for GMM-UBM using DIAGONAL
covariance matrices

Modified Date: Fri Oct 25 17:32 2019
Modified by: Daniel Escobar Grisales - Universidad Antioquia

Return type(mixture.GaussianMixtureModel)


"""

import numpy as np
from sklearn import mixture


# Raise error when the covariance matrix is not diagonal
class cov_type(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


try:
    raise cov_type('')
except cov_type as e:
    print(e.value)
# ---------------------------------------------------------------
# ---------------------------------------------------------------
# ---------------------------------------------------------------


def ubm_map(gmm, X, mode='111', niter=100, r=16):
    """
    Inputs:
        gmm: Fitted Gaussian Mixture Model using sklearn's GaussianMixture
        X: Feature matrix (n_samples,n_features)
        mode: Parameters to be adapted:
              111: weights, means, covariances (default)
              100: Only weigths
              010: Only mean vectors
              011: mean vectors and covariance matrices
        niter: Number of iterations for adaptation (default=100)
        r: Relevance factor (default=16)
    Return:
        aModel: mixture.GaussianMixtureModel
    """
    # Check covariance matrix type
    if gmm.covariance_type != "diag":
        raise cov_type('Covariance Matrix must be diagonal!!!')

    # Compute posteriors
    pr = gmm.predict_proba(X)

    # Number of gaussian components
    ncomp = gmm.n_components

    # Number of samples(feature vectors)
    nsamples = np.shape(X)[0]

    # Initial statistics
    w = gmm.weights_.copy()
    u = gmm.means_.copy()
    s = gmm.covariances_.copy()

    # Iterations for adaptation process
    for igauss in range(0, ncomp):
        # Compute sufficient statistic for weights
        ni = pr[:, igauss].sum()

        # Compute sufficient statistic for means
        E = pr[:, igauss]*X.T
        E = E.sum(axis=1)
        E = E/ni
#        if math.isnan(np.sum(E)):
#            E[np.isnan(E)==True] = np.finfo(float).eps
        # Compute sufficient statistic for diagonal covariances
        E2 = (pr[:, igauss])*(X*X).T
        E2 = E2.sum(axis=1)
        E2 = E2/ni
#        if math.isnan(np.sum(E2)):
#            E2[np.isnan(E2)==True] = np.finfo(float).eps

        # Adaptation coefficient
        alpha = ni/(ni+r)

        # Number feature vectors
        T = nsamples

        for i in range(0, niter):
            if mode[0] == '1':
                # Compute new weigths
                w_hat = ((alpha*ni)/T)+((1-alpha)*w[igauss])
                # Update statistics
                w[igauss] = w_hat
            if mode[1] == '1':
                # Compute new mean vectors
                u_hat = (alpha*E)+((1-alpha)*u[igauss, :])
                # Update statistics
                u[igauss, :] = u_hat
            if mode[2] == '1':
                # Compute new diagonal covariance matrices
                temp1 = u[igauss, :]*u[igauss, :]
                temp2 = u_hat*u_hat
                s_hat = (alpha*E2)+((1-alpha)*(s[igauss, :]+temp1))-temp2
                # Update statistics
                s[igauss, :] = s_hat

    aModel_gmm = mixture.GaussianMixture(
        n_components=ncomp, covariance_type='diag', random_state=100).fit(X)
    aModel_gmm.means_ = u
    aModel_gmm.covariances_ = s
    aModel_gmm.weights_ = w/np.sum(w)

    return aModel_gmm
