#!/usr/bin/python

import os
import shutil
from osgeo import gdal
import osr
import re
import sys
import Image, ImageDraw, ImageFont
from   PIL.ExifTags import TAGS, GPSTAGS
import pygpx as GPX
import datetime
import image_operator
import map_operator

import math

def split_by_gpx(map_img,gpx_file,utc_zone):
	"""Create crop map by day"""
	split_dir = "split"
        
	gpx = GPX.GPX(open(gpx_file))
	map_info = map_operator.Map(map_img)
	if not os.path.exists(split_dir):
		os.mkdir(split_dir)
	for track in gpx.tracks:
		for trkseg in track.trksegs:
		
			cur_day=''
			ptcoord_list = []
			if len(trkseg.trkpts)>0:
				cur_day = trkseg.trkpts[0]
				ptcoord_list.append(map_info.getPixelCoord(cur_day.lon,cur_day.lat))
				cur_day.time = cur_day.time + datetime.timedelta(hours=int(utc_zone))
			for pt in trkseg.trkpts:
				pt.time = pt.time + datetime.timedelta(hours=int(utc_zone))

				if (pt.time.day - cur_day.time.day) != 0:
					image_operator.crop_path(map_img, \
											 ptcoord_list,
								             os.path.join(os.curdir, split_dir, \
														  track.name + "_" + str(cur_day.time.month) + "_" + str(cur_day.time.day) + ".jpg"))
					cur_day = pt
					ptcoord_list = []
					ptcoord_list.append(map_info.getPixelCoord(pt.lon,pt.lat))
				else:
					ptcoord_list.append(map_info.getPixelCoord(pt.lon,pt.lat))

def minimap_create(map_img,dir_path):
	"""Create minimap on the corner of photo"""
	mod = "mod"
	tiff = map_operator.Map(map_img)
	
	geo = image_operator.GeoExifCollector(dir_path)
	if not os.path.exists(os.path.join(dir_path, mod)):
		os.mkdir(os.path.join(dir_path, mod))
	for f in geo.getImagesFiles():
		
		wgsc = geo.getWGS84Coord(f)
		
                minimap_path = image_operator.minimap(f, tiff.getPath(), tiff.getPixelCoord(wgsc[0],wgsc[1]))
                image_operator.copyMetaData(f,minimap_path)
		target_path = os.path.join(dir_path, mod, os.path.basename(minimap_path))
		


		if os.path.exists(target_path):
			os.remove(target_path)
		shutil.move(minimap_path, os.path.join(dir_path,mod))


class PaperFormat():
	A4=(20,28)
	A3=(28,36)
	
		

def splitA4All(map_image, format=PaperFormat.A4):
	#print map_image
	m = map_operator.Map(map_image)
	box = m.getCoordinateBox()
	
	pixkil = m.getPixelForKilometer()
	
	a4width = pixkil*20
	a4height = pixkil*28

	by_width = int(m.width/a4width)+1
	by_height = int(m.height/a4height)+1

	for i in range(by_width):
		xcoord = i*a4width #+ init_coord[1]
		for j in range(by_height):
			ycoord = j*a4height #+ init_coord[0]	
			#print xcoord,ycoord

			splitOne(m,(xcoord,ycoord),format=format)
def _wgsToStr(coord):
	print str(round(coord))+ "0", str(int(coord))+ " " + str(round(abs(coord-round(coord))*60)), coord - round(coord)
	if abs(coord -round(coord))< float(1)/100:
		return 	str(round(coord))+ " " + "0"
	else:
		return str(int(coord))+ " " + str(int(abs(coord-int(coord))*60))
		
