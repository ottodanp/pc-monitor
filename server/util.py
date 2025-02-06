from hashlib import sha256


def hash_auth_code(auth_code: str) -> str:
    return sha256(auth_code.encode()).hexdigest()
