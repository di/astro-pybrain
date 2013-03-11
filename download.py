#!/usr/bin/python
import os.path
import csv, random
import urllib, cStringIO
import cgi, cgitb
import MySQLdb, MySQLdb.cursors
from PIL import Image
import sys

conn = MySQLdb.connect(db='nrl_asteroids', read_default_file="./.my.cnf", cursorclass=MySQLdb.cursors.DictCursor)

def es(string):
   return MySQLdb.escape_string(str(string))

def getDataFromDB(image_id):
   cursor = conn.cursor()
   cursor.execute('SELECT * FROM images WHERE id=' + es(image_id))
   row = cursor.fetchone()
   return int(row['run']), int(row['camcol']), int(row['field'])

def get_unvalidated():
   cursor = conn.cursor()
   cursor.execute('SELECT * FROM asteroids WHERE validations=0')
   rows = cursor.fetchall()
   return rows

def buildImageURL(r,c,f):
   return "http://cas.sdss.org/dr7/en/get/frameByRCFZ.asp?R=" + str(r) + "&C=" + str(c) + "&F=" + str(f) + "&Z=0&submit1=Get+Image"

def checkThumbnail(asteroid_id, r, c, f, x, y):
   if int(asteroid_id) > 2000:
       print "Exiting", asteroid_id
       sys.exit(1)
   if (not os.path.isfile("./invalid/" + asteroid_id + ".jpg") and
       not os.path.isfile("./valid/" + asteroid_id + ".jpg") and
       not os.path.isfile("./test/" + asteroid_id + ".jpg")):
      im = Image.open(cStringIO.StringIO(urllib.urlopen(buildImageURL(r,c,f)).read()))
      im = im.crop((x-20, y-20, x+20, y+20))
      im.save("./test/" + asteroid_id + ".jpg", "JPEG")
      print "Adding %s.jpg" % (asteroid_id)
   else :
      print "Already have %s.jpg" % (asteroid_id)

invalid = get_unvalidated()
for asteroid in invalid:
   if asteroid['id'] > 1000 :
       asteroid_id = str(asteroid['id'])
       image_id = str(asteroid['image_id'])
       r,c,f = getDataFromDB(image_id)
       x = int(asteroid['x'])
       y = int(asteroid['y'])

       checkThumbnail(asteroid_id, r, c, f, x, y)
