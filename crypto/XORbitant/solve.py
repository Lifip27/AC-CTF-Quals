from collections import Counter
import sys

ALLOWED = b"CTF{}0123456789abcdef"
KEY_LEN = 69  # 4 + 64 + 1

def is_printable(b: int) -> bool:
    return b in (9, 10, 13) or 32 <= b <= 126

def score_chunk(bs: bytes) -> int:
    printable = sum(1 for x in bs if is_printable(x))
    spaces = bs.count(0x20)
    letters = sum(1 for x in bs if (65 <= x <= 90) or (97 <= x <= 122))
    return printable * 3 + spaces * 2 + letters

def recover_flag(cipher: bytes) -> bytes:
    key = [None] * KEY_LEN

    known = {0: ord('C'), 1: ord('T'), 2: ord('F'), 3: ord('{'), KEY_LEN - 1: ord('}')}
    for i, v in known.items():
        key[i] = v

    for pos in range(KEY_LEN):
        if key[pos] is not None:
            continue
        col = cipher[pos::KEY_LEN] 
        best = None 
        for k in ALLOWED:
            dec = bytes(b ^ k for b in col)
            s = score_chunk(dec)
            if best is None or s > best[0]:
                best = (s, k)
        key[pos] = best[1]

    return bytes(key)

def decrypt(cipher: bytes, key: bytes) -> bytes:
    kl = len(key)
    return bytes(cipher[i] ^ key[i % kl] for i in range(len(cipher)))

def main():
    with open(sys.argv[1], "rb") as f:
        ct = f.read()
    flag = recover_flag(ct)
    pt = decrypt(ct, flag)
    printable_ratio = sum(1 for b in pt if is_printable(b)) / max(1, len(pt))
    print("flag:", flag.decode())
    print(f"ratio: {printable_ratio:.3f}")

if __name__ == "__main__":
    main()
