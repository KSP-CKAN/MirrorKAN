#!/usr/bin/env python

import os, sys
from distutils.version import LooseVersion
from dateutil.parser import parse
from datetime import datetime, timedelta
import json
import operator
import pytz

from mirrorkan import parse_ckan_metadata_directory
from mirrorkan_conf import *
from mirrorkan_util import find_files_with_extension

def main():
    print 'Building CKAN-API..'

    ckan_files, ckan_json = parse_ckan_metadata_directory(LOCAL_CKAN_PATH)
    
    latest_versions = {}
    all_modules = {}
    latest_versions_by_identifier = {}
    
    for ckan_module in ckan_json:
        identifier = ckan_module[0]['identifier']
        version = ckan_module[0]['version']
        py_version = LooseVersion(version)
    
        if identifier in latest_versions:
            py_version2 = LooseVersion(latest_versions[identifier])
            if py_version > py_version2:
                print 'Version %s > %s' % (py_version, py_version2)
                latest_versions[identifier] = version
                latest_versions_by_identifier[identifier] = ckan_module
        else:
            latest_versions[identifier] = version
            latest_versions_by_identifier[identifier] = ckan_module
    
    for ckan_module in ckan_json:
        identifier = ckan_module[0]['identifier']
        print 'Generating API for module %s' % identifier
        
        root_path = os.path.join(API_PATH, identifier)
        
        if not os.path.exists(root_path):
            os.makedirs(root_path)
            
        version = ckan_module[0]['version']
        
        last_modified = 'unknown'
        try:
            last_modified = str(parse(ckan_module[0]['x_last_updated']))
        except:
            pass
        
        if identifier in all_modules:
             all_modules[identifier] += [ { 'version': version, 'path': '/%s/%s' % (identifier, version) } ]
        else:
            all_modules[identifier] = [ { 'version': version, 'path': '/%s/%s' % (identifier, version) } ]
        
        ckan_path = ckan_module[1]
        
        version_path = os.path.join(root_path, version)
        if os.path.exists(version_path):
            if os.path.isdir(version_path):
                os.removedirs(version_path)
            else:
                os.remove(version_path)
        
        local_path = os.path.join(LOCAL_CKAN_PATH, ckan_path)    
        print 'Symlink: %s -> %s' % (local_path, version_path)
        
        if os.path.exists(version_path):
            os.remove(version_path)
        
        os.symlink(local_path, version_path)
    
    for identifier, version in latest_versions.iteritems():
        root_path = os.path.join(API_PATH, identifier)
        version_path = os.path.join(root_path, version)
        latest_path = os.path.join(root_path, 'latest')
        
        if identifier in all_modules:
            all_modules[identifier] += [ { 'version': 'latest', 'path': '/%s/%s' % (identifier, version) } ]
        else:
            all_modules[identifier] = [ { 'version': 'latest', 'path': '/%s/%s' % (identifier, version) } ]
            
        print 'Symlink: %s -> %s' % (version_path, latest_path)
        
        if os.path.exists(latest_path):
            os.remove(latest_path)
        
        os.symlink(version_path, latest_path)
        
    all_path = os.path.join(API_PATH, 'all')
    with open(all_path, 'w') as all_file:
        print 'Writing %s' % all_path
        json.dump(all_modules, all_file)
    
    last_modified = {}
    
    for identifier, version in latest_versions.iteritems():
        ckan_module = latest_versions_by_identifier[identifier]
        parsed_date = None
        try:
            parsed_date = parse(ckan_module[0]['x_last_updated'])
        except:
            pass
            
        if parsed_date != None:
            now = pytz.utc.localize(datetime.now() - timedelta(hours=24))
            if parsed_date > now:
                last_modified['/%s/%s' % (identifier, version)] = str(parsed_date)
            
    last_modified = sorted(last_modified.items(), key=operator.itemgetter(1), reverse=True)

    pretty_last_modified = []
    for url, time in last_modified:
        pretty_last_modified += [ { 'module': url, 'last_updated': time } ]
    
    latest_path = os.path.join(API_PATH, 'latest')
    with open(latest_path, 'w') as latest_file:
        print 'Writing %s' % latest_path
        json.dump(pretty_last_modified, latest_file)
    
    print 'Done!'
    
if __name__ == "__main__":
    main()
