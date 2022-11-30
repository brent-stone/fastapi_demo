"""
Password hashing and comparison functions
"""
from typing import Optional

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Hasher:
    """
    Class for hashing passwords and verifying hashes match
    """

    @staticmethod
    def verify_password(plain_password, hashed_password):
        """
        Verify that a hashing a plantext password matches an expected hash
        :param plain_password: A plaintext version of the password
        :param hashed_password: The reference hash
        :return: True if they match, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(plain_password) -> Optional[str]:
        """
        Convert a plaintext password into a hashed representation
        :param plain_password: Input plaintext password
        :return: A hashed representation; else, None if input was None
        """
        if plain_password is None:
            return None
        return pwd_context.hash(plain_password)
