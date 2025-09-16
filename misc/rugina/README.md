# Rugină

![Proof](proof.png)

**Author:** `thek0der`  
**Solves:** 36

---

## Description

A brand new language is born — **Rugină** (Rust in Romanian).  
They give us a compiler web UI where we can paste our “Rugină” code, compile, and see the output.  
Of course, the flag is hidden in the container. Can we grab it?

---

## Solve

The compiler replaces `principal { ... }` with a `fn main { ... }` function and then runs **rustc**.  
All compiler errors are shown back to us in the browser.  
That means we can abuse Rust compile-time macros:

- `include_str!("/path")` reads a file at **compile time**  
- `compile_error!(...)` stops compilation and prints a message

So if we wrap the flag file in `compile_error!(include_str!(...))`, the compiler error will literally contain the file contents.

Final payload:

```rust
principal { compile_error!(include_str!("/flag.txt")); }
```
![flag](flag.png)

### Flag: ctf{73523e676b04e1c2db176d8035648893648b969f5ddf5ac40f8fc5b6c15d8692}