#!/usr/bin/python3
import md
import shutil
import sys
import sqlite3
import xml.etree.ElementTree as ET
from collections import deque
from pathlib import Path
from pathvalidate import sanitize_filepath, sanitize_filename

from models.node import Node

node_dict = {}
problem_langs = {str: str}
used_paths = [str]
target_dir = Path("c2md_gen")
cursor = None


# cherrytree and obsidian's code formatting methods are slightly different
# so we will change out the important ones in this method
# obsidian uses https://prismjs.com/#supported-languages
def check_lang(lang: str) -> str:
    if lang in problem_langs.keys():
        return problem_langs[lang]
    return lang


def populate_problem_langs() -> None:
    # cherrytree's codebox | obsidian
    # python3              | py or python
    problem_langs["python3"] = "python"
    problem_langs["c-sharp"] = "csharp"


# checks for duplicate path names
def create_path(node: Node) -> Path:
    # TODO: check if path is None and put all of these in a missing_path folder
    base_path = target_dir
    if node.father_id != 0:
        father_node = node_dict[node.father_id]
        base_path = father_node.path
    path = base_path.joinpath(node.name)
    if path in used_paths:
        # generate new name for folder and node with duplicate name
        new_name = f"{node.name}(dup)"
        path = base_path.joinpath(new_name)
        node.name = new_name
    path = sanitize_filepath(path)
    return path


# recursively create subfolders
def generate_subfolders(root: Node):
    if root is None:
        return

    queue = deque([root])
    while queue:
        node = queue.popleft()
        path = create_path(node)
        node.path = path
        used_paths.append(path)

        # enque all direct children of current node
        if node.has_children:
            print(f"creating folder -> {path}")
            path.mkdir()
            children_ids = cursor.execute(
                f"SELECT node_id FROM children WHERE father_id = '{node.id}'"
            ).fetchall()
            for row in children_ids:
                id = row[0]
                child_node = node_dict[id]
                queue.append(child_node)


# creates the proper folders and subfolders based off
# CherryTree's tree structure
# Note: we can't just process the Node.id's sequentially since a user can reparent nodes as they like.
def generate_folders() -> None:
    # select all nodes where father_id == 0, AKA root nodes
    root_nodes = {k: v for k, v in node_dict.items() if v.father_id == 0}
    for n in root_nodes.values():
        generate_subfolders(n)


def get_offset(processed_offsets, id: int) -> str:
    offsets_str = "''"
    length = len(processed_offsets)
    if length == 1:
        offsets_str = processed_offsets[0]
    elif length > 1:
        offsets_str = ",".join(processed_offsets)
    offset = cursor.execute(
        f"""SELECT MIN(offset) FROM
        (
            SELECT node_id, justification, offset
            FROM image
            WHERE node_id = '{id}' AND offset NOT IN({offsets_str})
            UNION ALL
            SELECT node_id, justification, offset
            FROM codebox
            WHERE node_id = '{id}' AND offset NOT IN({offsets_str})
            UNION ALL
            SELECT node_id, justification, offset
            FROM grid
            WHERE node_id = '{id}' AND offset NOT IN({offsets_str})
        )
        """
    ).fetchone()[0]
    return str(offset)


