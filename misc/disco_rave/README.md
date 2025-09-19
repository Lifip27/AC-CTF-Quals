# disco_rave

![Proof](proof.png)

**Author:** `unknown`  
**Solves:** 19

**writeup made by** `vlad`
---

## Description

This is so infuriating! I know exactly what to do , but those damn trolls won't let me ! This feels like that prisoner's dilema I heard about. Automatic spam will be banned, manual spam is fine. Flag format: CTF{sha256}

We are given `routes.ts` and `server.py`

---

## Solve

First i looked at the files provided and i see that in `server.py` the randomness is not random at all. The AES key is `SHA256(seed)`, where seed is the concatenation of `content + timestamp` of the last 10 messages from 2 discord channels.

The IV is random, but that doesn’t matter because we can recompute the key.

So if we can read the same messages, we can decrypt the ciphertext.

At first i was thinking we need to somehow exploit the fake token being replaced by the real one in route.ts but after looking in the discord server i saw that there is a channel called spam with the id from in the code.

I made a small script `decrypt.py` which makes the same api calls as the remote saving the last 10 messages content and timestamp.

First we run the script and than run the netcat connection to get our base64 encrypted stirng. Once we have the seed captures and the encrypted flag we just paste only the base64 part into the terminal and it prints out the flag.

### Note: For the script to work a discord token that has access to both channels is needed.


### Flag: CTF{a83a34f8791905a4edd6e03beefeddc1c7eeeeeacf9d96af6d1e3c34494df4cc}