# sigdance

![Proof](proof.png)

**Author:** `stancium`  
**Solves:** 58

**writeup made by** `vlad`
---

## Description

Dance to the rhythm of your hear...SIGKILLED

We get a few files: `main.c`, `plugin.c` and `server.py`

---

## Solve

First i opened all of the files and saw that `server.py` is simply a wraper for the compiled binary so it gets exposed over TCP.

In the file main.c we see that we see that it calls compute_counts(&A, &U), then prints Hello from pid8 = <pid & 0xff>; dynamically loads libcore.so (really plugin.c) and calls verify(provided, A, U, PID); loop: read integer from stdin -> call verify() and if true, print the flag.

So the whole challenge is: figure out what A and U are when the loop starts, and compute the token from the bannered pid8.

### Understanding compute_counts

compute_counts() sets up signal handlers and counters:

1) h_alrm: increments ac on SIGALRM.
2) h_usr1: increments uc on SIGUSR1.

It then starts a SIGALRM every 7000us, launches a thread that sends 13xSIGUSR1 to the process each 5ms apart, main thread nanosleeps for 0.777s, stops the timer and joins the thread and lastly saves ac into A and uc into U.

At first we assumed A = 0.777/0.007 = 111, U = 13. That produced huge numbers that never worked.

We then spotted the problem: interrupted sleep

After reading again we see that nanosleep is not restarted if its interupted by a signal. The first SIGUSR1 arrives after arround 5ms and the sleep immediately gets interrupted. That means that the program only runs for aproximate 5ms before disabling the timer.

This means that in those 5ms the 7ms SIGALRM never fires so ac stays 0 and even if it did manage to fire ac would be 1 at most.

The thread still finished and delivers all 13 SIGUSR1 so uc is 13.

Putting this all together to calculate the token we get:

```
token = (A << 16) ^ (13 << 8) ^ pid_low
      = 65536*A + 256*13 + pid_low
      = 65536*A + 3328 + pid_low
```
The pid_low mentioned above is what we get printed when we connect as pid8.

We than make a small script `solve.py` to try to solve this. Just to be sure i included A=1 and A=2 just to be sure.

After running the script we can it trying and sending "3399" gave us the flag.

```
Hello from pid8 = 17
Trying A=0, token=3345
CTF{cbc4e1be639219dad8912bb764b566200023e15152635eef87be047c41bd995a}
Trying A=1, token=68881

Trying A=2, token=134417

Trying A=3, token=199953
```


### Flag: CTF{cbc4e1be639219dad8912bb764b566200023e15152635eef87be047c41bd995a}