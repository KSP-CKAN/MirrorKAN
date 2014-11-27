#!/usr/bin/env python

import os, sys
import argparse

from mirrorkan_conf import *

class Script:
    def __init__(self):
        self.text = '#!/bin/sh\n'
        
    def append(self, text):
        if text.split(' ')[0] != 'echo':
            self.text += 'echo "Executing: %s" | $tee\n' % text.split('\n')[0].split('|')[0].replace('"', '').replace('`', '\\`')
        self.text += text + '\n'
      
    def append_nolog(self, text):
        self.text += text + '\n'

def append_clean_up(script, log_path):
    script.append('rm %s' % log_path)

def append_tee_header(script, log_path):
    script.append("tee='tee -a %s'" % log_path)
    
def append_clone_repo(script, repo):
    script.append("git clone %s 2>&1 | $tee" % repo)
    
def append_update_mirrorkan(script, mirrorkan_root):
    script.append("cd %s" % mirrorkan_root)
    script.append("cd MirrorKAN")
    script.append("python mirrorkan.py | $tee")

def append_ckan_build(script, mirrorkan_root, mirrorkan_cache, ckan_repo):
    script.append("cd %s" % mirrorkan_root)
    
    script.append("rm CKAN -R")
    append_clone_repo(script, ckan_repo)
    script.append("cd CKAN")
    script.append("perl bin/build 2>&1 | $tee")
    script.append("cp %s %s" % ("ckan.exe", mirrorkan_cache))
    script.append("cp %s %s" % ("netkan.exe", mirrorkan_cache))

def append_update_ckan_meta(script, mirrorkan_root, ckan_meta_repo):
    script.append("cd %s" % mirrorkan_root)
    script.append("rm CKAN-meta -R")
    append_clone_repo(script, ckan_meta_repo)
    
def append_update_netkan(script, mirrorkan_root, mirrorkan_cache, netkan_repo, file_list):
    script.append("cd %s" % mirrorkan_root)
    
    netkan_exe_path = os.path.join(os.path.join(mirrorkan_root, "CKAN"), "netkan.exe")
    netkans_path = os.path.join(mirrorkan_root, "NetKAN")
    output_path = os.path.join(mirrorkan_root, "CKAN-meta")
    
    script.append("rm NetKAN -R")
    append_clone_repo(script, netkan_repo)
    script.append("cd NetKAN")
    script.append("cd NetKAN")
    
    auth = ""
    token_path = os.path.join(os.path.join(mirrorkan_root, "MirrorKAN"), "github.token")
    
    if os.path.exists(token_path):
        auth = "--github-token=`cat \"%s\"`" % token_path
        script.append("echo Using GitHub OAuth token")
    
    if file_list == None:   
        script.append_nolog("for f in *.netkan")
        script.append_nolog("do")
        script.append("mono --debug %s %s/NetKAN/$f --cachedir=%s --outputdir=%s %s 2>&1 | $tee" % (netkan_exe_path, netkans_path, mirrorkan_cache, output_path, auth))
        script.append_nolog("done")
    else:
        for item in file_list:
            script.append("mono --debug %s %s/%s --cachedir=%s --outputdir=%s %s 2>&1 | $tee" % (netkan_exe_path, netkans_path, item, mirrorkan_cache, output_path, auth))

def append_push_ckan_meta(script, mirrorkan_root):
    script.append("cd %s" % mirrorkan_root)
    script.append("cd CKAN-meta")
    script.append("git add * 2>&1 | $tee")
    script.append("git commit -m \"NetKAN generated mods\" 2>&1 | $tee")
    script.append("git push 2>&1 | $tee")

def append_parse_events(script, mirrorkan_root, log_path):
    script.append("cd %s" % os.path.join(mirrorkan_root, "MirrorKAN"))
    script.append("python mirrorkan_parse_events.py %s log.json | $tee" % log_path)

def append_generate_index(script, mirrorkan_root):
    script.append("cd %s\n" % os.path.join(mirrorkan_root, "MirrorKAN"))
    script.append("python mirrorkan_generate_index.py | $tee")

