#!/usr/bin/env python

import os, sys

from mirrorkan import parse_ckan_metadata_directory
from mirrorkan_conf import *
from mirrorkan_util import find_files_with_extension

def main():
    ckan_files, ckan_json = parse_ckan_metadata_directory(LOCAL_CKAN_PATH)
    
    for ckan_module in ckan_json:
        identifier = ckan_module[0]['identifier']
        print 'Generating API for module %s' % identifier
        
        root_path = os.path.join(API_PATH, identifier)
        if not os.path.exists(root_path):
            os.makedirs(root_path)
        
        version = ckan_module[0]['version'] 
        
        version_path = os.path.join(root_path, version)
        if not os.path.exists(version_path):
            os.makedirs(version_path)
    
if __name__ == "__main__":
    main()