def splitOne(map_class, coord, format=PaperFormat.A4):
	m = map_class
	map_image = m.getPath()

	pixkil = m.getPixelForKilometer()
	
	xcoord = coord[0]
	ycoord = coord[1]
	formatWidth = format[0]*pixkil
	formatHeight= format[1]*pixkil
	offset = 26
	head = 80
	wgsLeft = m.getWGS84Coord(xcoord,ycoord)
	wgsRight = m.getWGS84Coord(xcoord+formatWidth,ycoord)
	#print wgsLeft,wgsRight
	#print j,i
	print int(wgsLeft[0]*60), wgsLeft[0]*60
	wgsDeltaX = wgsLeft[0]*60-int(wgsLeft[0]*60)
	wgsDeltaY = wgsLeft[1]*60-int(wgsLeft[1]*60)
	#print wgsLeft[1]*60,int(wgsLeft[1]*60),wgsDeltaX*m.getPixelForMinuteLat()
	#print wgsLeft[0],int(wgsLeft[0]),m.getPixelForMinuteLon()
	whKoef = m.getPixelForMinuteLat()/m.getPixelForMinuteLon()
	#math.sqrt((beginPixel[1]-endPixel[1])**2 + (beginPixel[0]-endPixel[0])**2)
	rotateAngle = math.atan((-wgsLeft[1]+wgsRight[1])/((-wgsLeft[0]+wgsRight[0])*whKoef))
	#print rotateAngle
	
	wgsToPath = lambda x:_wgsToStr(x).replace(" ","_")


	savepath = os.path.join(os.path.dirname(map_image),wgsToPath(wgsLeft[0]) + "x" +wgsToPath(wgsRight[1]) + ".jpg")
		
	print "Create " + savepath
	newIm = Image.new('RGBA',(int(formatWidth+52),int(formatHeight+52+head)),color=0xffffffff)

	img_raw = Image.open(map_image)
	box = (int(xcoord),int(ycoord),int(xcoord + formatWidth),int(ycoord+ formatHeight))
	im_crop = img_raw.crop(box)

	#image_operator._crop(map_image, (int(xcoord),int(ycoord),int(xcoord + formatWidth),int(ycoord+ formatHeight)),savepath)
	#im=Image.open(savepath)
	im_rotate=im_crop.rotate((180/math.pi)*rotateAngle,expand=True)
	newIm.paste(im_rotate,(offset,offset+head))
	#newIm.save(savepath)
			#print math.sin(rotateAngle)*formatHeight
			#print wgsDeltaX,offset+ wgsDeltaX*m.getPixelForMinuteLat()- math.sin(rotateAngle)*formatHeight,wgsLeft[0],int(wgsLeft[0])
	#print newIm.size[0]
	newIm = image_operator.drawXCoordinatePlank(newIm,m.getPixelForMinuteLat(),\
		init_coord=offset - wgsDeltaX*m.getPixelForMinuteLat() - math.sin(rotateAngle)*formatHeight,fixcoord=head+10,width=20)
	newIm = image_operator.drawYCoordinatePlank(newIm, m.getPixelForMinuteLon(),\
		init_coord=offset +  wgsDeltaY*m.getPixelForMinuteLon()+head,fixcoord=10,width=20)
	newIm = image_operator.drawYCoordinatePlank(newIm, m.getPixelForMinuteLon(),\
		init_coord=offset +  wgsDeltaY*m.getPixelForMinuteLon()+head,fixcoord=newIm.size[0]-10,width=20)
	newIm = image_operator.drawXCoordinatePlank(newIm,m.getPixelForMinuteLat(),\
		init_coord=offset - wgsDeltaX*m.getPixelForMinuteLat() - math.sin(rotateAngle)*formatHeight,fixcoord=newIm.size[1]-10,width=20)
			

	font = ImageFont.truetype(os.path.join(os.path.dirname(os.path.realpath(__file__)),"data","arial.ttf"), 30)
	#im = Image.open(savepath)
	draw  = ImageDraw.Draw(newIm)
	#print wgsLeft[1]-math.floor(wgsLeft[1]),str((wgsLeft[1]-math.floor(wgsLeft[1]))*60)
	draw.rectangle((0,0,formatWidth+offset*2,68),fill=0xffffffff)
	draw.text((0, 0), "N " + _wgsToStr(wgsLeft[1]), font=font,fill=0xff5533FF)
	draw.text((0, 33), "E " +_wgsToStr(wgsLeft[0]), font=font,fill=0xff5533FF)
			
	del draw
	newIm.save(savepath)
	