def main() -> None:
    print("starting...")
    populate_problem_langs()
    # check if arg size is correct
    if (args_count := len(sys.argv)) == 2:
        if sys.argv[1] == "help":
            print("convert.py /PATH_TO_CHERRYTREE_DB/")
            raise SystemExit(0)
    elif args_count > 2:
        print("Too many args: type 'help' for usage")
        raise SystemExit(2)
    elif args_count < 2:
        print("Too few args: type 'help' for usage")
        raise SystemExit(2)

    ct_file = Path(sys.argv[1])

    if target_dir.exists():
        print(f"Directory: {target_dir} already exists!")
        ans = input("overwrite? (y/n): \n")
        if ans.lower() == "y" or ans.lower() == "yes":
            shutil.rmtree(target_dir)
        else:
            sys.exit(1)

    connection = sqlite3.connect(ct_file)
    global cursor
    cursor = connection.cursor()
    nodes = cursor.execute(
        "SELECT * FROM node INNER JOIN children ON node.node_id = children.node_id ORDER BY father_id"
    ).fetchall()

    print(f"ct_file:{ct_file} target_dir:{target_dir}")
    target_dir.mkdir()

    for node in nodes:
        # take nodes from db and insert them into the dict
        # replace troublesome chars
        name = node[1].replace("/", "(forward_slash)").replace("\\", "(backslash)")
        name = sanitize_filename(name)
        id = node[0]
        has_children = int(
            cursor.execute(
                f"SELECT EXISTS(SELECT 1 FROM children WHERE father_id='{id}');"
            ).fetchone()[0]
        )
        n = Node(id, name, node[2], node[6], node[7], node[8], node[14], has_children)
        node_dict[n.id] = n

    generate_folders()

    for node in node_dict.values():
        root = ET.fromstring(node.text)
        processed_offsets = []
        print(f"generating md file -> {node}")
        # skip creating file if there is no text in node
        if len(root) < 1:
            continue
        # add .md extension
        path = node.path
        if node.has_children:
            path = path.joinpath(f"{node.name}.md")
        else:
            path = f"{path}.md"
        with open(path, encoding="utf-8", mode="w") as f:
            for child in root:
                # check for injectable tables, codeboxes or images
                # they all use the justification attribute
                if child.attrib.get("justification") is not None:
                    # offsets SHOULD be unique
                    offset = get_offset(processed_offsets=processed_offsets, id=node.id)
                    codebox_rows = cursor.execute(
                        f"SELECT * FROM codebox WHERE node_id='{node.id}' AND offset='{offset}'"
                    ).fetchall()
                    image_rows = cursor.execute(
                        f"SELECT * FROM image WHERE node_id='{node.id}' AND offset='{offset}'"
                    ).fetchall()
                    grid_rows = cursor.execute(
                        f"SELECT * FROM grid WHERE node_id='{node.id}' AND offset='{offset}'"
                    ).fetchall()
                    if len(codebox_rows) > 0:
                        print(f"processing codebox for node:{node.id}")
                        # db format
                        # [(1, 392, 'left', "import sys\n\nprint('hello world!)", 'python3', 500, 100, 1, 1, 0)]
                        codebox = codebox_rows[0]
                        lang = codebox[4]
                        lang = check_lang(lang)
                        text = codebox[3]
                        f.write(
                            f"```{lang}\n{text}\n```"
                        )  # obsidian uses backticks where other markdown is single quotes
                    elif len(image_rows) > 0:
                        print(f"processing image for node:{node.id}")
                        image = image_rows[0]
                        link_row = image[6]
                        blob = image[4]
                        if len(link_row) > 0:  # link to hosted image
                            link = link_row.split(" ")[1]
                            # ![Engelbart|100x145](https://history-computer.com/ModernComputer/Basis/images/Engelbart.jpg) obsidian syntax
                            f.write(f"![{link}]({link})")
                        else:  # link to local image
                            # save blob to _img folder
                            # generate link to this local file using relative path
                            # filename will be node name + offset
                            image_dir = target_dir.joinpath("img")
                            if not image_dir.exists():
                                image_dir.mkdir()
                            image_path = image_dir.joinpath(
                                f"{node.name}{node.id}{offset}.png"
                            )
                            if image_path.exists():
                                print(f"image {image_path} exists already! exiting...")
                                sys.exit(2)
                            with open(image_path, "wb") as file:
                                file.write(blob)
                            # obsidian just uses the file name for the image path and expects it to be in the img folder
                            relative_path = image_path.relative_to(image_dir)
                            # ![[Engelbart.jpg|100x145]] # local embed format for obsidian
                            f.write(f"![[{relative_path}]]")
                    elif len(grid_rows) > 0:
                        print(f"processing table for node:{node.id}")
                        table = grid_rows[0]
                        xml = table[3]
                        f.write(md.translate_table(xml))
                    processed_offsets.append(f"'{str(offset)}'")
                else:  # normal xml to  md conversion
                    f.write(md.translate_xml(child.attrib, child.text, node_dict))
    connection.close()
    print("finished with no errors")


if __name__ == "__main__":
    main()
