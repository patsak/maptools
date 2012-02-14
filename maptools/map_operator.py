#!/usr/bin/python

import os


import shutil
from osgeo import gdal
import osr
import re
import sys


import pygpx as GPX
import datetime

import math
"""
Module for operation with GeoTiff map
"""

def km1shppath():
        return os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)),"data","topo1km-rus.shp"))
def km2shppath():
        return os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)),"data","topo2km-rus.shp"))
class Map():

	def __init__(self, path):
		self.path = path
		ds = gdal.Open(path)

		new_cs=osr.SpatialReference()
		#print path
		new_cs.ImportFromWkt(ds.GetProjectionRef())
		
		# create the new coordinate system
		wgs84_wkt = """
		GEOGCS["WGS 84",
		DATUM["WGS_1984",
			SPHEROID["WGS 84",6378137,298.257223563,
				AUTHORITY["EPSG","7030"]],
			AUTHORITY["EPSG","6326"]],
		PRIMEM["Greenwich",0,
			AUTHORITY["EPSG","8901"]],
		UNIT["degree",0.01745329251994328,
			AUTHORITY["EPSG","9122"]],
		AUTHORITY["EPSG","4326"]]"""

		old_cs = osr.SpatialReference()
		old_cs.ImportFromWkt(wgs84_wkt)

		# create a transform object to convert between coordinate systems
		self.transform = osr.CoordinateTransformation(old_cs,new_cs) 
		self.reversetransform = osr.CoordinateTransformation(new_cs,old_cs)
		self.width = ds.RasterXSize
		self.height = ds.RasterYSize
		
		

		gt = ds.GetGeoTransform()
		#print gt
		self.minx = gt[0]
		self.miny = gt[3] + self.width*gt[4] + self.height*gt[5] 
		self.maxx = gt[0] + self.width*gt[1] + self.height*gt[2]
		self.maxy = gt[3] 
		self.coordMin = self.reversetransform.TransformPoint(self.minx,self.miny)[:-1]
	#	print self.minx,self.miny,self.maxx,self.maxy
		self.coordMax = self.reversetransform.TransformPoint(self.maxx,self.maxy)[:-1]
		
	def _getTopOffset(self,x):
		leftTopOffset = self.getPixelCoord(self.coordMin[0],self.coordMax[1])[1]
		rightTopOffset = self.getPixelCoord(self.coordMax[0],self.coordMax[1])[1]
		#print leftTopOffset,rightTopOffset
		return ((self.width-x)/self.width)*(leftTopOffset-rightTopOffset)
		
	def getPath(self):
		return self.path
	def getWGS84Coord(self,x,y):
		#print "offset ",x,self._getTopOffset(x)
		raw_coord = (x*(float)(self.maxx-self.minx)/self.width+self.minx ,\
					abs(y*(float)(self.maxy-self.miny)/self.height-self.maxy))
		#print self.getPixelCoord(117.33,57.0092)

		#print self.coordMax,self.coordMin

		coord=self.reversetransform.TransformPoint(raw_coord[0],raw_coord[1])[:-1]
		#print coord,x,y
		# coord=(coord[0],\
		# 	   coord[1]-(self._getTopOffset(x)/self.getPixelForMinuteLon())/60)
		#print coord
		return  coord 
			
	def getPixelCoord(self, lan, lat):
		#print self.transform
		
		
		tr_coord  = self.transform.TransformPoint(lan , lat)
		# self.minx,self.miny, self.maxx, self.maxy
		return  ((float)(tr_coord[0]-self.minx)/(self.maxx-self.minx)*self.width,\
		 (float)(-tr_coord[1]+self.maxy)/(self.maxy-self.miny)*self.height)
	def getCoordinateBox(self):
		return (self.coordMin,self.coordMax)
	def getPixelForKilometer(self):
		beginPixel = self.getPixelCoord(self.coordMin[0],self.coordMin[1])
		modCoordMin = (self.coordMin[0], self.coordMin[1] + float(1)/60)
		endPixel = self.getPixelCoord(modCoordMin[0], modCoordMin[1])
		
		return math.sqrt((beginPixel[1]-endPixel[1])**2 + (beginPixel[0]-endPixel[0])**2)*(2/1.85200)*0.5
	def getPixelForMinuteLat(self):
		beginPixel = self.getPixelCoord(self.coordMin[0],self.coordMax[1])
		modCoordMin = (self.coordMin[0]+float(1)/60, self.coordMax[1])
		endPixel = self.getPixelCoord(modCoordMin[0], modCoordMin[1])
		
		return math.sqrt((beginPixel[1]-endPixel[1])**2 + (beginPixel[0]-endPixel[0])**2)
	def getPixelForMinuteLon(self):
		
		beginPixel = self.getPixelCoord(self.coordMin[0],self.coordMax[1])
		#print self.coordMin
		modCoordMin = (self.coordMin[0], self.coordMax[1] - float(1)/60)
		#print modCoordMin
		endPixel = self.getPixelCoord(modCoordMin[0], modCoordMin[1])
		#print beginPixel,endPixel
		#print math.sqrt((beginPixel[1]-endPixel[1])**2 + (beginPixel[0]-endPixel[0])**2)

		return math.sqrt((beginPixel[1]-endPixel[1])**2 + (beginPixel[0]-endPixel[0])**2)


		#endPixel  = getPixelCoord()
#m = Map("/home/privezentsev/kodar-1km.tif")
#m.getPixelForMinuteLon()
#print m.getWGS84Coord(1000,0)
	

