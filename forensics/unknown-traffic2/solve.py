import struct, socket, re, base64, hashlib

PCAP = 'traffic.pcap'

MAGICS = {b'\xd4\xc3\xb2\xa1': '<', b'\xa1\xb2\xc3\xd4': '>', b'\x4d\x3c\xb2\xa1': '<', b'\xa1\xb2\x3c\x4d': '>'}

# wireshark pcap byte order 
def endian(path):
    with open(path,'rb') as f:
        m=f.read(4)
    if m not in MAGICS: raise SystemExit('Unknown pcap magic: '+m.hex())
    return MAGICS[m]

# reading the pcap packets
def read_ipv4_packets(path):
    pkts=[]; e = endian(path)
    with open(path,'rb') as f:
        f.read(24)
        while True:
            hdr=f.read(16)
            if not hdr or len(hdr)<16: break
            ts_sec, ts_usec, incl_len, orig_len = struct.unpack(e+'IIII', hdr)
            data=f.read(incl_len)
            if len(data)<20 or (data[0]>>4)!=4: continue
            ihl=(data[0] & 0x0F)*4; proto=data[9]
            src = socket.inet_ntoa(data[12:16]); dst = socket.inet_ntoa(data[16:20])
            payload = data[ihl:]
            pkts.append((proto, src, dst, payload))
    return pkts
# Skips link-layer entirely (the file’s linktype is IPv4).
# Pulls out protocol (proto=6 TCP, 17 UDP, 1 ICMP), source/dest IPs, and the L4 payload.

pkts = read_ipv4_packets(PCAP)

http, udp12345, icmp = {}, {}, {}

for proto,src,dst,p in pkts:
    if proto==6:  # TCP
        if len(p)<20: continue
        off = ((p[12]>>4)&0xF)*4; pl = p[off:]
        s=pl.decode('ascii','ignore')
        m=re.search(r'GET /data\?chunk=(\d+)&data=([A-Za-z0-9+/=]+)', s)
        if m: http[int(m.group(1))]=m.group(2)
    elif proto==17:  # UDP
        if len(p)<8: continue
        dport = struct.unpack('!H', p[2:4])[0]
        pl=p[8:]
        if dport==12345:
            m=re.match(r'QRDATA(\d{3})#([A-Za-z0-9+/=]+)', pl.decode('ascii','ignore'))
            if m: udp12345[int(m.group(1))]=m.group(2)
    elif proto==1:  # ICMP
        pl=p[4:]
        s=pl.decode('ascii','ignore')
        m=re.search(r'CHUNK_(\d{3}):([A-Za-z0-9+/=]+)', s)
        if m: icmp[int(m.group(1))]=m.group(2)

srcmap = http if len(http)==97 else (udp12345 if len(udp12345)==97 else icmp)

b64 = ''.join(srcmap[i] for i in range(97))
img = base64.b64decode(b64)

open('exfil.png','wb').write(img)
print('wrote exfil.png ({} bytes)'.format(len(img)))
print('sha256:', hashlib.sha256(img).hexdigest())