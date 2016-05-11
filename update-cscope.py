#!/usr/bin/env python

# Try looking at https://pypi.python.org/pypi/pycscope/ for python files

import os
import sys
import fnmatch
import subprocess
import random, string
import vim

# Global vars
project_root_indicators = ['.svn','.git']
project_root = ''
src_extensions = ('.c', '.h', '.cpp', '.hpp', '.py')
excluded_dirs = []
cscope_dir = '/home/rmatthews/.cscope'

#index info
index_file = os.path.join(cscope_dir, "index")
PROJ_PATH_IDX = 0
DB_NAME_IDX = 1

def find_project_root():
    current_dir = os.getcwd()

    current_root = current_dir
    found_path = None

    while found_path is None and current_root:
        dir_contents = os.listdir(current_root)

        for a_file in dir_contents:
            fullPath = os.path.join(current_root, a_file)
            #print(fullPath)
            if a_file in project_root_indicators:
                found_path = os.path.join(current_root, a_file)
                print("Found {}".format(found_path))
                break

        current_root = os.path.dirname(current_root)

    project_root = os.path.dirname(found_path)
    return project_root

def find_sources():
    sources = []

    print("Searching from project root {}".format(project_root))

    for (root, dirs, files) in os.walk(project_root, topdown=True):
        # prune unwanted directories in place
        dirs[:] = [d for d in dirs if d not in excluded_dirs]

        for filename in files:
            #print("checking file {}".format(filename))
            if filename.endswith(src_extensions):
                print("added file {}".format(filename))
                sources.append(os.path.join(root, filename))

    return sources

def createcscope_db(sources):
    # create cscope dir to hold databases
    if not os.path.isdir(cscope_dir):
        os.mkdir(cscope_dir)

    # create a dir to store database for this project
    database = randomword(10)+".db"
    database_path = os.path.join(cscope_dir, database)
    if not os.path.isdir(database_path):
        os.mkdir(database_path)

    addToIndex(database, project_root)

    # create sources list
    sources_file = os.path.join(database_path, 'cscope.files')
    f = open(sources_file, 'w+')

    for source in sources:
        f.write(source+"\n")

    f.close()

    # generate cscope database
    cd_command = "cd "+database_path
    cscope_command = "/usr/bin/cscope -b -q -k"
    command = cd_command + " && " + cscope_command

    print("Running {}".format(command))
    rc = subprocess.call(command, shell=True)

    if (rc != 0):
        print('cscope error')
        sys.exit()

def get_db():
    db_path = ''

    with open(index_file, "r") as f:
        for line in f:
            db = line.split('|')
            if db[PROJ_PATH_IDX] == project_root:
                db_dir = os.path.join(cscope_dir, db[DB_NAME_IDX])
                db_path = os.path.join(db_dir, 'cscope.out')
                break

    return db_path

def addToIndex(db, project):
    f = open(index_file, "a")

    f.write(project+"|"+db+"\n")

    f.close()


def randomword(length):
       return ''.join(random.choice(string.lowercase) for i in range(length))

def connect_db():
    global project_root

    project_root = find_project_root()

    if (project_root == ''):
        print("No project root found, exiting")
        sys.exit()

    db = get_db():

    if db == '':
        response = raw_input( 'No db found for current file, would you like to create one [y/n]? ')
        while response not in ['y', 'n', 'Y', 'N']:
            response = raw_input('y/n: ')

        if response in ['n', 'N']:
            sys.exit()

        sources = find_sources()
        createscsope_db(sources)

    # only add a db if not already added
    if vim.eval("cscope_connection(2, {})".format(db)) == 0:
        add_command = 'cs add ' + db
        vim.command(add_command)

    return db
    

def main():
    global project_root

    project_root = find_project_root()

    if (project_root == ''):
        print("No project root found, exiting")
        sys.exit()

    sources = find_sources()

    createcscope_db(sources)

if __name__ == "__main__":
    main()
