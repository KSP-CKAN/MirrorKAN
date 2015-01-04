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
    script.append("set -e")
    script.append("git clone --recursive %s 2>&1 | $tee" % repo)
    script.append("set +e")
    
def append_update_mirrorkan(script, mirrorkan_root):
    script.append("cd %s" % mirrorkan_root)
    script.append("cd MirrorKAN")
    script.append("python mirrorkan.py | $tee")

def append_ckan_download(script, mirrorkan_root, output_path, ckan_url, netkan_url):
    script.append("cd %s" % mirrorkan_root)
    script.append("wget -O ckan.exe %s" % ckan_url)
    script.append("wget -O netkan.exe %s" % netkan_url)
    script.append("cp ckan.exe %s" % output_path)
    script.append("cp netkan.exe %s" % output_path)

def append_update_ckan_meta(script, mirrorkan_root, ckan_meta_repo):
    script.append("cd %s" % mirrorkan_root)
    script.append("rm CKAN-meta -R")
    append_clone_repo(script, ckan_meta_repo)
    
def append_update_netkan(script, mirrorkan_root, mirrorkan_cache, netkan_repo, netkan_opts, file_list):
    script.append("cd %s" % mirrorkan_root)
    
    netkan_exe_path = os.path.join(mirrorkan_root, "netkan.exe")
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
        script.append("mono --debug %s \"%s/NetKAN/$f\" --cachedir=%s --outputdir=\"%s/$(basename -s .netkan \"$f\")/\" %s %s 2>&1 | $tee" % (netkan_exe_path, netkans_path, mirrorkan_cache, output_path, netkan_opts, auth))
        script.append_nolog("done")
    else:
        for item in file_list:
            out_dir = os.path.join(output_path, os.path.splitext(os.path.basename(item))[0])
            script.append("if [ ! -d %s ]" % out_dir)
            script.append("then")
            script.append("mkdir %s" % out_dir)
            script.append("fi")
            script.append("mono --debug %s \"%s/%s\" --cachedir=%s --outputdir=%s %s %s 2>&1 | $tee" % (netkan_exe_path, netkans_path, item, mirrorkan_cache, out_dir, netkan_opts, auth))

def append_push_ckan_meta(script, mirrorkan_root):
    script.append("set -e")
 
    script.append("cd %s" % mirrorkan_root)
    script.append("cd CKAN-meta")
    script.append("git add * 2>&1 | $tee")
    script.append("wget --quiet https://raw.githubusercontent.com/KSP-CKAN/CKAN/master/bin/ckan-validate.py -O ckan-validate.py")
    script.append("wget --quiet https://raw.githubusercontent.com/KSP-CKAN/CKAN/master/CKAN.schema -O CKAN.schema")
    script.append("chmod a+x ckan-validate.py")
    script.append("./ckan-validate.py `git diff --name-only --stat origin/master`")
    script.append("rm ckan-validate.py")
    script.append("rm CKAN.schema")
    
    commit_message = '`python %s/MirrorKAN/generate_commit_message.py`' % mirrorkan_root
    script.append("git commit -m \"NetKAN generated mods - %s\" 2>&1 | $tee" % commit_message)
    script.append("git push 2>&1 | $tee")
    script.append("set +e")

def append_parse_events(script, mirrorkan_root, log_path):
    script.append("cd %s" % os.path.join(mirrorkan_root, "MirrorKAN"))
    script.append("python mirrorkan_parse_events.py %s log.json | $tee" % log_path)

def append_generate_index(script, mirrorkan_root):
    script.append("cd %s\n" % os.path.join(mirrorkan_root, "MirrorKAN"))
    script.append("python mirrorkan_generate_index.py | $tee")

def append_generate_api(script, mirrorkan_root):
    script.append("cd %s\n" % os.path.join(mirrorkan_root, "MirrorKAN"))
    script.append("python mirrorkan_generate_api.py | $tee")

def append_generate_feed(script, mirrorkan_root):
    script.append("cd %s\n" % os.path.join(mirrorkan_root, "MirrorKAN"))
    script.append("python mirrorkan_generate_feed.py | $tee")

