#!/usr/bin/env python3
import struct
import sys

def rc4(data: bytes, key: list[int]) -> bytes:
    S = list(range(256))
    j = 0
    out = bytearray()
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) % 256
        S[i], S[j] = S[j], S[i]
    i = j = 0
    for char in data:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        out.append(char ^ S[(S[i] + S[j]) % 256])
    return out

KEYMASK = [
    0xB1, 0x54, 0x45, 0x57, 0xA7, 0xC4, 0x64, 0x2E,
    0x98, 0xD8, 0xB1, 0x1A, 0x0B, 0xAA, 0xD8, 0x8E,
    0x7F, 0x1E, 0x5B, 0x8D, 0x08, 0x67, 0x96, 0xCB,
    0xAA, 0x11, 0x50, 0x84, 0x17, 0x46, 0xA3, 0x30,
]

if len(sys.argv) <= 1:
    print(f"Usage: {sys.argv[0]} vgs_X_Y_Z.log")
    sys.exit(1)

with open(sys.argv[1], "rb") as f:
    data = f.read()

data = data[4:]  # skip header
real_key = [data[i] ^ KEYMASK[i] for i in range(32)]
data = data[32:]

block_idx = 0
while len(data) > 0:
    if len(data) < 4:
        break
    block_len = struct.unpack("<L", data[:4])[0]
    data = data[4:]
    block = data[:block_len]
    data = data[block_len:]
    dec = rc4(block, real_key)
    try:
        text = dec.decode("utf-16")
    except UnicodeDecodeError:
        text = dec.decode("utf-8", errors="replace")
    print(f"[block {block_idx}]\n{text}\n")
    block_idx += 1
