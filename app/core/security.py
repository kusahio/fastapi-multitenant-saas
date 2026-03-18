# from passlib.context import CryptContext

# pwd_context = CryptContext(
#     schemes=['bcrypt'],
#     deprecated='auto',
#     bcrypt__rounds=12
# )

import bcrypt

def hashed_password(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False
    # return pwd_context.verify(plain_password, hashed_password)