def append_generate_api(script, mirrorkan_root):
    script.append("cd %s\n" % os.path.join(mirrorkan_root, "MirrorKAN"))
    script.append("python mirrorkan_generate_api.py | $tee")

def main():
    parser = argparse.ArgumentParser(description='Generate MirrorKAN scripts')
    parser.add_argument('--clean', dest='clean', action='store_true', help='Clean-up build artifacts')

    parser.add_argument('--build-ckan', dest='build_ckan', action='store_true', help='Builds CKAN and NetKAN')
    parser.add_argument('--ckan-repository', dest='ckan_repository', action='store', help='Overrides the default CKAN repository')
    
    parser.add_argument('--update-ckan-meta', dest='update_ckan_meta', action='store_true', help='Fetches latest CKAN-meta')
    
    parser.add_argument('--update-netkan', dest='update_netkan', action='store_true', help='Builds all NetKAN metadata')
    parser.add_argument('--netkan-repository', dest='netkan_repository', action='store', help='Overrides the default NetKAN repository')
    parser.add_argument('--netkan-file-list', dest='netkan_file_list', action='store', help='Provide a list of files to be updated, if omitted will update all')

    parser.add_argument('--push-ckan-meta', dest='push_ckan_meta', action='store_true', help='Pushes all new data to CKAN-meta')
    parser.add_argument('--ckan-meta-repository', dest='ckan_meta_repository', action='store', help='Overrides the default CKAN-meta repository')

    parser.add_argument('--update-mirrorkan', dest='update_mirrorkan', action='store_true', help='Updates MirrorKAN')

    parser.add_argument('--generate-index', dest='generate_index', action='store_true', help='Generate index.html')

    parser.add_argument('--generate-api', dest='generate_api', action='store_true', help='Generate CKAN-API')
    
    parser.add_argument('--output', dest='output', action='store', help='Output file path, if omitted will print to stdout')
    args = parser.parse_args()
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    log_path = os.path.join(FILE_MIRROR_PATH, "log.txt")
    
    script = Script()
    append_tee_header(script, log_path)
    
    if args.clean:
        append_clean_up(script, log_path)
    
    if args.build_ckan:
        repo = "https://github.com/KSP-CKAN/CKAN.git"
        if args.ckan_repository != None:
            repo = args.ckan_repository
        append_ckan_build(script, MIRRORKAN_ROOT, FILE_MIRROR_PATH, repo)
    
    if args.update_ckan_meta:
        repo = "https://github.com/KSP-CKAN/CKAN-meta.git"
        if args.ckan_meta_repository != None:
            repo = args.ckan_meta_repository
        append_update_ckan_meta(script, MIRRORKAN_ROOT, repo)

    if args.update_netkan:
        if not args.update_ckan_meta:
            repo = "https://github.com/KSP-CKAN/CKAN-meta.git"
            if args.ckan_meta_repository != None:
                repo = args.ckan_meta_repository
            append_update_ckan_meta(script, MIRRORKAN_ROOT, repo)
        
        repo = "https://github.com/KSP-CKAN/NetKAN.git"
        if args.netkan_repository != None:
            repo = args.netkan_repository
        file_list = None
        
        if args.netkan_file_list != None:
            file_list = []
            for item in args.netkan_file_list.split(','):
                if len(item.strip()) > 0:
                    file_list += [item.strip()]
            
        append_update_netkan(script, MIRRORKAN_ROOT, FILE_MIRROR_PATH, repo, file_list)
    
    if args.push_ckan_meta:
        append_push_ckan_meta(script, MIRRORKAN_ROOT)
    
    if args.update_mirrorkan:
        append_parse_events(script, MIRRORKAN_ROOT, log_path)
        append_update_mirrorkan(script, MIRRORKAN_ROOT)
        
    if args.generate_index:
        append_generate_index(script, MIRRORKAN_ROOT)
        
    if args.generate_api:
        append_generate_api(script, MIRRORKAN_ROOT)
        
    if args.output == None:
        print script.text
    else:
        with open(args.output, 'w') as output_file:
            output_file.write(script.text)

if __name__ == "__main__":
    main()
