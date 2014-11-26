#!/usr/bin/env python

import os, sys
from os import listdir
from os.path import isfile, join
import tempfile
from urllib2 import urlopen, URLError, HTTPError
import zipfile
import json
import datetime
from dateutil.parser import parse
from email.Utils import formatdate
from hashlib import sha1

from mirrorkan_conf import *
from mirrorkan_db import *
from mirrorkan_log import *
from mirrorkan_util import zipdir, download_file, find_files_with_extension

db = Database('db.json')
log = Log('log.json')
   
DLRESULT_SUCCESS = 1
DLRESULT_CACHED = 2
DLRESULT_HTTP_ERROR_CACHED = 3
DLRESULT_HTTP_ERROR_NOT_CACHED = 4

def download_mod(url, path, filename):
    print 'Downloading ' + url
    
    f = None
    
    error = None
    
    is_cached = db.is_cached(url)
    
    # Open the url
    try:
        f = urlopen(url)
    except HTTPError, e:
        error = e
        print str(e) + ': ' + url
    except URLError, e:
        error = e
        print str(e) + ': ' + url
    
    if error is not None:
        if is_cached:
            return DLRESULT_HTTP_ERROR_CACHED
        else:
            return DLRESULT_HTTP_ERROR_NOT_CACHED
    
    should_download = False
    
    if 'last-modified' in f.headers:
        last_modified = f.headers['last-modified']
        print 'last-modified header time: ' + last_modified
        
        db_last_modified = db.get_lastmodified(url)
        if db_last_modified != None:
            print 'database last modified time: ' + db_last_modified
        
        if not db.is_newer(url, last_modified):
            return DLRESULT_CACHED
        
        db.add_mod(url, filename, last_modified)
    elif is_cached:
        return DLRESULT_CACHED
    else:
        db.add_mod(url, filename, 'LastModifiedHeaderMissing')
     
    download_file(url, path, filename)
    
    return DLRESULT_SUCCESS
   
def parse_ckan_metadata(filename):
    data = None
    
    with open(filename) as json_file:
        data = json.load(json_file)
        
    return data
    
def parse_ckan_metadata_directory(path):
    print 'Looking for .ckan metadata files in ' + path
    ckan_files = find_files_with_extension(path, '.ckan')
    print 'Found %i metadata files' % len(ckan_files)
    
    ckan_json = []
    
    for ckan_file in ckan_files:
        print 'Parsing "%s"' % ckan_file
        ckan_module = parse_ckan_metadata(ckan_file)
        ckan_json += [[ckan_module, ckan_file]]
        
    return (ckan_files, ckan_json)
    
def clean_up():
    print 'Cleaning up...',
    os.system('rm -R ' + LOCAL_CKAN_PATH + '/*')
    os.system('rm -R ' + MASTER_ROOT_PATH + '/*')
    print 'Done!'
    
def fetch_and_extract_master(master_repo, root_path):
    print 'Fetching remote master..',
    download_file(master_repo, '', 'master.zip')
    print 'Done!'
    
    with zipfile.ZipFile('master.zip', 'r') as zip_file:
        print 'Extracting master.zip..',
        zip_file.extractall(root_path)
        print 'Done!'

def dump_all_modules(ckan_files, ckan_json):
    for ckan_module in ckan_json:
        identifier = ckan_module[0]['identifier']
        version = ckan_module[0]['version']
        download_url = ckan_module[0]['download']
        mod_license = ckan_module[0]['license'] 
        
        ckan_module[0]['x_mirrorkan_download'] = download_url
        
        hasher = sha1()
        hasher.update(download_url.encode('utf-8'))
        url_hash = hasher.hexdigest()[:8].upper()
      
        filename = url_hash + '-' + identifier + '-' + version + '.zip'
        ckan_module[0]['x_mirrorkan_cached_filename'] = filename
        
        download_file_url = LOCAL_URL_PREFIX + filename
        
        last_updated = db.get_lastmodified(download_url)
        if last_updated is not None:
            ckan_module[0]['x_mirrorkan_last_updated'] = last_updated
        else:
            ckan_module[0]['x_mirrorkan_last_updated'] = 'NotAvailable'
            
        if mod_license is not 'restricted' and mod_license is not 'unknown':
            file_status = download_mod(download_url, FILE_MIRROR_PATH, filename)
            
            ckan_module[0]['download'] = download_file_url
            ckan_module[0]['x_alt_download'] = download_url
            ckan_module[0]['x_mirrorkan_download_status'] = file_status
            
            if file_status is DLRESULT_SUCCESS:
                print 'Success!'
                ckan_module[0]['x_mirrorkan_status'] = 'JustUpdated'
            elif file_status is DLRESULT_CACHED:
                ckan_module[0]['x_mirrorkan_status'] = 'Cached'
                print 'Cached'
            elif file_status is DLRESULT_HTTP_ERROR_CACHED:
                ckan_module[0]['x_mirrorkan_status'] = 'CachedHttpError'
                log.logError('Processing module %s resulted in an HTTP error but we have the url in the cache' % identifier)
                print 'HTTP Error (Cached)'
            elif file_status is DLRESULT_HTTP_ERROR_NOT_CACHED:
                print 'HTTP Error (Not cached)'
                ckan_module[0]['x_mirrorkan_status'] = 'NotCachedHttpError'
                log.logError('Processing module %s (%s) resulted in an HTTP error and the url is not cached, skipping..' % (identifier, ckan_module[0]['version']))
                continue
        else:
            log.logWarning('Module %s has a non-permissive license so we are not allowed to cache it' % identifier)
            
        print 'Dumping json for ' + identifier

        with open(os.path.join(LOCAL_CKAN_PATH, os.path.basename(ckan_module[1])), 'w') as out_ckan:
            json.dump(ckan_module[0], out_ckan)

def create_master_zip(path, sourceDir):
    print 'Creating new master.zip'
    
    zipf = zipfile.ZipFile(path, 'w')
    zipdir(sourceDir, zipf)
    zipf.close()
    
def update(master_repo, root_path, mirror_path):  
    if not os.path.exists(MASTER_ROOT_PATH):
        os.makedirs(MASTER_ROOT_PATH)
    if not os.path.exists(LOCAL_CKAN_PATH):
        os.makedirs(LOCAL_CKAN_PATH)
    if not os.path.exists(FILE_MIRROR_PATH):
        os.makedirs(FILE_MIRROR_PATH)
        
    clean_up()
    fetch_and_extract_master(master_repo, root_path)
  
    ckan_files, ckan_json = parse_ckan_metadata_directory(os.path.join(root_path, 'CKAN-meta-master'))
    dump_all_modules(ckan_files, ckan_json)
    
    log.logInfo('Processed %d modules' % len(ckan_json))
    log.logInfo('Last update: %s UTC' % str(datetime.datetime.utcnow()))
    
    create_master_zip(os.path.join(FILE_MIRROR_PATH, 'master.zip'), LOCAL_CKAN_PATH)
    
    print 'Done!'

def main():
    print 'Using "%s" as a remote' % MASTER_REPO
    print 'Master root is "%s"' % MASTER_ROOT_PATH
    print

    update(MASTER_REPO, MASTER_ROOT_PATH, FILE_MIRROR_PATH)

if __name__ == "__main__":
    main()
