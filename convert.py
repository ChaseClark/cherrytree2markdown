#!/usr/bin/python3
import shutil
import sys
import sqlite3
import xml.etree.ElementTree as ET
import md
from pathlib import Path

from models.node import Node



node_dict = {}

def create_dir(n: Node, fid: int):
    pass

def main():
    connection = sqlite3.connect("ct_db.ctb")

    print("starting...")
    # if (args_count := len(sys.argv)) == 2:
    #     if sys.argv[1] == "help":
    #         print("convert.py /PATH_TO_CHERRYTREE_DB/ /PATH_TO_NEW_DIR/")
    #         raise SystemExit(0)
    # elif args_count > 3:
    #     print("Too many args: type 'help' for usage")
    #     raise SystemExit(2)
    # elif args_count < 3:
    #     print("Too few args: type 'help' for usage")
    #     raise SystemExit(2)

    # ct_file = Path(sys.argv[1])
    # target_dir = Path(sys.argv[2])
    
    # print(f'ct_file:{ct_file} target_dir:{target_dir}')

    # if target_dir.is_dir():
    #     print("The target directory exists already! this program will not overwrite! exiting...")
    #     raise SystemExit(1)

    # temp hardcoding of inputs
    ct_file = Path('ct_db.ctb')
    target_dir = Path('temp')
    if target_dir.exists():
        shutil.rmtree(target_dir)

    target_dir.mkdir() # create temp dir

    cursor = connection.cursor()
    # nodes = cursor.execute("SELECT * FROM node").fetchall()
    nodes = cursor.execute("SELECT * FROM node INNER JOIN children ON node.node_id = children.node_id ORDER BY father_id").fetchall()


    for node in nodes:
        # take nodes from db and insert them into the dict
        n = Node(node[0],node[1],node[2],node[6],node[7],node[8],node[14])
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
            path = fn.path.joinpath(n.name)
            if path.exists():
                # generate new name for folder and node with duplicate name
                new_name = f'{n.name}(dup)'
                path = fn.path.joinpath(new_name)
                n.name = new_name
            path.mkdir()
            n.path = path
            



    test_node = node_dict[1]
    # print(node1)
    # print(f'node1[1]: {node1[1]}')
    root = ET.fromstring(test_node.text)
    with open(test_node.path.joinpath(f'{test_node.name}.md'), encoding="utf-8", mode='w') as f:
        if f.writable():
            for child in root:
                f.write(md.translate_xml(child.attrib,child.text,node_dict))
    print('finished')

if __name__ == "__main__":
    main()
