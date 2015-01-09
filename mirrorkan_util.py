import os
from os import listdir
from os.path import isfile, isdir, join

def zipdir(path, zip):
    for root, dirs, files in os.walk(path):
        for file in files:
            zip.write(os.path.join(root, file))

def download_file(url, path, filename):
    os.system('wget -O "' + os.path.join(path, filename) + '" "' + url + '"')
    
def find_files_with_extension(directory, extension, recursive = True):
    result_list = []
    
    file_list = [ f for f in listdir(directory) if isfile(join(directory, f)) ]
    file_list.sort()
    
    for f in file_list:
        fileName, fileExtension = os.path.splitext(f)
        if fileExtension == extension:
            result_list += [os.path.join(directory, f)]
    
    if recursive == True:
        directory_list = [ f for f in listdir(directory) if isdir(join(directory, f)) ]
        for d in directory_list:
            result_list += find_files_with_extension(os.path.join(directory, d), extension, True)
    
    return result_list
