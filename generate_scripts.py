#!/usr/bin/env python

import os, sys

class Script:
	def __init__(self):
		self.text = ''
		
	def append(self, text):
		if text.split(' ')[0] != 'echo':
			self.text += 'echo "Executing: %s"\n' % text.split('\n')[0]
		self.text += text

def append_tee_header(script, log_path):
	script.append("tee='tee -a %s'\n" % log_path)
	
def append_clone_repo(script, repo):
	script.append("git clone %s 2>&1 | $tee\n" % repo)
	
def append_update_mirrorkan(script, mirrorkan_root):
	script.append("cd %s\n" % mirrorkan_root)
	append_clone_repo(script, "https://github.com/KSP-CKAN/MirrorKAN.git")
	script.append("cd MirrorKAN\n")
	script.append("python mirrorkan.py | $tee")

def append_ckan_build(script):
	script.append("rm CKAN -R\n")
	append_clone_repo(script, "https://github.com/KSP-CKAN/CKAN.git")
	script.append("cd CKAN\n")
	script.append("perl bin/build | $tee\n")

def main():
	if len(sys.argv) < 3:
		print 'Usage:'
		print sys.argv[0] + ' <target bash script> <log path> <mirrorkan root>'
		sys.exit(0)
		
	script = Script()
	append_tee_header(script, sys.argv[2])
	
	append_ckan_build(script)
	append_update_mirrorkan(script, sys.argv[3])
		
	with open(sys.argv[1], 'w') as script_file:
		script_file.write(script.text)

if __name__ == "__main__":
	main()
