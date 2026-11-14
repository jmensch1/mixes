"""Read a WAV file (16-bit, 24-bit or 32-bit float, as Logic writes them) into one mono channel of floats."""
import struct, numpy as np


def readwav(p):
    b = open(p, "rb").read(); i = 12; fmt = None
    while i < len(b):
        cid, size = b[i:i+4], struct.unpack("<I", b[i+4:i+8])[0]
        if cid == b"fmt ": fmt = struct.unpack("<HHIIHH", b[i+8:i+24])
        if cid == b"data": data = b[i+8:i+8+size]; break
        i += 8 + size + (size & 1)
    ch, bits = fmt[1], fmt[5]
    if fmt[0] == 3: x = np.frombuffer(data[:len(data)//4*4], "<f4").astype(np.float32)
    elif bits == 16: x = np.frombuffer(data, "<i2").astype(np.float32) / 32768
    else:
        a = np.frombuffer(data[:len(data)//3*3], np.uint8).reshape(-1, 3).astype(np.int32)
        v = a[:, 0] | (a[:, 1] << 8) | (a[:, 2] << 16); v = np.where(v >= 1 << 23, v - (1 << 24), v)
        x = v.astype(np.float32) / (1 << 23)
    return x.reshape(-1, ch).mean(axis=1)   # channels averaged
