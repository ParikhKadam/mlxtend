# Sebastian Raschka 2014-2016
# mlxtend Machine Learning Library Extensions
#
# Implementation of the ADAptive LInear NEuron classification algorithm.
# Author: Sebastian Raschka <sebastianraschka.com>
#
# License: BSD 3 clause

import numpy as np


class Adaline(object):
    """ADAptive LInear NEuron classifier.

    Parameters
    ------------
    eta : float (default: 0.01)
        solver rate (between 0.0 and 1.0)
    epochs : int (default: 50)
         Passes over the training dataset.
    solver : {'gd', 'sgd', 'normal equation'} (default: 'sgd')
         Method for solving the cost function. 'gd' for gradient descent,
         'sgd' for stochastic gradient descent, or 'normal equation' (default)
         to solve the cost function analytically.
    shuffle : bool (default: False)
         Shuffles training data every epoch if True to prevent circles.
    random_seed : int (default: None)
        Set random state for shuffling and initializing the weights.
    zero_init_weight : bool (default: False)
        If True, weights are initialized to zero instead of small random
        numbers in the interval [-0.1, 0.1];
        ignored if solver='normal equation'

    Attributes
    -----------
    w_ : 1d-array
      Weights after fitting.
    cost_ : list
      Sum of squared errors after each epoch.

    """
    def __init__(self, eta=0.01, epochs=50, solver='sgd',
                 random_seed=None, shuffle=False, zero_init_weight=False):
        np.random.seed(random_seed)
        self.eta = eta
        self.epochs = epochs
        self.shuffle = shuffle
        if solver not in ('normal equation', 'gd', 'sgd'):
            raise ValueError('learning must be "normal equation", '
                             '"gd", or "sgd')
        self.solver = solver
        self.zero_init_weight = zero_init_weight

    def fit(self, X, y, init_weights=True):
        """Learn weight coefficients from training data.

        Parameters
        ----------
        X : {array-like, sparse matrix}, shape = [n_samples, n_features]
            Training vectors, where n_samples is the number of samples and
            n_features is the number of features.
        y : array-like, shape = [n_samples]
            Target values.
        init_weights : bool (default: True)
            Re-initializes weights prior to fitting. Set False to continue
            training with weights from a previous fitting.

        Returns
        -------
        self : object

        """
        # check array shape
        if not len(X.shape) == 2:
            raise ValueError('X must be a 2D array. Try X[:,np.newaxis]')

        # check if {0, 1} or {-1, 1} class labels are used
        self.classes_ = np.unique(y)
        if not len(self.classes_) == 2 \
                or not self.classes_[0] in (-1, 0) \
                or not self.classes_[1] == 1:
            raise ValueError('Only supports binary class'
                             ' labels {0, 1} or {-1, 1}.')
        if self.classes_[0] == -1:
            self.thres_ = 0.0
        else:
            self.thres_ = 0.5

        # initialize weights
        if init_weights:
            self._init_weights(shape=1 + X.shape[1])

        self.cost_ = []

        if self.solver == 'normal equation':
            self.w_ = self._normal_equation(X, y)

        # Gradient descent or stochastic gradient descent learning
        else:
            for _ in range(self.epochs):

                if self.shuffle:
                    X, y = self._shuffle(X, y)

                if self.solver == 'gd':
                    y_val = self.activation(X)
                    errors = (y - y_val)
                    self.w_[1:] += self.eta * X.T.dot(errors)
                    self.w_[0] += self.eta * errors.sum()
                    cost = (errors**2).sum() / 2.0

                elif self.solver == 'sgd':
                    cost = 0.0
                    for xi, yi in zip(X, y):
                        yi_val = self.net_input(xi)
                        error = (yi - yi_val)
                        self.w_[1:] += self.eta * xi.dot(error)
                        self.w_[0] += self.eta * error
                        cost += error**2 / 2.0
                self.cost_.append(cost)

        return self

    def _shuffle(self, X, y):
        """Shuffle arrays in unison."""
        r = np.random.permutation(len(y))
        return X[r], y[r]

    def _normal_equation(self, X, y):
        """Solve linear regression analytically."""
        Xb = np.hstack((np.ones((X.shape[0], 1)), X))
        w = np.zeros(X.shape[1])
        z = np.linalg.inv(np.dot(Xb.T, Xb))
        w = np.dot(z, np.dot(Xb.T, y))
        return w

    def _init_weights(self, shape):
        """Initialize weight coefficients."""
        if self.zero_init_weight:
            self.w_ = np.zeros(shape)
        else:
            self.w_ = 0.2 * np.random.ranf(shape) - 0.5
        self.w_.astype('float64')

    def net_input(self, X):
        """Compute the linear net input."""
        return np.dot(X, self.w_[1:]) + self.w_[0]

    def activation(self, X):
        """Compute the linear activation from the net input."""
        return self.net_input(X)

    def predict(self, X):
        """Predict class labels of X.

        Parameters
        ----------
        X : {array-like, sparse matrix}, shape = [n_samples, n_features]
            Training vectors, where n_samples is the number of samples and
            n_features is the number of features.

        Returns
        ----------
        class : int
          Predicted class label.
          
        """
        return np.where(self.net_input(X) >= self.thres_,
                        self.classes_[1], self.classes_[0])