"""Strict one-pixel outline with topology cleanup."""
from __future__ import annotations
import importlib.util

_HAS_NUMPY = importlib.util.find_spec("numpy") is not None


def _idx(x,y,w): return y*w+x

def _neighbors8(x,y,w,h):
    for dy in (-1,0,1):
        for dx in (-1,0,1):
            if dx or dy:
                nx,ny=x+dx,y+dy
                if 0 <= nx < w and 0 <= ny < h: yield nx,ny

def outline_mask_from_alpha(pixels, width, height):
    if _HAS_NUMPY:
        import numpy as np
        alpha = np.asarray([p[3] for p in pixels], dtype=np.float64).reshape((int(height), int(width))) > 0
        neighbor = np.zeros_like(alpha, dtype=bool)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                src_y0=max(0,-dy); src_y1=int(height)-max(0,dy)
                src_x0=max(0,-dx); src_x1=int(width)-max(0,dx)
                dst_y0=max(0,dy); dst_y1=int(height)-max(0,-dy)
                dst_x0=max(0,dx); dst_x1=int(width)-max(0,-dx)
                neighbor[dst_y0:dst_y1, dst_x0:dst_x1] |= alpha[src_y0:src_y1, src_x0:src_x1]
        return cleanup_strict_mask((~alpha & neighbor).reshape(-1).tolist(), width, height)
    mask=[False]*(width*height)
    for y in range(height):
        for x in range(width):
            if pixels[_idx(x,y,width)][3] > 0: continue
            if any(pixels[_idx(nx,ny,width)][3] > 0 for nx,ny in _neighbors8(x,y,width,height)):
                mask[_idx(x,y,width)] = True
    return cleanup_strict_mask(mask,width,height)


def _cleanup_strict_mask_python(mask,w,h,max_passes=32):
    mask=list(mask)
    for _ in range(max_passes):
        changed=False
        for y in range(h-1):
            for x in range(w-1):
                block=[_idx(x,y,w),_idx(x+1,y,w),_idx(x,y+1,w),_idx(x+1,y+1,w)]
                if all(mask[i] for i in block):
                    mask[block[-1]]=False; changed=True
        for y in range(h):
            for x in range(w):
                i=_idx(x,y,w)
                if not mask[i]: continue
                deg=sum(1 for nx,ny in _neighbors8(x,y,w,h) if mask[_idx(nx,ny,w)])
                if deg >= 3:
                    mask[i]=False; changed=True
        if not changed:
            break
    else:
        print(f"PAQ outline cleanup stopped after {max_passes} passes without convergence")
    return mask


def cleanup_strict_mask(mask,w,h,max_passes=32):
    if not _HAS_NUMPY:
        return _cleanup_strict_mask_python(mask,w,h,max_passes)
    import numpy as np
    arr=np.asarray(mask, dtype=bool).reshape((int(h), int(w))).copy()
    for _ in range(max_passes):
        old=arr.copy()
        if int(h) > 1 and int(w) > 1:
            blocks=arr[:-1,:-1] & arr[:-1,1:] & arr[1:,:-1] & arr[1:,1:]
            arr[1:,1:] &= ~blocks
        deg=np.zeros_like(arr, dtype=np.uint8)
        for dy in (-1,0,1):
            for dx in (-1,0,1):
                if dx == 0 and dy == 0:
                    continue
                src_y0=max(0,-dy); src_y1=int(h)-max(0,dy)
                src_x0=max(0,-dx); src_x1=int(w)-max(0,dx)
                dst_y0=max(0,dy); dst_y1=int(h)-max(0,-dy)
                dst_x0=max(0,dx); dst_x1=int(w)-max(0,-dx)
                deg[dst_y0:dst_y1, dst_x0:dst_x1] += arr[src_y0:src_y1, src_x0:src_x1]
        arr &= ~(arr & (deg >= 3))
        if np.array_equal(arr, old):
            break
    else:
        print(f"PAQ outline cleanup stopped after {max_passes} passes without convergence")
    return arr.reshape(-1).astype(bool).tolist()

def apply_outline(pixels,w,h,outline_color):
    mask=outline_mask_from_alpha(pixels,w,h)
    out=list(pixels)
    for i,m in enumerate(mask):
        if m: out[i]=(*outline_color[:3],1.0)
    return out
