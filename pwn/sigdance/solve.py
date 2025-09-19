import re, socket

HOST, PORT = "ctf.ac.upt.ro", 9893

s = socket.create_connection((HOST, PORT))
banner = s.recv(1024).decode(errors="ignore")
print(banner.strip())
pid_low = int(re.search(r'pid8\s*=\s*(\d+)', banner).group(1))

U = 13
for A in range(0, 4):
    token = ((A << 16) ^ (U << 8) ^ pid_low) & 0xffffffff
    print(f"Trying A={A}, token={token}")
    s.sendall(f"{token}\n".encode())
    out = s.recv(4096).decode(errors="ignore")
    print(out.strip())
    if "FLAG{" in out:
        break

s.close()