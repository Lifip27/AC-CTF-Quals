import sys, struct, base64, string
from collections import defaultdict, OrderedDict

PRINTSET = set(string.ascii_letters + string.digits + '+/=')

def printable_chunks(b, min_len=4):
    cur = []
    for x in b:
        if 32 <= x < 127:
            cur.append(chr(x))
        else:
            if len(cur) >= min_len:
                yield ''.join(cur)
            cur.clear()
    if len(cur) >= min_len:
        yield ''.join(cur)

def try_b64(s: str):
    if (len(s) % 4) != 0: 
        return None
    if any(c not in PRINTSET for c in s):
        return None
    try:
        return base64.b64decode(s, validate=True).decode('ascii')
    except Exception:
        return None

def parse_pcap_ipv4_icmp(path):
    with open(path, 'rb') as f:
        data = f.read()
    if len(data) < 24:
        raise ValueError("File too small for PCAP")
    # Endianness of pcap header
    magic_le = struct.unpack('<I', data[:4])[0]
    magic_be = struct.unpack('>I', data[:4])[0]
    endian = '<' if magic_le == 0xA1B2C3D4 else ('>' if magic_be == 0xA1B2C3D4 else '<')

    off = 24
    out = []

    while off + 16 <= len(data):
        ts_sec, ts_usec, incl_len, _ = struct.unpack(endian + 'IIII', data[off:off+16])
        off += 16
        pkt = data[off:off+incl_len]
        off += incl_len
        if len(pkt) < 20: 
            continue
        # IPv4 only (DLT_RAW)
        if (pkt[0] >> 4) != 4:
            continue
        ihl = (pkt[0] & 0x0F) * 4
        if len(pkt) < ihl + 8:
            continue
        total_len = struct.unpack('!H', pkt[2:4])[0]
        proto = pkt[9]
        if proto != 1:  # ICMP
            continue
        icmp = pkt[ihl:total_len]
        if len(icmp) < 8:
            continue
        icmp_type = icmp[0]
        if icmp_type not in (0, 8):
            continue
        ident = struct.unpack('!H', icmp[4:6])[0]
        seq   = struct.unpack('!H', icmp[6:8])[0]
        data_bytes = icmp[8:]
        out.append({'t': ts_sec + ts_usec/1e6, 'id': ident, 'seq': seq, 'data': data_bytes})
    return out

def assemble_flag(records):
    by_id = defaultdict(dict)  # id -> { seq: token }
    for r in sorted(records, key=lambda x: x['t']):
        token = None
        for chunk in printable_chunks(r['data'], 4):
            tok = try_b64(chunk)
            if tok is not None:
                token = tok
                break
        if token is None:
            continue
        by_id[r['id']].setdefault(r['seq'], token)

    if not by_id:
        return None, {}

    best_id = max(by_id.keys(), key=lambda k: len(by_id[k]))
    seq_map = by_id[best_id]
    assembled = ''.join(seq_map[s] for s in sorted(seq_map))
    return assembled, OrderedDict(sorted(seq_map.items()))

def main():
    pcap = sys.argv[1] if len(sys.argv) > 1 else 'unknown-traffic1.pcap'
    flag, seq_map = assemble_flag(parse_pcap_ipv4_icmp(pcap))
    if not seq_map:
        print("No tokens found.")
        sys.exit(2)
    print("[+] Identifier used:", next(iter(set([hex(k) for k in [list(seq_map.keys())[0]]])), "0x???"))
    print("[+] Sequence → token:")
    for s, tok in seq_map.items():
        print(f"    {s:>3} → {tok}")
    print("\n[+] Flag:")
    print(flag)

if __name__ == '__main__':
    main()