# cherrytree2markdown

TODO

- [x] if a node has no text, skip generation of md file
- [x] if a node has no children, skip generation of folder
- [ ] add support for cherrytree tables
      maybe we can find correct location to insert by finding(</rich_text><rich_text justification="left"></rich_text><rich_text>) in xml
- [ ] add support for cherrytree images
- [ ] add support for cherrytree codeboxes

## query snippit

```
SELECT * FROM
(
SELECT node_id, justification, offset
FROM image
WHERE node_id = '1'
UNION ALL
SELECT node_id, justification, offset
FROM codebox
WHERE node_id = '1'
UNION ALL
SELECT node_id, justification, offset
FROM grid
WHERE node_id = '1'
)
ORDER BY offset
```
