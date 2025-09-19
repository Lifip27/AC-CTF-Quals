# disco_dance

![Proof](proof.png)

**Author:** `unknown`  
**Solves:** 22

**writeup made by** `vlad`
---

## Description

I heard disco parties can be pretty random and chaotic. Let’s see just how chaotic. Flag format: CTF{sha256}

We are given `routes.ts` and `server.py`

---

## Solve

First i looked at the files provided and i see that in `server.py` the randomness is not random at all. The AES key is `SHA256(seed)`, where seed is the concatenation of the last 5 Discord messages from channel `1416908413375479891`.

The IV is random, but that doesn’t matter because we can recompute the key.

So if we can read the same messages, we can decrypt the ciphertext.

At first i was thinking we need to somehow exploit the fake token being replaced by the real one in route.ts but after looking in the discord server i saw that there is a channel called spam with the id from in the code.

I waited for a moment when not many people were talking and started typing 1, 2, 3, 4, 5 someone managed to type somthing random after 5 buts its fine, i connected to the remote and locked in the encrypted the base64.

I made a small script `decrypt.py` where i put in the messages together, the base64 and it decrypts it and prints out the flag.


### Flag: CTF{f55ba4939edd5611a7ab797529b51dae47989b3c5a99f2ffc82e4b2c74d03e56}