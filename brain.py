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
warnings.filterwarnings('ignore')


def make_dataset():
    data = SupervisedDataSet(3, 1)

    print("Adding valid training data")
    for i in glob("./training_data/valid/*.jpg"):
        data.addSample(functions.values(i), [1])

    print("Adding invalid training data")
    for i in glob("./training_data/invalid/*.jpg"):
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


def test(net, cutoff):
    print("Testing")
    for path in glob("./test_data/*.jpg"):
        val = net.activate(functions.values(path))
        if val > cutoff:
            print path, val, "(Valid)"
            shutil.move(path, './test_data/valid/' + os.path.basename(path))
        else:
            print path, val, "(Invalid)"
            shutil.move(path, './test_data/invalid/' + os.path.basename(path))

if __name__ == "__main__":
    try:
        f = open('_learned', 'r')
        net = pickle.load(f)
        f.close()
    except:
        net = train_network(make_dataset(), iterations=5000)
        f = open('_learned', 'w')
        pickle.dump(net, f)
        f.close()
    test(net, cutoff=0.9)
