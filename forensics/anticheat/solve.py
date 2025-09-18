import sys,struct,base64,zlib,re,zipfile
from pathlib import Path

KEYMASK=[0xB1,0x54,0x45,0x57,0xA7,0xC4,0x64,0x2E,0x98,0xD8,0xB1,0x1A,0x0B,0xAA,0xD8,0x8E,0x7F,0x1E,0x5B,0x8D,0x08,0x67,0x96,0xCB,0xAA,0x11,0x50,0x84,0x17,0x46,0xA3,0x30]
FLAG_RE=re.compile(r'(?i)\b(?:flag|ctf)\{.*?\}')

def rc4(data,key):
    S=list(range(256));j=0
    for i in range(256):
        j=(j+S[i]+key[i%len(key)])&0xFF;S[i],S[j]=S[j],S[i]
    i=j=0;out=bytearray()
    for b in data:
        i=(i+1)&0xFF; j=(j+S[i])&0xFF; S[i],S[j]=S[j],S[i]; out.append(b ^ S[(S[i]+S[j])&0xFF])
    return bytes(out)

def decrypt_bytes(blob):
    if len(blob)<36: return ""
    b=blob[4:]; real=[b[i]^KEYMASK[i] for i in range(32)]; b=b[32:]; parts=[]
    while len(b)>=4:
        n=struct.unpack_from("<I",b,0)[0]; b=b[4:]
        if n>len(b) or n<=0: break
        dec=rc4(b[:n],real); b=b[n:]
        for enc in ("utf-16","utf-16-le","utf-8","latin-1"):
            try:
                parts.append(dec.decode(enc)); break
            except: pass
    return "".join(parts)

def postproc(s):
    raw=s.strip().encode("ascii",errors="ignore")
    try: b=base64.b64decode(raw,validate=True)
    except: return None
    try: b=zlib.decompress(b); step="base64+zlib"
    except: step="base64"
    for enc in ("utf-8","utf-16","utf-16-le","latin-1"):
        try: return b.decode(enc)
        except: pass
    return repr(b)

def scan_buf(name,blob,results):
    dec=decrypt_bytes(blob)
    if dec:
        for m in FLAG_RE.findall(dec): results.append((name,m))
        p=postproc(dec)
        if p:
            for m in FLAG_RE.findall(p): results.append((name,m))
    for m in FLAG_RE.findall(blob.decode("latin-1",errors="ignore")): results.append((name,m))

def iter_files(path):
    p=Path(path)
    if p.suffix.lower()==".zip":
        with zipfile.ZipFile(p,"r") as z:
            for info in z.infolist():
                if info.is_dir(): continue
                yield info.filename, z.read(info)
    elif p.is_dir():
        for f in p.rglob("*"):
            if f.is_file(): yield str(f), f.read_bytes()
    elif p.is_file():
        yield p.name, p.read_bytes()

if __name__=="__main__":
    hits=[]; total=0
    for name,blob in iter_files(sys.argv[1]):
        total+=1
        scan_buf(name,blob,hits)
    for fn,flag in hits:
        print(f"{fn}: {flag}")
    print(f"scanned {total} files, found {len(hits)} hits")
