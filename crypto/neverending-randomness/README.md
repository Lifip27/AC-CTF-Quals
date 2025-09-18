# neverending randomness

![Proof](proof.png)

**Author:** `stancium`  
**Solves:** 31

**writeup made by** `lifip27`
 ---

## Description

I've found the holy land fo cryptograpy! Endless randomness! Enough for all! Even the unworthy. Flag format:CTF{sha256}

We get `server.py`

## Inspecting

Let's inspect the server.py

Starting with the function `seed_once()`:
```python
def seed_once():
    data=b""
    try:
        data=os.read(fd, 4096)
    except:
        data=b""
    if len(data)>=2048:
        return int.from_bytes(data,"big")
    return (int(time.time()) ^ os.getpid())
```
Each connection calls `seed_once()` once to choose the PRNG seed.   
If it can read ≥ 2048 bytes, it converts those bytes to a huge integer and uses that as the seed. That branch is unpredictable (good for defenders).  
Fallback (vulnerable branch): if it gets < 2048 bytes or the read fails, it seeds with `int(time.time()) ^ pid`, i.e., second-resolution time xor process id. Since the PID is sent to the client and “now” is known within seconds, the seed is brute-forceable in a tiny window.  

Next we have the `xor_bytes()`:
```python
def xor_bytes(a,b):
    return bytes(x^y for x,y in zip(a,b))
```

Stream-cipher pattern with XOR. This is fine only if the keystream is cryptographically secure and not reused/leaked.   
Here it’s Python’s Mersenne Twister, which is not cryptographically secure.

Know the `handle_client()`:
```python
def handle_client(c, flag):
    seed=seed_once()
    rng=random.Random(seed)
    ks=bytearray()
    while len(ks)<len(flag):
        ks.extend(rng.getrandbits(8).to_bytes(1,"big"))
    ct=xor_bytes(flag, ks[:len(flag)])
    leak=[rng.getrandbits(32) for _ in range(3)]
    out={
        "ciphertext_hex": binascii.hexlify(ct).decode(),
        "leak32": leak,
        "pid": os.getpid()
    }
    c.sendall((str(out)+"\n").encode())
```
Uses Python’s `random.Random` (MT19937) as a keystream generator. That’s not a CSPRNG.   
It generates `len(flag)` bytes for keystream, XORs with `flag` in `ciphertext`.
Critical leak: right after producing the keystream, it emits the next three 32-bit outputs of the same RNG as `leak32`. These three values uniquely fingerprint the state you’d have after generating the keystream. That gives the attacker a cheap way to test a guessed seed without even decrypting.
It also returns the PID, which halves the uncertainty in the fallback seed `(time() ^ pid)`.Lastly the `main`:
```python
def main():
    flag=os.environ.get("FLAG","you ran this locally, duh").encode()
    ...
    s.bind(("0.0.0.0",5000))
    ...
```
Plain TCP server that serves one line per connection.

We can just `DRAIN` the `/opt/app/random` so reads returm <2048 bytes.

So I vibe coded `solve.py` so it does the job and im not gonna let it run but first im gonna drain it like so:
```bash
$ for i in $(seq 1 3000); do nc ctf.ac.upt.ro 9117 >/dev/null & sleep 0.003; done; wait
python3 solve.py --host ctf.ac.upt.ro --port 9117 --window 20
```

What this does is its gonna do 3000 requests to the server and sleep for a very little time so we dont get rate limited and after 3000 requests we will use or solve.py and decrypt the flag!

Output:
```bash
[2998]   Done                    nc ctf.ac.upt.ro 9117 > /dev/null
[2999]-  Done                    nc ctf.ac.upt.ro 9117 > /dev/null
[3000]+  Done                    nc ctf.ac.upt.ro 9117 > /dev/null
[+] Fetching from ctf.ac.upt.ro:9117 ...
[+] Service line: {'ciphertext_hex': '8ead9db3e79d39964fecbb29c33ad38433af739e4829259ff23a68be3b111e8345b33f9084195be360bc6ef664140c00f6504d867dbfb6978cf867fcf5b4eb879d217502e8', 'leak32': [1326420283, 3297517928, 4098103181], 'pid': 7}
[+] Found seed 1758209153 (time 2025-09-18 15:25:58 UTC)
[+] Plaintext: CTF{1bac99dddbcb8c532891bb5f1f3bc0feeac9037f18e575ef9d4f0805dc4d6893}
[+] FLAG: CTF{1bac99dddbcb8c532891bb5f1f3bc0feeac9037f18e575ef9d4f0805dc4d6893}
```

### Flag: CTF{1bac99dddbcb8c532891bb5f1f3bc0feeac9037f18e575ef9d4f0805dc4d6893}
