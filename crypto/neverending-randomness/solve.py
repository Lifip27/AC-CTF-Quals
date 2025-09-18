import argparse, socket, time, ast, random, re, sys

def fetch_one_line(host, port, timeout=1.0):
    with socket.create_connection((host, port), timeout=timeout) as s:
        data = b""
        while not data.endswith(b"\n"):
            chunk = s.recv(4096)
            if not chunk:
                break
            data += chunk
    return data.decode(errors="replace").strip()

def parse_line(line):
    d = ast.literal_eval(line.strip())
    ct = bytes.fromhex(d["ciphertext_hex"])
    leak = list(map(int, d["leak32"]))
    pid = int(d["pid"])
    return ct, leak, pid

def seed_matches(seed, nbytes, leak):
    r = random.Random(seed)
    for _ in range(nbytes):
        r.getrandbits(8)
    return [r.getrandbits(32) for _ in range(3)] == leak

def brute(ct, leak, pid, window):
    n = len(ct)
    now = int(time.time())
    offsets = [0]
    for i in range(1, window + 1):
        offsets += (i, -i)
    for off in offsets:
        t = now + off
        seed = t ^ pid
        if seed_matches(seed, n, leak):
            r = random.Random(seed)
            ks = bytes(r.getrandbits(8) for _ in range(n))
            pt = bytes(c ^ k for c, k in zip(ct, ks))
            return t, seed, pt
    return None, None, None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", required=True)
    ap.add_argument("--port", required=True, type=int)
    ap.add_argument("--window", type=int, default=30)
    args = ap.parse_args()

    print(f"[+] Fetching from {args.host}:{args.port} ...")
    line = fetch_one_line(args.host, args.port)
    print("[+] Service line:", line)
    ct, leak, pid = parse_line(line)

    t, seed, pt = brute(ct, leak, pid, args.window)
    if t is None:
        print("[-] No seed found in this window. Try larger --window.")
        sys.exit(2)

    print(f"[+] Found seed {seed} (time {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(t))} UTC)")
    try:
        print("[+] Plaintext:", pt.decode())
    except:
        print("[+] Plaintext (repr):", repr(pt))
    m = re.search(rb"CTF\{[0-9a-fA-F]{64}\}", pt)
    if m:
        print("[+] FLAG:", m.group(0).decode())

if __name__ == "__main__":
    main()
