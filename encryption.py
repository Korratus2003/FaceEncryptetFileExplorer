from cryptography.fernet import Fernet
import base64
import hashlib
import os

def get_fernet_key_from_biometric_key(biometric_key_hex: str) -> bytes:
    # Konwersja klucza biometrycznego (hex) na 32-bajtowy klucz dla Fernet
    key_bytes = bytes.fromhex(biometric_key_hex)
    key_hash = hashlib.sha256(key_bytes).digest()
    return base64.urlsafe_b64encode(key_hash)

def encrypt_file(file_path: str, biometric_key_hex: str) -> str:
    fernet_key = get_fernet_key_from_biometric_key(biometric_key_hex)
    fernet = Fernet(fernet_key)

    with open(file_path, "rb") as f:
        data = f.read()
    encrypted = fernet.encrypt(data)

    out_path = file_path + ".enc"
    with open(out_path, "wb") as f:
        f.write(encrypted)
    return out_path

def decrypt_file(file_path: str, biometric_key_hex: str) -> str:
    if not file_path.endswith(".enc"):
        raise ValueError("Plik do odszyfrowania powinien mieć rozszerzenie '.enc'")

    fernet_key = get_fernet_key_from_biometric_key(biometric_key_hex)
    fernet = Fernet(fernet_key)

    with open(file_path, "rb") as f:
        data = f.read()
    decrypted = fernet.decrypt(data)

    out_path = file_path[:-4]  # usuwamy ".enc"
    # Zabezpieczenie: jeśli plik docelowy istnieje, dodajemy sufiks, aby nie nadpisać
    if os.path.exists(out_path):
        base, ext = os.path.splitext(out_path)
        out_path = f"{base}_decrypted{ext}"

    with open(out_path, "wb") as f:
        f.write(decrypted)
    return out_path
