# make_png.py
import struct, zlib, binascii

def chunk(t,d):
    return len(d).to_bytes(4,'big') + t + d + binascii.crc32(t+d).to_bytes(4,'big')

sig  = b"\x89PNG\r\n\x1a\n"
ihdr = chunk(b'IHDR', struct.pack(">IIBBBBB", 1337, 1, 8, 2, 0, 0, 0))               # RGB, 8-bit
text = chunk(b'tEXt', b"6ee494848e978ea" + b"\x00" + b"d50bc687e6e14f8f8")           # 15 + NUL + 17
rare = chunk(b'raRE', b"2b6b2c6ba2912d219d")                                          # 18 bytes
scan = b"\x00" + bytes([255,255,255]) * 1337                                          # one white row
idat = chunk(b'IDAT', zlib.compress(scan, 9))
png  = sig + ihdr + text + rare + idat + chunk(b'IEND', b"")

open("pass.png","wb").write(png)
print("built pass.png")
