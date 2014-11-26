#!/usr/bin/env python

import os, sys

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

def append_ckan_build(script, mirrorkan_root):
    script.append("cd %s\n" % mirrorkan_root)
    
    script.append("rm CKAN -R\n")
    append_clone_repo(script, "https://github.com/KSP-CKAN/CKAN.git")
    script.append("cd CKAN\n")
    script.append("perl bin/build | $tee\n")

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
    script.append("python MirrorKAN/mirrorkan_parse_events.py %s MirrorKan/log.json | $tee\n" % log_path)

def main():
    if len(sys.argv) < 4:
        print 'Usage:'
        print sys.argv[0] + ' <target bash script> <log path> <mirrorkan root> <mirrorkan cache>'
        sys.exit(0)
    
    log_path = sys.argv[2]     
    mirrorkan_root = sys.argv[3]
    mirrorkan_cache = sys.argv[4]

    script = Script()
    append_tee_header(script, log_path)
    append_clean_up(script, log_path)
    append_ckan_build(script, mirrorkan_root)
    append_update_ckan_meta(script, mirrorkan_root)
    append_update_netkan(script, mirrorkan_root, mirrorkan_cache)
    append_push_ckan_meta(script, mirrorkan_root)
    append_parse_events(script, mirrorkan_root, log_path)
    append_update_mirrorkan(script, mirrorkan_root)
        
    with open(sys.argv[1], 'w') as script_file:
        script_file.write(script.text)

if __name__ == "__main__":
    main()
