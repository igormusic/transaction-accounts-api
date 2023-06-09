"""Endpoints module."""
from datetime import date
from typing import List, Union

from accounts.metadata import AccountType
from accounts.runtime import Account, AccountValuation
from fastapi import APIRouter, Depends, Response, status
from dependency_injector.wiring import inject, Provide
from starlette.responses import JSONResponse, Response

from .containers import Container
from .models import AccountInfo, ForcastResult
from .services import AccountTypeService, AccountService
from .repositories import NotFoundError
import logging

router = APIRouter()

# configure the logging module
logging.basicConfig(filename='app.log', level=logging.INFO)


@router.get("/status")
def get_status():
    return {"status": "OK"}


@router.get("/accounttypes")
@inject
def get_account_types(
        account_type_service: AccountTypeService = Depends(Provide[Container.account_type_service]),
):
    return account_type_service.get_account_types()


@router.get("/accounttypes/{name}")
@inject
def get_account_type_by_name(
        name: str,
        account_type_service: AccountTypeService = Depends(Provide[Container.account_type_service]),
):
    try:
        return account_type_service.get_account_type_by_name(name)
    except NotFoundError:
        return Response(status_code=status.HTTP_404_NOT_FOUND)


@router.post("/accounttypes", status_code=status.HTTP_201_CREATED)
@inject
def create_account_type(
        account_type: AccountType,
        account_type_service: AccountTypeService = Depends(Provide[Container.account_type_service]),
):
    try:
        return account_type_service.create_account_type(account_type)
    except NotFoundError:
        return Response(status_code=status.HTTP_404_NOT_FOUND)


@router.delete("/accounttypes/{name}", status_code=status.HTTP_204_NO_CONTENT)
@inject
def delete_account_type(
        name: str,
        account_type_service: AccountTypeService = Depends(Provide[Container.account_type_service]),
):
    try:
        account_type_service.delete_account_type(name)
    except NotFoundError:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/accounts/", status_code=status.HTTP_201_CREATED)
@inject
def create_account(
        account: Account,
        account_service: AccountService = Depends(Provide[Container.account_service])):
    try:
        account_info = account_service.create_account(account)
    except Exception as e:
        logging.error(e)
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    else:
        return account_info


@router.get("/accounts/")
@inject
def get_accounts(
        account_service: AccountService = Depends(Provide[Container.account_service]),
) -> List[AccountInfo]:
    return account_service.get_accounts()


@router.get("/accounts/{account_id}")
@inject
def get_account_by_id(
        account_id: int,
        account_service: AccountService = Depends(Provide[Container.account_service])):
    try:
        return account_service.get_account_by_id(account_id)
    except NotFoundError:
        return Response(status_code=status.HTTP_404_NOT_FOUND)


@router.delete("/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
def delete_account(
        account_id: int,
        account_service: AccountService = Depends(Provide[Container.account_service]),
):
    try:
        account_service.delete_account(account_id)
    except NotFoundError:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/accounts/{account_id}/value")
@inject
def value_account(
        account_id: int,
        action_date: date,
        account_service: AccountService = Depends(Provide[Container.account_service])) -> ForcastResult:
    try:
        valuation = account_service.value(account_id, action_date)

        return ForcastResult(account_id=account_id, account= valuation.account, trace_list=valuation.trace_list)

    except Exception as e:
        logging.error(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/accounts/{account_id}/solve")
@inject
def solve_account(
        account_id: int,
        account_service: AccountService = Depends(Provide[Container.account_service])):
    try:
        valuation = account_service.solve(account_id)

        # reset the transactions, too many to return
        valuation.account.transactions = []

        return valuation.account

    except Exception as e:
        logging.error(e)
        return Response(status_code=status.HTTP_404_NOT_FOUND)


@router.put("/accounts/{account_id}")
@inject
def update_account(
        account_id: int,
        active: bool,
        account: Account,
        account_service: AccountService = Depends(Provide[Container.account_service])):
    try:
        account_service.update_account(account_id, active, account)
    except NotFoundError:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
