from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.sql.schema import Column

from demo_backend.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
