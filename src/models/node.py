from pathlib import Path


class Node:
    def __init__(
        self,
        id: int,
        name: str,
        text: str,
        has_codebox: bool,
        has_table: bool,
        has_image: bool,
        father_id: int,
        has_children: bool,
    ):
        self.id = id
        self.name = name
        self.text = text
        self.has_codebox = has_codebox
        self.has_table = has_table
        self.has_image = has_image
        self.father_id = father_id
        self.has_children = has_children
        self.path: Path = None

    def __str__(self):
        return f"Node<{self.id}> \tname:{self.name}\t father_id:{self.father_id}"
