import sys
with open(sys.argv[1]) as f:
    tokens = []
    for line in f:
        for part in line.strip().split('$$$'):
            if part:
                tokens.append(part)

hex_str = ''.join(tokens)
flag = bytes.fromhex(hex_str).decode()

print("hex", hex_str)
print("flag", flag)
