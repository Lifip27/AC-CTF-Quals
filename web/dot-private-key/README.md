# dot-private-key

![Proof](proof.png)   

**Author:** `RaduTek`  
**Solves:** 26

---

## Description

Our security researcher has found this dubious website claiming to check any private keys for potential breaches in a secure manner. They think otherwise.

Attached are some clean keys that our researcher tried to check with the website a few days ago. Curiously, they have been exposed since.

Your task is to see if this website is truly up to what it claims.

we get `keys.txt`

## Solve

I found a vulnerability in this challenge particular to /dump

```bash
$ curl http://ctf.ac.upt.ro:9239/dump
...
ctf{...}
```

This would just leak absolut everything even the flag.