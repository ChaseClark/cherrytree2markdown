#!/usr/bin/python3
import shutil
import sys
import sqlite3
import xml.etree.ElementTree as ET
from pathlib import Path

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


    #TODO open connection to the cherrytree file and attempt to read nodes

    cursor = connection.cursor()
    nodes = cursor.execute("SELECT * FROM node").fetchall()
    # print(rows)

    for node in nodes:
        # 1 = node name
        # 2 = txt
        # print(node[1])
        pass


    node1 = nodes[0]
    print(node1[1])
    root = ET.fromstring(node1[2])
    for child in root:
        if len(child.attrib) > 0:
            print(child.tag, child.attrib, child.text)

    target_dir.mkdir()
    print('finished')

if __name__ == "__main__":
    main()
