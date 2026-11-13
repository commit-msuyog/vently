
import base64
import hashlib
import hmac
import secrets


ITERATIONS = 600_000
ALGORITHM = "sha256"


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)

    password_bytes = password.encode("utf-8")

    derived_key = hashlib.pbkdf2_hmac(
        ALGORITHM,
        password_bytes,
        salt,
        ITERATIONS,
    )

    encoded_salt = base64.urlsafe_b64encode(salt).decode()
    encoded_hash = base64.urlsafe_b64encode(derived_key).decode()

    return (
        f"pbkdf2_sha256${ITERATIONS}"
        f"${encoded_salt}${encoded_hash}"
    )


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    try:
        algorithm, iterations, encoded_salt, encoded_hash = (
            hashed_password.split("$")
        )

        if algorithm != "pbkdf2_sha256":
            return False

        iterations = int(iterations)

        if not 1 <= iterations <= 1_000_000:
            return False

        salt = base64.urlsafe_b64decode(encoded_salt)
        expected_hash = base64.urlsafe_b64decode(encoded_hash)

        actual_hash = hashlib.pbkdf2_hmac(
            ALGORITHM,
            plain_password.encode("utf-8"),
            salt,
            iterations,
        )

        return hmac.compare_digest(
            actual_hash,
            expected_hash,
        )

    except (ValueError, TypeError):
        return False
