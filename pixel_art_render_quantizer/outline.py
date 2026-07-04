"""Strict one-pixel outline with topology cleanup."""
from __future__ import annotations

def _idx(x,y,w): return y*w+x

def _neighbors8(x,y,w,h):
    for dy in (-1,0,1):
        for dx in (-1,0,1):
            if dx or dy:
                nx,ny=x+dx,y+dy
                if 0 <= nx < w and 0 <= ny < h: yield nx,ny

def outline_mask_from_alpha(pixels, width, height):
    mask=[False]*(width*height)
    for y in range(height):
        for x in range(width):
            if pixels[_idx(x,y,width)][3] > 0: continue
            if any(pixels[_idx(nx,ny,width)][3] > 0 for nx,ny in _neighbors8(x,y,width,height)):
                mask[_idx(x,y,width)] = True
    return cleanup_strict_mask(mask,width,height)

def cleanup_strict_mask(mask,w,h):
    mask=list(mask); changed=True
    while changed:
        changed=False
        # remove 2x2 blocks
        for y in range(h-1):
            for x in range(w-1):
                block=[_idx(x,y,w),_idx(x+1,y,w),_idx(x,y+1,w),_idx(x+1,y+1,w)]
                if all(mask[i] for i in block):
                    mask[block[-1]]=False; changed=True
        # remove branches (8-neighbor degree >=3), preserving earliest pixels
        for y in range(h):
            for x in range(w):
                i=_idx(x,y,w)
                if not mask[i]: continue
                deg=sum(1 for nx,ny in _neighbors8(x,y,w,h) if mask[_idx(nx,ny,w)])
                if deg >= 3:
                    mask[i]=False; changed=True
    return mask

def apply_outline(pixels,w,h,outline_color):
    mask=outline_mask_from_alpha(pixels,w,h)
    out=list(pixels)
    for i,m in enumerate(mask):
        if m: out[i]=(*outline_color[:3],1.0)
    return out
