#!/usr/bin/env python

import os, sys

def make_config_file(config_path, master_repo, mirrorkan_root, master_root, lokal_ckan, mirror_path, local_url, index_header):
    cfg = """MASTER_REPO = '%s'
MIRRORKAN_ROOT = '%s'
MASTER_ROOT_PATH = '%s'
LOCAL_CKAN_PATH = '%s'
FILE_MIRROR_PATH = '%s'
LOCAL_URL_PREFIX = '%s'
INDEX_HTML_HEADER = '%s'""" % (master_repo, mirrorkan_root, master_root, lokal_ckan, mirror_path, local_url, index_header)

    with open(config_path, 'w') as config_file:
        config_file.write(cfg)

def ask_user(message, default):
    user = ''
    
    if default != None:
        user = raw_input('%s [%s]: ' % (message, default))
    else:
        user = raw_input('%s: ' % message)
        
    if user == '':
        user = default
    
    return user

def main():
    print 'Bootstrapping MirrorKAN in the current working directory'
    
    root = os.getcwd()
    print 'Root: ' + root
    
    config_path = os.path.join(os.path.join(root, "MirrorKAN"), "mirrorkan_conf.py")
    config_source = None
    
    db_path = os.path.join(os.path.join(root, "MirrorKAN"), "db.json")
    db_source = None
    
    if os.path.exists(config_path):
        with open(config_path, 'r') as config_file:
            config_source = config_file.read()
    
    if os.path.exists(db_path):
        with open(db_path, 'r') as db_file:
            db_source = db_file.read()
    
    os.system('rm -R MirrorKAN')
    os.system('git clone https://github.com/KSP-CKAN/MirrorKAN.git')
    
    print 'Preparing configuration'
    
    mirror_path = None
    
    if config_source == None:
        master_repo = ask_user("Set the CKAN master repository to mirror (url to master.zip)", "https://github.com/KSP-CKAN/CKAN-meta/archive/master.zip")
        
        master_root = os.path.join(root, 'master/')
        if not os.path.exists(master_root):
            os.makedirs(master_root)
        
        local_ckan = os.path.join(root, 'local_ckan/')
        
        if not os.path.exists(local_ckan):
            os.makedirs(local_ckan)
        
        mirror_path = ask_user("Set the local path where downloads will be mirrored (must be visible on the web)", '/var/ckan/mirror/')
        local_url = ask_user("Set the URL pointing to the mirror path", 'http://amsterdam.ksp-ckan.org/')
        index_header = ask_user("Enter a description for this repo", 'CKAN Mirror')
        
        print 'Writing mirrorkan_conf.py..',
        make_config_file(config_path, master_repo, root, master_root, local_ckan, mirror_path, local_url, index_header)
        print 'Done!'
    else:
        with open(config_path, 'w') as config_file:
            print 'Writing mirrorkan_conf.py.. (cached)',
            config_file.write(config_source)
            print 'Done!'
            
        for line in config_source.split('\n'):
            if 'FILE_MIRROR_PATH' in line:
                mirror_path = line.split('=')[1].strip().strip('\'')
    
    if db_source != None:
        with open(db_path, 'w') as db_file:
            print 'Writing db.json.. (cached)',
            db_file.write(db_source)
            print 'Done!'
    
    print 'Generating shell scripts..'
    generate_scripts_path = os.path.join(os.path.join(root, "MirrorKAN"), "generate_scripts.py")
    log_path = os.path.join(mirror_path, 'log.txt')
    
    with open(os.path.join(root, 'all.sh')), 'w') as all_sh_file:
        all_sh_file.write('#!/bin/sh\npython ' + generate_scripts_path + ' --clean --build-ckan --update-netkan --push-ckan-meta --update-mirrorkan --generate-index | sh\n')
        
    os.system('chmod a+x %s' % os.path.join(root, 'all.sh'))
    
    print 'Done!'
    
if __name__ == "__main__":
    main()
