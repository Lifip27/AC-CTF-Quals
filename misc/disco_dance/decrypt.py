import base64
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Util.Padding import unpad

# Correct order: newest first
seed = "ZJD5432".encode()
key = SHA256.new(seed).digest()

enc_b64 = "ezf87eRXMXwhzATMXPDr2gLo7wFUPk17Bv893DJJn+CuJGJcFTS05FGbGoNBO6AIavKg1r8FF3MCv/sL54HpksjytTqAjIoZDTSgSzIvjmLvvp/lR94e6ecOppmiIGpC"
blob = base64.b64decode(enc_b64)

iv, ct = blob[:16], blob[16:]
cipher = AES.new(key, AES.MODE_CBC, iv)
pt = unpad(cipher.decrypt(ct), AES.block_size)
print(pt.decode())
