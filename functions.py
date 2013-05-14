#!/usr/bin/python
import Image
import colorsys
import glob
import os
import sys
import math
import matplotlib
matplotlib.use('Agg')
import numpy
import pylab
pylab.close()
from scipy.cluster.vq import *
import warnings
warnings.filterwarnings('ignore')


def _distance(a, b):
    a_x, a_y = a
    b_x, b_y = b
    return math.sqrt((a_x - b_x)**2 + (a_y - b_y)**2)


def _to_hsv(r, g, b):
    return colorsys.rgb_to_hsv(float(r)/256, float(g)/256, float(b)/256)


def _plot(res, idx, xyz_np, i=0):
    colors = ([([0, 0, 0], [1, 0, 0], [0, 0, 1])[q] for q in idx])
    pylab.scatter(xyz_np[:, 0], xyz_np[:, 1], c=colors)
    pylab.plot(res[:, 0], res[:, 1], 'ro')
    pylab.savefig("clust-%d.png" % (i))
    pylab.close()


def function(filename):
    return values(Image.open(filename))


def mean_distance(res, idx, xyz, _max=5):
    # Determine the average cluster distance
    dist_min = sys.maxint
    avg_dist = [[], [], []]
    for i, g in enumerate(idx):
        dist = _distance((xyz[i][0], xyz[i][1]), (res[g][0], res[g][1]))
        avg_dist[g].append(dist)
    for l in avg_dist:
        try:
            avg = sum(l)/len(l)
            dist_min = min(dist_min, avg)
        except ZeroDivisionError:
            pass
    return dist_min/_max


def collinearity(res, _max=125):
    # Determine the collinearity metric
    return abs((res[2][0] - res[0][0]) * (res[1][1] - res[0][1]) + (res[2][1] - res[0][1]) * (res[0][0] - res[1][0]))/_max


def hue_ratio(im, val_min=.25, val_max=.90):
    stds = 2
    a_avg = 0.713228289156627
    a_std = 0.03178173297698*stds
    b_avg = 0.192794843373494
    b_std = 0.03031368437293*stds
    a_c = b_c = c_c = 0

    xyz = []
    pix = im.load()
    wid, hei = im.size
    for x in range(10, wid-10):
        for y in range(10, hei-10):
            h, s, v = _to_hsv(*pix[x, y])

            if val_max > v > val_min:
                xyz.append([x, y, h])
                if a_avg - a_std < h < a_avg + a_std:
                    a_c += 1
                elif b_avg - b_std < h < b_avg + b_std:
                    b_c += 1
                else:
                    c_c += 1
    if (a_c < 10 or b_c < 10) and val_min > .075:
        return hue_ratio(im, val_min=val_min-.01)
    else:
        return float(a_c + b_c) / float(a_c + b_c + c_c), xyz


def values(im, val_min=.25, val_max=.90):
    dist_min = sys.maxint
    collin_min = sys.maxint

    hue_rat, xyz = hue_ratio(im)

    # Repeated k-means-cluster stuff
    for t in range(20):
        # Do a k-means-squared clustering
        res, idx = kmeans2(numpy.array(xyz), 3)

        # Plot the clusters
        # plot(res, idx, numpy.array(xyz), t)

        dist_min = min(dist_min, mean_distance(res, idx, xyz))
        collin_min = min(collin_min, collinearity(res))

    return [hue_rat, collin_min, dist_min]

if __name__ == "__main__":
    for i in glob.glob("./invalid/272.jpg"):
        print i, function(i)
