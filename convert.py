#!/usr/bin/python3
import shutil
import sys
import sqlite3
import xml.etree.ElementTree as ET
from pathlib import Path

def to_md(attr: dict, text: str) -> str:
    if text is None:
        return ''
    replaced = text.replace('☐','- [ ]').replace('☑','- [x]')
    for k in attr.keys():
        match k:
            case 'scale':
                if attr[k][0].lower() == 'h':
                    return f'{'#'*int(attr[k][1])} {replaced}'
                elif attr[k].lower() == 'sub':
                    return f'<sub>{replaced}</sub>'
                elif attr[k].lower() == 'sup':
                    return f'<sup>{replaced}</sup>'
            case 'weight':
                return f'**{replaced}**'
            case 'style':
                return f'*{replaced}*'
            case 'strikethrough':
                return f'~~{replaced}~~'
            case 'underline':
                return f'=={replaced}=='
            case 'family':
                if attr[k].lower() == 'monospace':
                    return f'`{replaced.split('\n')[0]}`\n\n'
            case _:
                return replaced or ''
    return replaced or ''
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

    cursor = connection.cursor()
    nodes = cursor.execute("SELECT * FROM node").fetchall()
    # print(rows)

    for node in nodes:
        # 1 = node name
        # 2 = txt
        # print(node[1])
        pass


    node1 = nodes[0]
    # print(node1)
    # print(f'node1[1]: {node1[1]}')
    root = ET.fromstring(node1[2])
    count = 0
    for child in root:
        # print(count,child.tag, child.attrib, child.text)
        # print(type(child.attrib))
        count += 1

    target_dir.mkdir()

    with open(target_dir.joinpath('new.md'), encoding="utf-8", mode='w') as f:
        if f.writable():
            for child in root:
                f.write(to_md(child.attrib,child.text))
    print('finished')

if __name__ == "__main__":
    main()
