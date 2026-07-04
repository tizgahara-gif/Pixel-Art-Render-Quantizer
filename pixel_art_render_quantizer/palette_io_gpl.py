from __future__ import annotations
from .utils import rgba_to_hex, hex_to_rgba

def parse_gpl(text):
    colors=[]
    for line in text.splitlines():
        s=line.strip()
        if not s or s.startswith('#') or s.startswith('GIMP Palette') or s.startswith('Name:') or s.startswith('Columns:'):
            continue
        parts=s.split()
        if len(parts)>=3 and all(p.isdigit() for p in parts[:3]):
            colors.append((int(parts[0])/255, int(parts[1])/255, int(parts[2])/255, 1.0))
    if not colors: raise ValueError('No colors found in GPL file')
    return colors

def write_gpl(name, colors):
    lines=['GIMP Palette', f'Name: {name}', 'Columns: 8', '#']
    for c in colors:
        r,g,b=[round(v*255) for v in c[:3]]; lines.append(f'{r:3d} {g:3d} {b:3d}\t{rgba_to_hex(c)}')
    return '\n'.join(lines)+'\n'
