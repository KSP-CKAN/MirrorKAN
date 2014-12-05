#!/usr/bin/env python

import os, sys
import datetime

from mirrorkan import parse_ckan_metadata_directory
from mirrorkan_conf import *
from mirrorkan_log import *

log = Log('log.json')

DLRESULT_SUCCESS = 1
DLRESULT_CACHED = 2
DLRESULT_HTTP_ERROR_CACHED = 3
DLRESULT_HTTP_ERROR_NOT_CACHED = 4

def main():
    ckan_files, ckan_json = parse_ckan_metadata_directory(LOCAL_CKAN_PATH)
    
    index = '<html>'
    index += '<head>'
    index += '<link rel="alternate" type="application/rss+xml" title="RSS" href="' + LOCAL_URL_PREFIX + 'feed/ckan.rss" />'
    index += '</head>'
    index += '<body>'
    index += INDEX_HTML_HEADER + '<br/>&nbsp;<br/>'
    index += '<a href="' + LOCAL_URL_PREFIX + 'master.zip">master.zip</a><br/>'
    index += '<a href="' + LOCAL_URL_PREFIX + 'ckan.exe">ckan.exe</a> | <a href="' + LOCAL_URL_PREFIX + 'netkan.exe">netkan.exe</a><br/>'
    index += '<a href="' + LOCAL_URL_PREFIX + 'ckan.rss">RSS Feed</a><br/>&nbsp;<br/>'
    index += '<a href="' + LOCAL_URL_PREFIX + 'log.txt">MirrorKAN log</a><br/>&nbsp;<br/>'
    
    info = log.getInfo()
    
    index += '<font style="color: #669900; font-weight: normal;">Info:<br/>'
    for item in info:
        index += item + '<br/>'
    index += '</font><br/>'

    warnings = log.getWarnings()
    index += '<font style="color: #CC3300; font-weight: normal;">Warnings:<br/>'
    for item in warnings:
        index += item + '<br/>'
    index += '</font><br/>'
    
    errors = log.getErrors()
    index += '<font style="color: #CC3300; font-weight: bold;">Errors:<br/>'
    for item in errors:
        index += item + '<br/>'
    index += '</font><br/><br/>'
    
    index += 'Modules list:<br/>'
    
    for ckan_module in ckan_json:
        identifier = ckan_module[0]['identifier']
        print 'Generating info for module %s' % identifier
        
        version = ckan_module[0]['version']
        filename = ckan_module[0]['x_mirrorkan_cached_filename']
        
        file_status = ckan_module[0]['x_mirrorkan_download_status']
        
        style = "color: #339900;"
        if file_status is DLRESULT_HTTP_ERROR_NOT_CACHED:
            style = "color: #CC3300; font-weight: bold;"
        elif file_status is DLRESULT_HTTP_ERROR_CACHED:
            style = "color: #FFD700; font-weight: bold;"
        
        index += '<font style="' + style + '">'
        
        index += '&nbsp;' + identifier + ' - ' + version + ' - '
        index += 'Status: ' + ckan_module[0]['x_mirrorkan_status'] + '(' + str(ckan_module[0]['x_mirrorkan_download_status']) + ') - '
        index += 'Last update: ' + ckan_module[0]['x_last_updated'] + '<br/>'
        
        index += '</font>'
    
    index += '</body></html>'

    index_file_path = os.path.join(FILE_MIRROR_PATH, 'index.html')
    print 'Writing %s' % index_file_path
    index_file = open(index_file_path, 'w')
    index_file.write(index)
    index_file.close()
    
if __name__ == "__main__":
    main()
