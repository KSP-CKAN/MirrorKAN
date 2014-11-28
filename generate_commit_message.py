#!/usr/bin/env python

import os, sys

def main(): 
    os.system('git status --porcelain > git.status')
    
    mods = []
        
    with open('git.status', 'r') as status_file:
        for line in status_file.readlines():
            while '  ' in line:
                line = line.replace('  ', ' ')
            mod_name = os.path.splitext(line.strip().split(' ')[1])[0]
            if mod_name == 'git':
                continue
            mods += [mod_name]      
        status_file.close()
    os.system('rm git.status')
    
    print ', '.join(mods)

if __name__ == "__main__":
    main()
