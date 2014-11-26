#!/usr/bin/env python

import os, sys
import argparse

from mirrorkan_conf import *

class Script:
    def __init__(self):
        self.text = ''
        
    def append(self, text):
        if text.split(' ')[0] != 'echo':
            self.text += 'echo "Executing: %s" | $tee\n' % text.split('\n')[0].split('|')[0].replace('"', '')
        self.text += text
      
    def append_nolog(self, text):
        self.text += text

def append_clean_up(script, log_path):
    script.append('rm %s\n' % log_path)

def append_tee_header(script, log_path):
    script.append("tee='tee -a %s'\n" % log_path)
    
def append_clone_repo(script, repo):
    script.append("git clone %s 2>&1 | $tee\n" % repo)
    
def append_update_mirrorkan(script, mirrorkan_root):
    script.append("cd %s\n" % mirrorkan_root)
    script.append("cd MirrorKAN\n")
    script.append("python mirrorkan.py | $tee")

def append_ckan_build(script, mirrorkan_root, mirrorkan_cache):
    script.append("cd %s\n" % mirrorkan_root)
    
    script.append("rm CKAN -R\n")
    append_clone_repo(script, "https://github.com/KSP-CKAN/CKAN.git")
    script.append("cd CKAN\n")
    script.append("perl bin/build | $tee\n")
    script.append("cp %s %s\n" % ("ckan.exe", mirrorkan_cache))
    script.append("cp %s %s\n" % ("netkan.exe", mirrorkan_cache))

def append_update_ckan_meta(script, mirrorkan_root):
    script.append("cd %s\n" % mirrorkan_root)
    script.append("rm CKAN-meta -R\n")
    append_clone_repo(script, "https://github.com/KSP-CKAN/CKAN-meta.git")
    
def append_update_netkan(script, mirrorkan_root, mirrorkan_cache):
    script.append("cd %s\n" % mirrorkan_root)
    
    netkan_exe_path = os.path.join(os.path.join(mirrorkan_root, "CKAN"), "netkan.exe")
    netkans_path = os.path.join(os.path.join(mirrorkan_root, "NetKAN"), "NetKAN")
    output_path = os.path.join(mirrorkan_root, "CKAN-meta")
    
    script.append("rm NetKAN -R\n")
    append_clone_repo(script, "https://github.com/KSP-CKAN/NetKAN.git")
    script.append("cd NetKAN\n")
    script.append("cd NetKAN\n")
    script.append_nolog("for f in *.netkan\n")
    script.append_nolog("do\n")
    script.append("%s %s/$f --cachedir=%s --outputdir=%s | $tee\n" % (netkan_exe_path, netkans_path, mirrorkan_cache, output_path))
    script.append_nolog("done\n")

def append_push_ckan_meta(script, mirrorkan_root):
    script.append("cd %s\n" % mirrorkan_root)
    script.append("cd CKAN-meta\n")
    script.append("git add * 2>&1 | $tee\n")
    script.append("git commit -m \"NetKAN generated mods\" 2>&1 | $tee\n")
    script.append("git push 2>&1 | $tee\n")

def append_parse_events(script, mirrorkan_root, log_path):
    script.append("cd %s\n" % mirrorkan_root)
    script.append("python MirrorKAN/mirrorkan_parse_events.py %s MirrorKAN/log.json | $tee\n" % log_path)

def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--clean', dest='clean', action='store_true', help='Clean-up build artifacts')
    parser.add_argument('--build-ckan', dest='build_ckan', action='store_true', help='Builds CKAN and NetKAN')
    parser.add_argument('--update-netkan', dest='update_netkan', action='store_true', help='Builds all NetKAN metadata')
    parser.add_argument('--push-ckan-meta', dest='push_ckan_meta', action='store_true', help='Pushes all new data to CKAN-meta')
    parser.add_argument('--update-mirrorkan', dest='update_mirrorkan', action='store_true', help='Updates MirrorKAN')
    args = parser.parse_args()

    log_path = os.path.join(FILE_MIRROR_PATH, "log.txt")
    
    script = Script()
    append_tee_header(script, log_path)
    
    if args.clean == True:
        append_clean_up(script, log_path)
    
    if args.build_ckan == True:
        append_ckan_build(script, MIRRORKAN_ROOT, FILE_MIRROR_PATH)
    
    if args.update_ckan_meta == True:
        append_update_ckan_meta(script, MIRRORKAN_ROOT)

    if args.update_netkan == True:
        append_update_netkan(script, MIRRORKAN_ROOT, FILE_MIRROR_PATH)
    
    if args.push_ckan_meta == True:
        append_push_ckan_meta(script, MIRRORKAN_ROOT)
    
    if args.update_mirrorkan == True:
        append_parse_events(script, MIRRORKAN_ROOT, log_path)
        append_update_mirrorkan(script, MIRRORKAN_ROOT)
        
    print script.text

if __name__ == "__main__":
    main()
