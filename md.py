def translate_xml(attr: dict, text: str, node_dict) -> str:
    if text is None:
        return ''
    replaced = text.replace('☐','- [ ]').replace('☑','- [x]')
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
                print(f'l {l} r {r} replaced {replaced}') 
                if l == 'webs':
                   return f'[{replaced}]({r})'
                elif l == 'node':
                    return f'[[{node_dict[int(r)].name}]]'
            case _:
                return replaced or ''
    return replaced or ''