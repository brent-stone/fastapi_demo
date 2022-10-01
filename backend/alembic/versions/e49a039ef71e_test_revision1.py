"""test revision1

Revision ID: e49a039ef71e
Revises: c382d26779b8
Create Date: 2022-09-05 13:20:02.835252

"""
from alembic import op
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String


# revision identifiers, used by Alembic.
revision = "e49a039ef71e"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Add postgres user empty table and functional 'user' and 'job' tables.
    """
    # Create the user table
    op.create_table(
        "user",
        Column("id", Integer, primary_key=True, index=True),
        Column("username", String, unique=True, nullable=False),
        Column("email", String, nullable=False, unique=True, index=True),
        Column("hashed_password", String, nullable=False),
        Column("is_active", Boolean, default=True),
        Column("is_superuser", Boolean, default=False),
    )

    # Create the job table
    op.create_table(
        "job",
        Column("id", Integer, primary_key=True, index=True),
        Column("title", String, nullable=False),
        Column("company", String, nullable=False),
        Column("company_url", String),
        Column("location", String, nullable=False),
        Column("description", String),
        Column("date_posted", Date),
        Column("is_active", Boolean, default=True),
        Column("owner_id", Integer, ForeignKey("user.id")),
    )


def downgrade() -> None:
    """
    Drop all the tables created by this version.
    """
    op.drop_table("user")
    op.drop_table("job")
