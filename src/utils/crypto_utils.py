import bcrypt
import base64


def hash_password(password: str) -> str:
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    encoded_hashed_password = base64.b64encode(hashed_password).decode('utf-8')
    return encoded_hashed_password


def verify_password(password: str, hashed_password: str) -> bool:
    password_byte_enc = password.encode("utf-8")
    hashed_password = base64.b64decode(hashed_password)
    return bcrypt.checkpw(password=password_byte_enc, hashed_password=hashed_password)
