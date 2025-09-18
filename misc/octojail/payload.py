#!/usr/bin/env python3
import io, os, sys, tarfile, argparse, math

MAX_OCTAL_LEN = 300_000

def make_tar(plugin_bytes: bytes) -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode='w') as tf:
        ti = tarfile.TarInfo('plugin.py')
        ti.size = len(plugin_bytes)
        ti.mode = 0o644
        ti.uid = ti.gid = 0
        ti.uname = ti.gname = ""
        ti.mtime = 0
        tf.addfile(ti, io.BytesIO(plugin_bytes))
    return buf.getvalue()

def to_octal_line(data: bytes, add_newline=True) -> str:
    s = ''.join(f'{b:03o}' for b in data)
    return s + ('\n' if add_newline else '')

def from_octal_line(s: str) -> bytes:
    s = s.strip('\n')
    if len(s) % 3 != 0:
        raise ValueError("octal length not multiple of 3")
    return bytes(int(s[i:i+3], 8) for i in range(0, len(s), 3))

def main():
    ap = argparse.ArgumentParser(description="Build octal-encoded tar payload from plugin.py")
    ap.add_argument("plugin", nargs="?", default="plugin.py", help="Path to plugin.py (default: ./plugin.py)")
    ap.add_argument("-o", "--output", default="payload.txt", help="Output file path or '-' for stdout")
    ap.add_argument("--no-newline", action="store_true", help="Do not append final newline")
    ap.add_argument("--check", action="store_true", help="Verify the generated octal decodes into a valid tar")
    args = ap.parse_args()

    try:
        with open(args.plugin, "rb") as f:
            p = f.read()
    except FileNotFoundError:
        sys.exit(f"error: cannot find {args.plugin!r}")

    tar_bytes = make_tar(p)
    octal = to_octal_line(tar_bytes, add_newline=not args.no_newline)
    octal_len = len(octal.rstrip('\n'))


    padded_data = math.ceil(len(p) / 512) * 512
    expected_tar_sz = 512 + padded_data + 1024
    print(f"plugin size: {len(p)} bytes")
    print(f"tar size (actual):   {len(tar_bytes)} bytes")
    print(f"tar size (expected): {expected_tar_sz} bytes")
    print(f"octal length: {octal_len} digits  (limit {MAX_OCTAL_LEN})")
    if octal_len > MAX_OCTAL_LEN:
        sys.exit("error: octal exceeds challenge limit")

    if args.check:
        try:
            tb = from_octal_line(octal)
            import tarfile, io
            with tarfile.open(fileobj=io.BytesIO(tb), mode='r:*') as tf:
                names = tf.getnames()
            print("check: OK, tar members:", names)
        except Exception as e:
            sys.exit(f"check failed: {e}")

    if args.output == "-":
        sys.stdout.write(octal)
    else:
        with open(args.output, "wb") as f:
            f.write(octal.encode("ascii"))
        print(f"Wrote {args.output}")

if __name__ == "__main__":
    main()
