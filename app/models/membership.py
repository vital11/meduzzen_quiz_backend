from sqlalchemy import Column, Integer, Boolean, ForeignKey, UniqueConstraint, Enum
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.schemas.membership import MembershipTypes


class Membership(Base):
    __tablename__ = 'memberships'

    membership_id = Column(Integer, primary_key=True, index=True)
    membership_type = Column(Enum(MembershipTypes))

    company_id = Column(Integer, ForeignKey('companies.comp_id', ondelete='CASCADE', onupdate='CASCADE'))
    company = relationship('Company', back_populates='memberships')

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'))
    user = relationship('User', back_populates="memberships")

    __table_args__ = (
        UniqueConstraint('user_id', 'company_id', 'membership_type', name='membership'),
    )


class Member(Base):
    __tablename__ = 'members'

    m_id = Column(Integer, primary_key=True, index=True)
    is_admin = Column(Boolean, default=False)

    company_id = Column(Integer, ForeignKey('companies.comp_id', ondelete='CASCADE', onupdate='CASCADE'))
    company = relationship('Company', back_populates='members')

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'))
    member = relationship('User', back_populates="member_companies")

    __table_args__ = (
        UniqueConstraint('user_id', 'company_id', 'is_admin', name='unique_member'),
    )
