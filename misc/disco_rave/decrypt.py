import base64, json, requests
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Util.Padding import unpad

TOKEN = "token"
CHANNELS = [
    "1416908413375479891",  # spam
    "1417154025371209852",  # spam++
]

def get_seed():
    headers = {"Authorization": TOKEN}
    all_data = []
    for cid in CHANNELS:
        url = f"https://discord.com/api/v10/channels/{cid}/messages?limit=10"
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        msgs = r.json()
        for m in msgs:
            all_data.append(m["content"] + m["timestamp"])
    return "".join(all_data).encode()

def decrypt(enc_b64, seed):
    blob = base64.b64decode(enc_b64)
    iv, ct = blob[:16], blob[16:]
    key = SHA256.new(seed).digest()
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    return pt.decode()

if __name__ == "__main__":
    seed = get_seed()
    print("Seed captured (SHA256 key derived).")

    enc_b64 = input("Paste encrypted base64: ").strip()
    try:
        flag = decrypt(enc_b64, seed)
        print("FLAG:", flag)
    except Exception as e:
        print("Error:", e)
