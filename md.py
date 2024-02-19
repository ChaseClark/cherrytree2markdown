import re
import xml.etree.ElementTree as ET

# this may be better done with regex but i cba
def fix_nested_num_lists(text: str) -> str:
    num_symbols = (')','-','>')
    lines = text.split('\n')
    for i in range(len(lines)):
        if ' ' in lines[i]: 
            for j in range(len(lines[i])):
                char = lines[i][j]
                if char in num_symbols:
                    # check if first char in line is a space
                    # and if prev char is a number
                    if lines[i][0].isspace() and lines[i][j-1].isdigit():
                        # replace symbol with dot
                        lines[i] = lines[i][:j] + '.' +  lines[i][j + 1:]

    return '\n'.join(lines)

def fix_nested_bullet_lists(text: str) -> str:
    bullet_symbols = ('◇','▪','→','⇒')
    replaced = text.replace('•','-')
    lines = replaced.split('\n')
    for i in range(len(lines)):
        if ' ' in lines[i]: 
            for j in range(len(lines[i])):
                char = lines[i][j]
                if char in bullet_symbols:
                    # check if first char in line is a space
                    # and if prev char is a number
                    if lines[i][0].isspace():
                        # replace symbol with dot
                        lines[i] = lines[i][:j] + '-' +  lines[i][j + 1:]

    return '\n'.join(lines)

def escape_md_symbols(text: str) -> str:
    replaced = text
    symbols = ('*','=','#','~','`','_')
    for s in symbols:
        replaced = replaced.replace(s,fr'\{s}')
    return replaced

def transform_plaintext(original: str) -> str:
    # replace unchecked box symbol for todo items
    replaced = original.replace('☐','- [ ]')
    # replace check box symbol for todo items
    replaced = replaced.replace('☑','- [x]')
    # horizontal rule
    replaced = replaced.replace('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~','---')
    # All nested numbered lists symbols, 
    replaced = fix_nested_num_lists(replaced)
    # fix nested bulleted lists with cherrytree symbols
    replaced = fix_nested_bullet_lists(replaced)
    # escape md symbols with '\' so they do get rendered by obsidian
    replaced = escape_md_symbols(replaced) 
    return replaced

# process input depending on what xml attribute is detected
def translate_xml(attr: dict, text: str, node_dict) -> str:
    if text is not None:
        replaced = transform_plaintext(text)
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
    # obsidian table format # 2nd line is to distinguish header row
    # First name | Last name
    # | -- | -- | # this row has bars on outside in case the header is blank for some reason
    # Max | Planck
    # Marie | Curie    
     ###
    col_len = len(array[0])
    row_len = len(array)
    # tables in obsidian need extra newline before or else it will not render
    output = f'\n| {(' | ').join(array[row_len-1])}\n'
    output = output + '--' + ' | --' * (col_len - 1) + '\n'
    for x in range(row_len-1):
        output = output + (' | ').join(array[x]) + '\n'
    return output