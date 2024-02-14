#!/usr/bin/python3
import md
import shutil
import sys
import sqlite3
import xml.etree.ElementTree as ET
from pathlib import Path
from pathvalidate import sanitize_filepath, sanitize_filename

from models.node import Node

node_dict = {}

def create_dir(n: Node, fid: int):
    pass

def main():

    print("starting...")
    # check if arg size is correct
    if (args_count := len(sys.argv)) == 2:
        if sys.argv[1] == "help":
            print("convert.py /PATH_TO_CHERRYTREE_DB/ /PATH_TO_NEW_DIR/")
            raise SystemExit(0)
    elif args_count > 3:
        print("Too many args: type 'help' for usage")
        raise SystemExit(2)
    elif args_count < 3:
        print("Too few args: type 'help' for usage")
        raise SystemExit(2)


    ct_file = Path(sys.argv[1])
    target_dir = Path(sys.argv[2])

    if target_dir.exists():
        print(f'Directory: {target_dir} already exists!')
        ans = input('overwrite? (y/n): \n')
        if ans == 'y' or ans == 'yes':
            shutil.rmtree(target_dir)
        else:
            sys.exit(1)

    #troubleshooting path name
    # p = Path('C:\\Users\\chase.clark\\vault\\cherrytree2markdown\\temp\\notes\\prn')
    # print(len(p.as_posix()))
    # p.mkdir(parents=True)

    # ct_file = Path('testing').joinpath('ct_db.ctb')
    connection = sqlite3.connect(ct_file)
    cursor = connection.cursor()
    nodes = cursor.execute("SELECT * FROM node INNER JOIN children ON node.node_id = children.node_id ORDER BY father_id").fetchall()
    
    print(f'ct_file:{ct_file} target_dir:{target_dir}')

    # if target_dir.is_dir():
    #     print("The target directory exists already! this program will not overwrite! exiting...")
    #     raise SystemExit(1)

    # # temp hardcoding of inputs
    # target_dir = Path('temp')
    # if target_dir.exists():
        
    target_dir.mkdir() 

    for node in nodes:
        # take nodes from db and insert them into the dict
        # replace troublesome chars
        name = node[1].replace('/','(forward_slash)').replace('\\','(backslash)')
        name = sanitize_filename(name)
        n = Node(node[0],name,node[2],node[6],node[7],node[8],node[14])
        node_dict[n.id] = n

    # second pass through the nodes to make correct folder structure
    for k in node_dict.keys():
        n = node_dict[k]
        f = n.father_id
        print(f'processing -> {n}')
        if f == 0:
            path = target_dir.joinpath(n.name)            
            if path.exists():
                print('The target directory exists already! this program will not overwrite! exiting...')
                sys.exit(1)
            path.mkdir()
            n.path = path
        else:
            # get father node
            fn = node_dict[f]
            name = n.name
            name = sanitize_filepath(name)
            # print(sanitize_filepath(name,replacement_text=''))

            path = fn.path.joinpath(name)
            if path.exists():
                # generate new name for folder and node with duplicate name
                new_name = f'{name}(dup)'
                path = fn.path.joinpath(new_name)
                n.name = new_name
            # print(f'path {path} node: {n}')
            path.mkdir()
            n.path = path
            

    for node in node_dict.values():
        root = ET.fromstring(node.text)
        with open(node.path.joinpath(f'{node.name}.md'), encoding="utf-8", mode='w') as f:
            if f.writable():
                # convert xml to md
                for child in root:
                    f.write(md.translate_xml(child.attrib,child.text,node_dict))
                # check for tables to inject
                # tables = cursor.execute(f'SELECT * FROM grid WHERE node_id = {node.id}').fetchall()
                # if len(tables) > 0:
                #     print(f'{len(tables)} table(s) found in DB!')
                #     for t in tables:
                #         offset = int(t[1])
                #         txt = t[3]
                        
                        # f.write(md.translate_xml(child.attrib,child.text,node_dict))
    connection.close()
    print('finished with no errors')

if __name__ == "__main__":
    main()
