"""Containers module."""
import os

from dependency_injector import containers, providers
from webapp.database import Database
from webapp.repositories import AccountTypeRepository, AccountRepository
from webapp.services import AccountTypeService, AccountService


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=[".endpoints"])

    db_url = os.environ['ACCOUNTS_DB_URL']

    db = providers.Singleton(Database, db_url=db_url)

    account_type_repository = providers.Factory(
        AccountTypeRepository,
        session_factory=db.provided.session,
    )

    account_type_service = providers.Factory(
        AccountTypeService,
        account_type_repository=account_type_repository,
    )

    account_repository = providers.Factory(
        AccountRepository,
        session_factory=db.provided.session,
    )

    account_service = providers.Factory(
        AccountService,
        account_repository=account_repository,
        account_type_repository=account_type_repository,
    )






