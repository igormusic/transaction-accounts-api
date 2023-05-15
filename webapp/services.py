"""Services module."""

from uuid import uuid4
from typing import Iterator

from accounts.metadata import AccountType
from accounts.runtime import Account

from .repositories import AccountTypeRepository, AccountRepository


class AccountTypeService:

    def __init__(self, account_type_repository: AccountTypeRepository) -> None:
        self._repository: AccountTypeRepository = account_type_repository

    def get_account_types(self) -> Iterator[AccountType]:
        return self._repository.get_account_types()

    def get_account_type_by_name(self, name: str) -> AccountType:
        return self._repository.get_account_type_by_name(name)

    def create_account_type(self, account_type: AccountType) -> None:
        return self._repository.create_account_type(account_type)

    def delete_account_type(self, name: str) -> None:
        return self._repository.delete_account_type(name)


class AccountService:

    def __init__(self, account_repository: AccountRepository) -> None:
        self._repository: AccountRepository = account_repository

    def get_accounts(self) -> Iterator[Account]:
        return self._repository.get_accounts()

    def get_account_by_id(self, id: int) -> Account:
        return self._repository.get_account_by_id(id)

    def create_account(self, account: Account) -> None:
        return self._repository.create_account(account)

    def delete_account(self, account_id: int) -> None:
        return self._repository.delete_account(account_id)
