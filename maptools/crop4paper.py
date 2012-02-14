#!/usr/bin/python
#import maptools.minimap
import sys
import os
import argparse
import os
import maptools.minimap

def paperCoord(string):
	coord = string.split("x")
	
	if  coord[0].isdigit() and coord[1].isdigit():
		return [int(coord[0]),int(coord[1])]
	else:
		msg = "%r is not a perfect coordinate. Use like this 1000x1000" % string
		raise argparse.ArgumentTypeError(msg)



if __name__ == "__main__":
	argv = sys.argv
	#if (len(argv)<3):
	#	print "Few argument. Use program as: addminimap [directory-path] [map-path]"
	#	exit(0)
	amap={"--format","--coord"}
	parser = argparse.ArgumentParser(description='Create some map for print on standart paper format (a4,a3) and add coordinate plank for it')
	#parser.add_argument('MAP_PATH', required=True)
	parser.add_argument("MAP_PATH", nargs=1, type=argparse.FileType('r'), help="path to map")
	parser.add_argument('--format', choices=["a3","a4"], nargs=1,default="a4",
							help='paper format')
	parser.add_argument('--coord', type=paperCoord,
                   help='coordinate of left top corner of paper on map. If is not set, map all cropping.')

	args = parser.parse_args()
	

	maptools.minimap.splitA4All(os.path.abspath(args.MAP_PATH[0].name),format=minimap.PaperFormat.A3)
	 #print args.accumulate(args.integers)
	#for option in amap:
	#	if not option in argv:
	#		print "Invalid option " + str(option)
	
	#print dir(amap)
	#for a in argv[1:]:
	#	pass
