#!/usr/bin/python
from pybrain.datasets import SupervisedDataSet
from pybrain.tools.shortcuts import buildNetwork
from pybrain.supervised import BackpropTrainer
import functions
import glob
import warnings
import pickle
import shutil
import os
warnings.filterwarnings('ignore')

def make_dataset():
    data = SupervisedDataSet(3,1)

    print "Adding valid data"
    for i in glob.glob("./valid/*.jpg"):
        data.addSample(functions.function(i),[1])

    for inpt, target in data:
        print inpt, target

    print "Adding invalid data"
    for i in glob.glob("./invalid/*.jpg"):
        data.addSample(functions.function(i),[0])

    return data

def training(d):
    print "Training"
    n = buildNetwork(d.indim, 4, d.outdim,bias=True)
    t = BackpropTrainer(n, d, learningrate = 0.01, momentum = 0.99, verbose = False)
    for epoch in range(0,5000):
        t.train()
    return n

def test(net):
    print "Testing"
    #testdata = SupervisedDataSet(9,1)

    for path in glob.glob("./test/*.jpg"):
        val = net.activate(functions.function(path))
        if val > .90 :
            print path, val, "(Valid)"
            shutil.move(path, './test/valid/' + os.path.basename(path))
        else :
            print path, val, "(Invalid)"
            shutil.move(path, './test/invalid/' + os.path.basename(path))


if __name__ == "__main__":
    try:
        f = open('_learned', 'r')
        net = pickle.load(f)
        f.close()
    except:
        trainingdata = make_dataset()
        net = training(trainingdata)
        f = open('_learned', 'w')
        pickle.dump(net, f)
        f.close()
    test(net)