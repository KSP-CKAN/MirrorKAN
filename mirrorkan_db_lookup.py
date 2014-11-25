#!/usr/bin/env python

import os, sys

from mirrorkan_db import *

def main():
	if len(sys.argv) < 3:
		print 'Usage:'
		print sys.argv[0] + ' <database> <url>'
		sys.exit(0)
	
	db = Database(sys.argv[1])
	if not db.is_cached(sys.argv[2]):
		print 'NotFound'
		sys.exit(1)
		
	print db.get_filename(sys.argv[2])
	sys.exit(0)
	
if __name__ == "__main__":
	main()
