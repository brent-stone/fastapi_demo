from demo_backend.database import Base
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.orm import validates


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    jobs = relationship("Job", back_populates="owner")

    # Attempt to ensure consistent checks between provided values and those stored in
    # database by forcing all usernames and emails to be stored as all lowercase.
    # StackOverlow reference for doing this:
    # https://stackoverflow.com/a/34322323/6163904
    @validates("username", "email")
    def convert_lower(self, key, value: str):
        return value.lower()
