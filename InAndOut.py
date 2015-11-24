import os
from sys import exit
import hashlib          #We use it to check different configurations
import shutil           #Backup every config used

def startup_check(output_dir = ".store"):
    if not os.path.isdir(output_dir):
        if not os.path.exists(output_dir):
            try:
                os.mkdir(output_dir)
            except:
                exit("Unknown error creating folder")
            return True
        else:
            exit("Destination must be a folder! Check your config")
    else:
        return True

def hashIt(module): #We use this to check if configuration changed
    key_string = str({key: value for key, value in module.__dict__.iteritems()
        if not (key.startswith('__') or key.startswith('_'))})

    return key_string, hashlib.sha1(key_string).hexdigest()

def saveKey(file_hash, values):
    output_name = '.' + file_hash
    if not os.path.isfile(output_name):
        try:
            output = open(output_name, 'w')
            output.write("%s" % values)
            output.close()
        except:
            raise
            exit("Probem writing file?! DEBUG me")
        return True
    else:
        return False

def saveFile(file_name, file_hash):
    output_name = '.' + file_hash + '.py'
    if not os.path.isfile(output_name):
        try:
            shutil.copy2(file_name, '.' + file_hash + '.py')
        except:
            raise
            exit("Probem copying file?! DEBUG me")
        return True
    else:
        return False
