"""Models module."""
from typing import List

from accounts.runtime import Account, TransactionTrace
from pydantic.main import BaseModel
from sqlalchemy import Column, String, Boolean, Integer, JSON

from .database import Base


class AccountTypeData(Base):
    __tablename__ = 'account_types'
    name = Column(String, primary_key=True, index=True)
    model = Column(JSON)


class AccountData(Base):
    __tablename__ = 'accounts'
    account_id = Column(Integer, primary_key=True, index=True)
    account_type = Column(String, index=True)
    active = Column(Boolean, default=True)
    model = Column(JSON)


class AccountInfo(BaseModel):
    account_id: int
    active: bool
    account: Account


class ForcastResult(BaseModel):
    account_id: int
    account: Account
    trace_list: List[TransactionTrace]
