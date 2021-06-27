import hashlib

def calculate_hash(private_key: str, public_key: str,) -> str:
    m = hashlib.sha256()
    m.update(private_key.encode('utf-8'))
    m.update(public_key.encode('utf-8'))

    return m.digest().hex()


def verify_hash(private_key: str, public_key: str, our_hash: str) -> bool:
    return calculate_hash(private_key, public_key,) == our_hash