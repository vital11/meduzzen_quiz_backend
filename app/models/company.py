from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base


class Company(Base):
    __tablename__ = 'companies'

    comp_id = Column(Integer, primary_key=True, index=True)
    comp_name = Column(String(50), unique=True, index=True)
    comp_description = Column(String(500))
    is_private = Column(Boolean, default=False)

    owner_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'))
    owner = relationship('User', back_populates='companies', passive_deletes=True)

    memberships = relationship('Membership', back_populates='company', cascade='all, delete')

    members = relationship('Member', back_populates='company', cascade='all, delete')
