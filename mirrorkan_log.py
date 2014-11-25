#!/usr/bin/env python

import os, sys
import json

class Log:
    def __init__(self, path):
        self.path = path
        
        if os.path.exists(path):
            return
        
        clear()
        
    def clear(self):
        with open(self.path, 'w') as db_file:
            db_file.write('{ "warnings": [], "errors": [], "info": [], "events": [] }')
            
    def logInfo(self, message):
        db = None
    
        with open(self.path, 'r') as db_file:
            db = json.load(db_file)
            db['info'] += [message]
        
        if db is not None:
            with open(self.path, 'w') as db_file:
                json.dump(db, db_file)
            
    def logWarning(self, message):
        db = None
    
        with open(self.path, 'r') as db_file:
            db = json.load(db_file)
            db['warnings'] += [message]
        
        if db is not None:
            with open(self.path, 'w') as db_file:
                json.dump(db, db_file)
        
    def logError(self, message):
        db = None
    
        with open(self.path, 'r') as db_file:
            db = json.load(db_file)
            db['errors'] += [message]
        
        if db is not None:
            with open(self.path, 'w') as db_file:
                json.dump(db, db_file)

    def logEvent(self, event, message):
        db = None
    
        with open(self.path, 'r') as db_file:
            db = json.load(db_file)
            db['events'] += [{'event': event, 'message': message}]
        
        if db is not None:
            with open(self.path, 'w') as db_file:
                json.dump(db, db_file)

    def getWarnings(self):
        with open(self.path, 'r') as db_file:
            db = json.load(db_file)
            return db['warnings']
            
        return None
        
    def getErrors(self):
        with open(self.path, 'r') as db_file:
            db = json.load(db_file)
            return db['errors']
            
        return None

    def getInfo(self):
        with open(self.path, 'r') as db_file:
            db = json.load(db_file)
            return db['info']

        return None
        
    def getEvents(self):
        with open(self.path, 'r') as db_file:
            db = json.load(db_file)
            return db['events']

        return None
        
def main():
    if len(sys.argv) < 4:
        print 'Usage:'
        print sys.argv[0] + ' <log_db> <warning/error/info> <message>'
        sys.exit(0)
    
    log = Log(sys.argv[1])
    
    if sys.argv[2] == 'warning':
        log.logWarning(sys.argv[3])
    elif sys.argv[2] == 'error':
        log.logError(sys.argv[3])
    elif sys.argv[2] == 'info':
        log.logInfo(sys.argv[3])
    else:
        print 'Invalid argument "%s", expected "warning", "error" or "info"' % sys.argv[2]
        sys.exit(1)
    
    sys.exit(0)

if __name__ == "__main__":
    main()
