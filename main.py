import numpy as np
import os
import cv2

FILE_PATH = "Tibia.spr"
OUTPUT_DIR = "./sprites"

TRANS_COLOR = (255, 105, 180)
SPRITE_WIDTH = 32

def read_u32(data, index):
    value = int.from_bytes(data[index:index+4], byteorder='little', signed=False)
    return value

def read_u16(data, index):
    value = int.from_bytes(data[index:index+2], byteorder='little', signed=False)
    return value

def read_u8(data, index):
    value = int.from_bytes(data[index:index+1], byteorder='little', signed=False)
    return value
    

data = open(FILE_PATH, 'rb').read()

def read_sprite(data, id):
    pixels = []
    sprite_offset = read_u32(data, 6 + (id-1)*4)
    n_bytes_read = 0
    n_bytes_readable = read_u16(data, sprite_offset + 3)
    
    if sprite_offset == 0 or n_bytes_readable == 0:
        return None

    offset = sprite_offset + 5
    while n_bytes_read < n_bytes_readable:
        n_pixels_transparent = read_u16(data, offset)
        n_pixels_colored = read_u16(data, offset + 2)
        offset += 4
        
        pixels.extend([TRANS_COLOR] * n_pixels_transparent)
        for i in range(n_pixels_colored):
            r = read_u8(data, offset)
            g = read_u8(data, offset + 1)
            b = read_u8(data, offset + 2)
            pixels.append((r, g, b))                        
            offset += 3
        n_bytes_read += 4 + 3 * n_pixels_colored

    n_pixels_read = len(pixels)
    n_pixels_missing = SPRITE_WIDTH**2 - n_pixels_read
    pixels.extend([TRANS_COLOR] * n_pixels_missing)
    
    dim = np.sqrt(len(pixels))
    assert dim == int(dim) # must be square
    dim = int(dim)
    pixels = np.array(pixels).reshape(dim, dim, 3)
    return pixels
    
n_sprites = read_u16(data, 4)

for i in range(1,n_sprites+1):
    pixels = read_sprite(data, i)
    if pixels is not None:
        output_path = os.path.join(OUTPUT_DIR, "{}.png".format(i))
        print("Writing image to path: " + output_path)

        pixels_bgr = pixels[:, :, ::-1]
        cv2.imwrite(output_path, pixels_bgr)
        
