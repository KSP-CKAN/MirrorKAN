#!/usr/bin/env python

import os, sys

from mirrorkan_log import *

def main():
    if len(sys.argv) < 2:
        print 'Usage:'
        print sys.argv[0] + ' <log_txt_path> <log_db_path>'
        sys.exit(0)
    
    log_txt_path = sys.argv[1]
    log_db_path = sys.argv[2]
    
    log = Log(log_db_path)
    
    print 'Parsing %s' % log_txt_path
    
    with open(log_txt_path, 'r') as log_txt_file:
        for line in log_txt_file.readlines():
            line = line.strip()
            print line
            
            if '): warning C' in line and '.cs(' in line:
                msg = 'Build warning: ' + line
                log.logWarning(msg)
                print msg
                continue
            elif 'FATAL CKAN.NetKAN' in line:
                msg = 'NetKAN error: ' + line
                log.logError(msg)
                print msg
                continue
            elif 'Build succeeded.' in line:
                msg = 'Build successful'
                log.logInfo(msg)
                print msg
                continue
    
    print 'Done!'
    
if __name__ == "__main__":
    main()
