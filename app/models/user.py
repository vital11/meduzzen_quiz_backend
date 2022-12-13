from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String(50))
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    companies = relationship('Company', back_populates='owner', cascade='all, delete')

    memberships = relationship('Membership', back_populates='user', cascade='all, delete')

    member_companies = relationship('Member', back_populates='member', cascade='all, delete')


users = User.__table__
