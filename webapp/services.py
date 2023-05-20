"""Services module."""
from datetime import datetime, date
from typing import Iterator, List

from accounts.metadata import AccountType
from accounts.runtime import Account, AccountValuation

from .models import AccountInfo
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

    def __init__(self, account_repository: AccountRepository, account_type_repository: AccountTypeRepository) -> None:
        self._repository: AccountRepository = account_repository
        self._account_type_repository: AccountTypeRepository = account_type_repository

    def get_accounts(self) -> List[AccountInfo]:
        return self._repository.get_accounts()

    def get_account_by_id(self, id: int) -> AccountInfo:
        return self._repository.get_account_by_id(id)

    def create_account(self, account_prototype: Account) -> AccountInfo:
        account_type = self._account_type_repository.get_account_type_by_name(account_prototype.account_type_name)

        # validate properties, initialize positions, schedules, instalment
        account = Account(start_date=account_prototype.start_date,
                          account_type_name=account_prototype.account_type_name,
                          account_type=account_type,
                          value_dated_properties=account_prototype.value_dated_properties,
                          properties=account_prototype.properties,
                          dates=account_prototype.dates)

        return self._repository.create_account(account)

    def delete_account(self, account_id: int) -> None:
        return self._repository.delete_account(account_id)

    def update_account(self, account_id: int, active: bool, account: Account) -> AccountInfo:
        self._repository.update_account(account_id, active, account)

    def solve(self, account_id: int) -> AccountValuation:
        account_info = self._repository.get_account_by_id(account_id)
        account = account_info.account
        account_type = self._account_type_repository.get_account_type_by_name(account.account_type_name)

        end_date = account.dates["end_date"] if "end_date" in account.dates.keys() \
            else datetime.strptime(max(account.instalments.keys()), '%Y-%m-%d').date()

        valuation = AccountValuation(account, account_type, end_date, False)

        payment = valuation.solve_instalment()

        return valuation

    def value(self, account_id: int, action_date: date) -> AccountValuation:
        account_info = self._repository.get_account_by_id(account_id)
        account = account_info.account
        account_type = self._account_type_repository.get_account_type_by_name(account.account_type_name)

        valuation = AccountValuation(account=account, account_type=account_type, action_date=action_date, trace=True)

        valuation.forecast(action_date, {})

        return valuation
