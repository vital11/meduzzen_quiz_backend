from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint, Enum, MetaData
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.schemas.membership import MembershipTypes


class Company(Base):
    __tablename__ = "companies"

    comp_id = Column(Integer, primary_key=True, index=True)
    comp_name = Column(String(50), unique=True, index=True)
    comp_description = Column(String(500))
    is_private = Column(Boolean, default=False)

    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    owner = relationship("User", back_populates="companies")


class Membership(Base):
    __tablename__ = "memberships"

    membership_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    company_id = Column(Integer, ForeignKey("companies.comp_id"))
    membership_type = Column(Enum(MembershipTypes))

    __table_args__ = (
        UniqueConstraint('user_id', 'company_id', 'membership_type', name='membership'),
    )


companies = Company.__table__
memberships = Membership.__table__
