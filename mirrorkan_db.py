import json
import os
from dateutil.parser import parse

class Database:
    def __init__(self, path):
        self.path = path
        
        if os.path.exists(path):
            return
        
        with open(path, 'w') as db_file:
            db_file.write('{}')

    def add_mod(self, url, filename, lastModified):
        db = None
    
        with open(self.path, 'r') as db_file:
            db = json.load(db_file)
            db[url] = (lastModified, filename)
        
        if db is not None:
            with open(self.path, 'w') as db_file:
                json.dump(db, db_file)
    
    def is_newer(self, url, lastModified):
        with open(self.path, 'r') as db_file:
            db = json.load(db_file)
            if url not in db:
                return True
                
            lastModifiedCached = db[url][0]
            dateCached = parse(lastModifiedCached)
            dateIncoming = parse(lastModified)
            
            if dateIncoming > dateCached:
                return True
            return False
        
        return True

    def get_lastmodified(self, url):
        with open(self.path, 'r') as db_file:
            db = json.load(db_file)
            if url not in db:
                return None
                
            return db[url][0]
        return None
        
    def get_filename(self, url):
        with open(self.path, 'r') as db_file:
            db = json.load(db_file)
            if url not in db:
                return None
                
            return db[url][1]
        return None
        
    def is_cached(self, url):
        with open(self.path, 'r') as db_file:
            db = json.load(db_file)
            if url not in db:
                return False
                
            return True
        return False