def main():
    parser = argparse.ArgumentParser(description='Generate MirrorKAN scripts')
    parser.add_argument('--log', dest='log_path', action='store', help='Set the log path')
    
    parser.add_argument('--clean', dest='clean', action='store_true', help='Clean-up build artifacts')

    parser.add_argument('--ckan-url', dest='ckan_url', action='store', help='Overrides the default CKAN.exe download url')
    parser.add_argument('--netkan-url', dest='netkan_url', action='store', help='Overrides the default NetKAN.exe download url')
    parser.add_argument('--ckan-output', dest='ckan_output', action='store', help='Sets the CKAN.exe/NetKAN.exe destination directory')
    
    parser.add_argument('--update-ckan-meta', dest='update_ckan_meta', action='store_true', help='Fetches latest CKAN-meta')
    
    parser.add_argument('--update-netkan', dest='update_netkan', action='store_true', help='Builds all NetKAN metadata')
    parser.add_argument('--netkan-repository', dest='netkan_repository', action='store', help='Overrides the default NetKAN repository')
    parser.add_argument('--netkan-file-list', dest='netkan_file_list', action='store', help='Provide a list of files to be updated, if omitted will update all')

    parser.add_argument('--push-ckan-meta', dest='push_ckan_meta', action='store_true', help='Pushes all new data to CKAN-meta')
    parser.add_argument('--ckan-meta-repository', dest='ckan_meta_repository', action='store', help='Overrides the default CKAN-meta repository')

    parser.add_argument('--netkan_opts', dest='netkan_opts', action='store', help='Optional additional flags to netkan')

    parser.add_argument('--update-mirrorkan', dest='update_mirrorkan', action='store_true', help='Updates MirrorKAN')

    parser.add_argument('--generate-index', dest='generate_index', action='store_true', help='Generate index.html')

    parser.add_argument('--generate-api', dest='generate_api', action='store_true', help='Generate CKAN-API')
    
    parser.add_argument('--generate-feed', dest='generate_feed', action='store_true', help='Generate CKAN RSS Feed')

    parser.add_argument('--output', dest='output', action='store', help='Output file path, if omitted will print to stdout')
    args = parser.parse_args()
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    log_path = os.path.join(FILE_MIRROR_PATH, "log.txt")
    if args.log_path != None:
        log_path = args.log_path
    
    script = Script()
    append_tee_header(script, log_path)
    
    if args.clean:
        append_clean_up(script, log_path)
    
    ckan_url = 'http://ci.ksp-ckan.org:8080/job/CKAN/lastSuccessfulBuild/artifact/ckan.exe'
    netkan_url = 'http://ci.ksp-ckan.org:8080/job/NetKAN/lastSuccessfulBuild/artifact/netkan.exe'
    
    if args.ckan_url != None:
        ckan_url = args.ckan_url
    
    if args.netkan_url != None:
        netkan_url = args.netkan_url
    
    output_path = FILE_MIRROR_PATH
    if args.ckan_output != None:
        output_path = args.ckan_output
    
    append_ckan_download(script, MIRRORKAN_ROOT, output_path, ckan_url, netkan_url)
    
    if args.update_ckan_meta:
        repo = "git@github.com:KSP-CKAN/CKAN-meta"
        if args.ckan_meta_repository != None:
            repo = args.ckan_meta_repository
        append_update_ckan_meta(script, MIRRORKAN_ROOT, repo)

    if args.update_netkan:
        if not args.update_ckan_meta:
            repo = "git@github.com:KSP-CKAN/CKAN-meta"
            if args.ckan_meta_repository != None:
                repo = args.ckan_meta_repository
            append_update_ckan_meta(script, MIRRORKAN_ROOT, repo)
        
        repo = "git@github.com:KSP-CKAN/NetKAN"
        if args.netkan_repository != None:
            repo = args.netkan_repository

        netkan_opts = NETKAN_OPTS
        if args.netkan_opts != None:
            netkan_opts = args.netkan_opts

        file_list = None
        
        if args.netkan_file_list != None:
            file_list = []
            for item in args.netkan_file_list.split(','):
                if len(item.strip()) > 0:
                    file_list += [item.strip()]
            
        append_update_netkan(script, MIRRORKAN_ROOT, FILE_MIRROR_PATH, repo, netkan_opts, file_list)
    
    if args.push_ckan_meta:
        append_push_ckan_meta(script, MIRRORKAN_ROOT)
    
    if args.update_mirrorkan:
        append_parse_events(script, MIRRORKAN_ROOT, log_path)
        append_update_mirrorkan(script, MIRRORKAN_ROOT)
        
    if args.generate_index:
        append_generate_index(script, MIRRORKAN_ROOT)

    if args.generate_api:
        append_generate_api(script, MIRRORKAN_ROOT)
        
    if args.generate_feed:
        append_generate_feed(script, MIRRORKAN_ROOT)

    if args.output == None:
        print script.text
    else:
        with open(args.output, 'w') as output_file:
            output_file.write(script.text)

if __name__ == "__main__":
    main()
