"""
SQLAlchemy database Model for users table
"""
from datetime import datetime

from demo.database import Base
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import validates


class User(Base):
    """
    Primary table for User information.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False, unique=True)
    username = Column(String, nullable=False, unique=False)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    time_created = Column(DateTime, nullable=False, default=datetime.now())

    # Attempt to ensure consistent checks between provided values and those stored in
    # database by forcing all usernames and emails to be stored as all lowercase.
    # Stack Overflow reference for doing this:
    # https://stackoverflow.com/a/34322323/6163904
    @validates("email")
    def convert_lower(self, key, value: str):
        """
        Ensure emails are stored as all lowercase
        :param key: (Unused) The table field name
        :param value: The provided email str
        :return: A lowercase version of the email str
        """
        return value.lower()
