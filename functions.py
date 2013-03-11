#!/usr/bin/python

import MySQLdb, MySQLdb.cursors
import Image
import colorsys 
import glob, os
import numpy
import matplotlib
matplotlib.use('Agg')
from scipy.cluster.vq import *
import pylab
pylab.close()
import math
import warnings

def fxn():
    warnings.warn("deprecated", DeprecationWarning)

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    fxn()

conn = MySQLdb.connect(db='nrl_asteroids',read_default_file="./.my.cnf",cursorclass=MySQLdb.cursors.DictCursor)

def distance(a, b) :
    a_x, a_y = a
    b_x, b_y = b
    return math.sqrt((a_x - b_x)**2 + (a_y - b_y)**2)

def _get_img(filename):
    return Image.open(filename)

def _majority(r, g, b) :
    return colorsys.rgb_to_hsv(float(r)/256,float(g)/256,float(b)/256)

def function(filename):
    return values(_get_img(filename))

def values(im, val_min=.25, val_max=.90):
    stds = 2
    a_avg = 0.713228289156627
    a_std = 0.03178173297698*stds
    b_avg = 0.192794843373494
    b_std = 0.03031368437293*stds
    a = b = c = 0.0
    a_c = b_c = c_c = 0.0
    wid, hei = im.size
    pix = im.load()
    xyz = []

    for x in range(10, wid-10) :
        for y in range(10, hei-10) :
            h, s, v =  _majority(*pix[x,y])
            #print "%f\t %f\t %f" % (h, s, v)
            if val_max > v > val_min :
                xyz.append([x,y,h])
                if a_avg - a_std < h < a_avg + a_std:
                    a += h
                    a_c += 1.0
                elif b_avg - b_std < h < b_avg + b_std:
                    b += h
                    b_c += 1.0
                else:
                    c += h
                    c_c += 1.0
    if (a_c < 10 or b_c < 10) and val_min > .075: # We haven't found any of one
        return values(im, val_min=val_min-.01)
    else :
        if a_c == 0.0 :
            a_c = 1.0
        if b_c == 0.0 :
            b_c = 1.0
        if c_c == 0.0 :
            c_c = 1.0

        _sum = a_c + b_c + c_c

        colin_max = 0
        colin_min = 1000
        dist_max = 0
        dist_min = 1000
        xyz_np = numpy.array(xyz)

        # Repeated k-means-cluster stuff
        for t in range(20):
            # Do a k-means-squared clustering
            res, idx = kmeans2(xyz_np,3)

            '''
            colors = ([([0,0,0],[1,0,0],[0,0,1])[q] for q in idx])
            pylab.scatter(xyz_np[:,0],xyz_np[:,1], c=colors)
            pylab.plot(res[:,0], res[:,1], 'ro')
            pylab.savefig("clust-%d.png" % (t))
            pylab.close()
            '''

            # Determine the average cluster distance
            avg_dist = [[],[],[]]
            for i, g in enumerate(idx):
                dist = distance((xyz[i][0],xyz[i][1]),(res[g][0], res[g][1])) 
                avg_dist[g].append(dist)
            for l in avg_dist:
                try :
                    avg = sum(l)/len(l)
                    if avg < dist_min :
                        dist_min = avg
                    if avg > dist_max :
                        dist_max = avg
                except ZeroDivisionError :
                    pass

            # Determine the collinearity metric
            colin = abs((res[2][0] - res[0][0]) * (res[1][1] - res[0][1]) + (res[2][1] - res[0][1]) * (res[0][0] - res[1][0]))
            if colin < colin_min:
                colin_min = colin
            if colin > colin_max:
                colin_max = colin
        '''
        "Average high value",
        "Average low value",
        "Ratio of high to colored",
        "Ratio of low to colored",
        "Ratio of non-valid to colored",
        "minimum colinearity",
        "maximum colinearity",
        "minimum cluster distance",
        "maximum cluster distance")
        '''
#        return [a/a_c, b/b_c, a_c/_sum, b_c/_sum, c_c/_sum, colin_min, colin_max, dist_min, dist_max]
        '''
        Percentage valid hues to non valid hues,
        best collinearity
        best cluster distance
        '''
        return [(a_c+b_c)/_sum, colin_min/125, dist_min/5]

if __name__ == "__main__":
    worst_dist = 0
    for i in glob.glob("./invalid/272.jpg"):
        x = function(i)
        if x[2] > worst_dist :
            worst_dist = x[2]
            print i, x
