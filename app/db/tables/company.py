from sqlalchemy import Table, Column, Integer, String, Boolean, ForeignKey

from app.db.database import metadata
from app.db.tables.user import users

companies = Table(
    'companies',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(50), unique=True, index=True, nullable=False),
    Column('description', String(500)),
    Column('is_private', Boolean, default=False),
    Column('owner_id', Integer, ForeignKey('users.id'), nullable=False),
)

admins = Table(
    'admins',
    metadata,
    Column('user_id', ForeignKey(users.c.id)),
    Column('company_id', ForeignKey(companies.c.id)),
)

members = Table(
    'members',
    metadata,
    Column('user_id', ForeignKey(users.c.id)),
    Column('company_id', ForeignKey(companies.c.id)),
)
