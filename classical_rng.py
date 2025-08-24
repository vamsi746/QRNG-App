# classical_rng.py
import secrets

def generate_random_bits(n_bits: int) -> str:
    return format(secrets.randbits(n_bits), f"0{n_bits}b")
