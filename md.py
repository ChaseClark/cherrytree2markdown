import xml.etree.ElementTree as ET

def translate_xml(attr: dict, text: str, node_dict) -> str:
    replaced = text
    if text is not None:
        replaced = replaced.replace('☐','- [ ]').replace('☑','- [x]').replace('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~','---')
    for k in attr.keys():
        match k:
            case 'scale':
                if attr[k][0].lower() == 'h':
                    return f'{'#' * int(attr[k][1])} {replaced}'
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
            case 'link':
                l,r = attr[k].lower().split(' ')
                # print(f'l {l} r {r} replaced {replaced}') 
                if l == 'webs':
                   return f'[{replaced}]({r})'
                elif l == 'node':
                    return f'[[{node_dict[int(r)].name}]]'
            case _:
                return replaced or ''
    return replaced or ''

def translate_table(xml: str) -> str:
    root = ET.fromstring(xml)
    output = ''
    count = 0
    array = []
    for row in root:
        array.append([])
        for cell in row:
            array[count].append(cell.text or '') # append blank string if no text in cell
        count = count + 1
    # header row
    ###
    # obsidian table format # 2nd line is to distinguish header row
    # First name | Last name
    # -- | --
    # Max | Planck
    # Marie | Curie    
     ###
    col_len = len(array[0])
    row_len = len(array)
    # tables in obsidian need extra newline before or else it will not render
    output = '\n' + (' | ').join(array[row_len-1]) + '\n'
    output = output + '--' + ' | --' * (col_len - 1) + '\n'
    for x in range(row_len-1):
        output = output + (' | ').join(array[x]) + '\n'
    return output