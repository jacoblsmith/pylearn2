"""
Test LpNorm cost
"""
import os
import numpy
from nose.tools import raises
import theano
from pylearn2.models.mlp import Linear
from pylearn2.models.mlp import Softmax
from pylearn2.models.mlp import MLP
from pylearn2.costs.supervised_cost import NegativeLogLikelihood
from pylearn2.costs.cost import LpNorm
from pylearn2.costs.cost import SumOfCosts
from pylearn2.testing import datasets
from pylearn2.training_algorithms.sgd import SGD
from pylearn2.termination_criteria import EpochCounter
from pylearn2.train import Train


def test_shared_variables():
    '''
    LpNorm should handle shared variables.
    '''
    model = MLP(
        layers=[Linear(dim=100, layer_name='linear', irange=1.0),
                Softmax(n_classes=10, layer_name='softmax', irange=1.0)],
        batch_size=10,
        nvis=50
    )

    dataset = datasets.random_one_hot_dense_design_matrix(
        rng=numpy.random.RandomState(1876),
        num_examples=100,
        dim=50,
        num_classes=10
    )

    cost = SumOfCosts([NegativeLogLikelihood(),
                       LpNorm(variables=model.get_params(), p=2)])

    algorithm = SGD(
        learning_rate=0.01,
        cost=cost, batch_size=10,
        monitoring_dataset=dataset,
        termination_criterion=EpochCounter(1)
    )

    trainer = Train(
        dataset=dataset,
        model=model,
        algorithm=algorithm
    )

    trainer.main_loop()


def test_symbolic_expressions_of_shared_variables():
    '''
    LpNorm should handle symbolic expressions of shared variables.
    '''
    model = MLP(
        layers=[Linear(dim=100, layer_name='linear', irange=1.0),
                Softmax(n_classes=10, layer_name='softmax', irange=1.0)],
        batch_size=10,
        nvis=50
    )

    dataset = datasets.random_one_hot_dense_design_matrix(
        rng=numpy.random.RandomState(1876),
        num_examples=100,
        dim=50,
        num_classes=10
    )

    cost = SumOfCosts([NegativeLogLikelihood(),
                       LpNorm(variables=[param ** 2 for param in
                                         model.get_params()],
                              p=2)])

    algorithm = SGD(
        learning_rate=0.01,
        cost=cost, batch_size=10,
        monitoring_dataset=dataset,
        termination_criterion=EpochCounter(1)
    )

    trainer = Train(
        dataset=dataset,
        model=model,
        algorithm=algorithm
    )

    trainer.main_loop()


@raises(ValueError)
def test_symbolic_variables():
    '''
    LpNorm should not handle symbolic variables
    '''
    model = MLP(
        layers=[Linear(dim=100, layer_name='linear', irange=1.0),
                Softmax(n_classes=10, layer_name='softmax', irange=1.0)],
        batch_size=10,
        nvis=50
    )

    dataset = datasets.random_one_hot_dense_design_matrix(
        rng=numpy.random.RandomState(1876),
        num_examples=100,
        dim=50,
        num_classes=10
    )

    cost = SumOfCosts([NegativeLogLikelihood(), LpNorm(variables=[], p=2)])

    algorithm = SGD(
        learning_rate=0.01,
        cost=cost, batch_size=10,
        monitoring_dataset=dataset,
        termination_criterion=EpochCounter(1)
    )

    cost.costs[1].variables = [model.fprop(theano.tensor.matrix())]

    trainer = Train(
        dataset=dataset,
        model=model,
        algorithm=algorithm
    )

    trainer.main_loop()


if __name__ == '__main__':
    test_shared_variables()
    test_symbolic_expressions_of_shared_variables()
    test_symbolic_variables()
