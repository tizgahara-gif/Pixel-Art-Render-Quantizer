from .dither import BAYER4

def apply_alpha(pixels, width, height, mode="PRESERVE", threshold=0.5):
    if mode == "PRESERVE":
        return list(pixels)
    out=[]
    for y in range(height):
        for x in range(width):
            r,g,b,a = pixels[y*width+x]
            if mode == "DITHERED":
                keep = a >= (BAYER4[y%4][x%4] + 0.5) / 16.0
            else:
                keep = a >= threshold
            out.append((r,g,b,1.0 if keep else 0.0))
    return out
