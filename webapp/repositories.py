"""Repositories module."""

from contextlib import AbstractContextManager
from typing import Callable, Iterator, List

from accounts.metadata import AccountType
from accounts.runtime import Account
from sqlalchemy.orm import Session
from .models import AccountTypeData, AccountData


class AccountTypeRepository:
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]) -> None:
        self.session_factory = session_factory

    def get_account_types(self) -> List[AccountType]:
        with self.session_factory() as session:
            accounts = session.query(AccountTypeData).all()
            return [AccountType.parse_raw(account.model) for account in accounts]

    def get_account_type_by_name(self, name: str) -> AccountType:
        with self.session_factory() as session:
            account = session.query(AccountTypeData).filter(AccountTypeData.name == name).first()

        if not account:
            raise AccountTypeNotFound(name)
        return AccountType.parse_raw(account.model)

    def create_account_type(self, account_type: AccountType) -> None:
        with self.session_factory() as session:
            account_type_obj = AccountTypeData(name=account_type.name, model=account_type.json())
            session.add(account_type_obj)
            session.commit()
            session.refresh(account_type_obj)

    def delete_account_type(self, name: str) -> None:
        with self.session_factory() as session:
            account = session.query(AccountTypeData).filter(AccountTypeData.name == name).first()
            if not account:
                raise AccountTypeNotFound(name)
            session.delete(account)
            session.commit()


class AccountRepository:
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]) -> None:
        self.session_factory = session_factory

    def get_accounts(self) -> List[Account]:
        with self.session_factory() as session:
            accounts = session.query(AccountData).all()
            return [Account.parse_raw(account.model) for account in accounts]

    def get_account_by_id(self, id: int) -> Account:
        with self.session_factory() as session:
            account = session.query(AccountData).filter(AccountData.account_id == id).first()

        if not account:
            raise AccountNotFound(id)
        return Account.parse_raw(account.model)

    def create_account(self, account: Account) -> int:
        with self.session_factory() as session:
            account_obj = AccountData(account_type=account.account_type_name, active=False, model=account.json())
            session.add(account_obj)
            session.commit()
            session.refresh(account_obj)

        return account_obj.account_id

    def delete_account(self, id: int) -> None:
        with self.session_factory() as session:
            account = session.query(AccountData).filter(AccountData.account_id == id).first()
            if not account:
                raise AccountNotFound(id)
            session.delete(account)
            session.commit()

    def update_account(self, account_id: int, account: Account, active: bool) -> None:
        with self.session_factory() as session:
            account_obj = session.query(AccountData).filter(AccountData.account_id == account_id).first()
            if not account_obj:
                raise AccountNotFound(account_id)
            account_obj.model = account.json()
            account_obj.active = active
            session.commit()


class NotFoundError(Exception):
    entity_name: str


class AccountTypeNotFound(NotFoundError):
    entity_name: str = "AccountType"

    def __init__(self, name):
        super().__init__(f"{self.entity_name} not found, name: {name}")


class AccountNotFound(NotFoundError):
    entity_name: str = "Account"

    def __init__(self, id):
        super().__init__(f"{self.entity_name} not found, name: {id}")
