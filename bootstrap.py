#!/usr/bin/env python

import os, sys

def make_config_file(config_path, master_repo, master_root, lokal_ckan, mirror_path, local_url, index_header):
    cfg = """MASTER_REPO = '%s'
MASTER_ROOT_PATH = '%s'
LOCAL_CKAN_PATH = '%s'
FILE_MIRROR_PATH = '%s'
LOCAL_URL_PREFIX = '%s'
INDEX_HTML_HEADER = '%s'""" % (master_repo, master_root, lokal_ckan, mirror_path, local_url, index_header)

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
    
    if os.path.exists(config_path):
        with open(config_path, 'r') as config_file:
            config_source = config_file.read()
    
    os.system('wget https://github.com/KSP-CKAN/MirrorKAN/archive/master.zip')
    os.system('unzip -o master.zip')
    os.system('rm master.zip')
    os.system('mv MirrorKAN-master MirrorKAN')
    
    print 'Preparing configuration'
    
    master_repo = ask_user("Set the CKAN master repository to mirror (url to master.zip)", "https://github.com/KSP-CKAN/CKAN-meta/archive/master.zip")
    
    if config_source == None:
        master_root = os.path.join(root, 'master')
        if not os.path.exists(master_root):
            os.makedirs(master_root)
        
        local_ckan = os.path.join(root, 'local_ckan')
        
        if not os.path.exists(local_ckan):
            os.makedirs(local_ckan)
        
        mirror_path = ask_user("Set the local path where downloads will be mirrored (must be visible on the web)", None)
        local_url = ask_user("Set the URL pointing to the mirror path", None)
        index_header = ask_user("Enter a description for this repo", None)
        
        print 'Writing mirrorkan_conf.py..',
        make_config_file(config_path, master_repo, master_root, local_ckan, mirror_path, local_url, index_header)
        print 'Done!'
    else:
        with open(config_path, 'w') as config_file:
            print 'Writing mirrorkan_conf.py.. (cached)',
            config_file.write(config_source)
            print 'Done!'
    
    print 'Generating shell scripts..'
    generate_scripts_path = os.path.join(os.path.join(root, "MirrorKAN"), "generate_scripts.py")
    log_path = os.path.join(mirror_path, 'log.txt')
    os.system('python ' + generate_scripts_path + ' "' + os.path.join(root, 'all.sh') + '" "' + log_path + '" "' + root + '" "' + mirror_path + '"')
    print 'Done!'
    
if __name__ == "__main__":
    main()
