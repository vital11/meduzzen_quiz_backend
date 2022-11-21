from sqlalchemy import Table, Column, Integer, String, Boolean, ForeignKey, UniqueConstraint, Enum
from sqlalchemy.orm import relationship
import enum

from app.db.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)
    description = Column(String(500))
    is_private = Column(Boolean, default=False)

    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    owner = relationship("User", back_populates="companies")


class MembershipType(enum.Enum):
    invite = 'invite'
    request = 'request'


class Membership(Base):
    __tablename__ = "memberships"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    company_id = Column(Integer, ForeignKey("companies.id"))
    membership_type = Column(Enum(MembershipType))

    __table_args__ = (
        UniqueConstraint('user_id', 'company_id', 'membership_type', name='membership'),
    )


companies = Company.__table__
memberships = Membership.__table__
