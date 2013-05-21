#!/usr/bin/python
from pybrain.datasets import SupervisedDataSet
from pybrain.tools.shortcuts import buildNetwork
from pybrain.supervised import BackpropTrainer
from glob import glob
import functions
import warnings
import pickle
import shutil
import os
import sys
warnings.filterwarnings('ignore')


def make_dataset(source):
    data = SupervisedDataSet(3, 1)

    print("Adding valid training data")
    for i in glob(source + "valid/*.jpg"):
        data.addSample(functions.values(i), [1])

    print("Adding invalid training data")
    for i in glob(source + "invalid/*.jpg"):
        data.addSample(functions.values(i), [0])

    return data


def train_network(d, iterations):
    print("Training")
    n = buildNetwork(d.indim, 4, d.outdim, bias=True)
    t = BackpropTrainer(
        n,
        d,
        learningrate=0.01,
        momentum=0.99,
        verbose=False)
    for epoch in range(iterations):
        t.train()
    return n


def test(path, source, net, cutoff):
    val = net.activate(functions.values(path))
    base = os.path.basename(path)
    if val > cutoff:
        print path, val, "(Valid)"
        shutil.copy(path, source + 'valid/' + base)
    else:
        print path, val, "(Invalid)"
        shutil.copy(path, source + 'invalid/' + base)

if __name__ == "__main__":
    try:
        f = open('_learned', 'r')
        net = pickle.load(f)
        f.close()
    except:
        data = make_dataset('./training_data')
        net = train_network(data, iterations=5000)
        f = open('_learned', 'w')
        pickle.dump(net, f)
        f.close()

    print("Testing")
    for path in glob('./' + sys.argv[1] + "*.jpg"):
        test(path, './' + sys.argv[1], net, cutoff=0.9)
