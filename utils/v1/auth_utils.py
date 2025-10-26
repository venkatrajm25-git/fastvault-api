import bcrypt


def hash_password(password: str) -> str:
    # Generate a salt
    salt = bcrypt.gensalt()  # default cost=12
    # Hash the password
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )
