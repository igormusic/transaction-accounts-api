"""Models module."""

from sqlalchemy import Column, String, Boolean, Integer, JSON

from .database import Base


class AccountTypeData(Base):
    __tablename__ = 'account_types'
    name = Column(String, primary_key=True, index=True)
    model = Column(JSON)
