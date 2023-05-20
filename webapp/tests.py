"""Tests module."""
import json
from datetime import date
from decimal import Decimal
from unittest import mock

import pytest
from accounts.metadata import AccountType, ScheduleType, TransactionOperation, ScheduledTransactionTiming, DataType, \
    ScheduleEndType, ScheduleFrequency, BusinessDayAdjustment
from accounts.runtime import Account
from dependency_injector.wiring import Provide
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool

from . import endpoints
from .containers import Container
from .database import Base, Database
from .repositories import NotFoundError, AccountTypeRepository, AccountRepository
from .services import AccountService


def create_test_app():
    container = Container()

    db = Database(
        engine=create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, echo=True,
                             poolclass=StaticPool))

    container.db.override(db)

    db.create_database()

    test_app = FastAPI()
    test_app.container = container
    test_app.include_router(endpoints.router)
    return test_app


app = create_test_app()


@pytest.fixture
def client():
    yield TestClient(app)


def test_get_account_type_list(client):
    repository_mock = mock.Mock(spec=AccountTypeRepository)
    repository_mock.get_account_types.return_value = [
        AccountType(name="saving", label="Saving Account"),
        AccountType(name="checking", label="Checking Account"),
    ]

    with app.container.account_type_repository.override(repository_mock):
        response = client.get("/accounttypes")

    assert response.status_code == 200
    data = response.json()
    assert data == [{'name': 'saving', 'label': 'Saving Account', 'transaction_types': [], 'position_types': [],
                     'date_types': [], 'rate_types': {}, 'triggered_transactions': [], 'schedule_types': [],
                     'property_types': [], 'scheduled_transactions': [], 'instalment_type': None},
                    {'name': 'checking', 'label': 'Checking Account', 'transaction_types': [], 'position_types': [],
                     'date_types': [], 'rate_types': {}, 'triggered_transactions': [], 'schedule_types': [],
                     'property_types': [], 'scheduled_transactions': [], 'instalment_type': None}]


def test_get_account_type_by_id(client):
    repository_mock = mock.Mock(spec=AccountTypeRepository)
    repository_mock.get_account_type_by_name.return_value = \
        {'name': 'saving', 'label': 'Saving Account', 'transaction_types': [], 'position_types': [], 'date_types': [],
         'rate_types': {}, 'triggered_transactions': [], 'schedule_types': [], 'property_types': [],
         'scheduled_transactions': [], 'instalment_type': None}
    with app.container.account_type_repository.override(repository_mock):
        response = client.get("/accounttypes/saving")

    assert response.status_code == 200
    data = response.json()
    assert data == {'name': 'saving', 'label': 'Saving Account', 'transaction_types': [], 'position_types': [],
                    'date_types': [], 'rate_types': {}, 'triggered_transactions': [], 'schedule_types': [],
                    'property_types': [], 'scheduled_transactions': [], 'instalment_type': None}
    repository_mock.get_account_type_by_name.assert_called_once_with("saving")


def test_get_account_type_by_id_404(client):
    repository_mock = mock.Mock(spec=AccountTypeRepository)
    repository_mock.get_account_type_by_name.side_effect = NotFoundError("loan")

    with app.container.account_type_repository.override(repository_mock):
        response = client.get("/accounttypes/loan")

    assert response.status_code == 404


def test_add_account_type(client):
    repository_mock = mock.Mock(spec=AccountTypeRepository)

    repository_mock.create_account_type.return_value = None

    with app.container.account_type_repository.override(repository_mock):
        response = client.post("/accounttypes", json={'name': 'saving', 'label': 'Saving Account'})

    assert response.status_code == 201

    repository_mock.create_account_type.assert_called_once_with(AccountType(name="saving", label="Saving Account"))


def test_delete_account_type(client):
    repository_mock = mock.Mock(spec=AccountTypeRepository)

    with app.container.account_type_repository.override(repository_mock):
        response = client.delete("/accounttypes/saving")

    assert response.status_code == 204
    repository_mock.delete_account_type.delete_account_type('saving')


def test_delete_account_type_404(client):
    repository_mock = mock.Mock(spec=AccountTypeRepository)
    repository_mock.delete_account_type.side_effect = NotFoundError('loan')

    with app.container.account_type_repository.override(repository_mock):
        response = client.delete("/accounttypes/loan")

    assert response.status_code == 404


def test_create_account(client):
    account_repository_mock = mock.Mock(spec=AccountRepository)
    account_repository_mock.create_account.return_value = None
    account_type_repository_mock = mock.Mock(spec=AccountTypeRepository)
    account_type_repository_mock.get_account_type_by_name.return_value = create_loan_account_type()

    with app.container.account_repository.override(account_repository_mock), \
            app.container.account_type_repository.override(account_type_repository_mock):
        request = {
            "start_date": "2013-03-08",
            "account_type_name": "Loan",
            "properties": {
                "advance": 624000,
                "payment": 0
            },
            "dates": {
                "accrual_start": "2013-03-08",
                "end_date": "2038-03-08"
            }
        }

        response = client.post("/accounts", json=request)

    assert response.status_code == 201

    account_repository_mock.create_account.assert_called_once()


def test_create_account_in_memory(client):
    repository = app.container.account_type_repository()

    repository.create_account_type(create_loan_account_type())

    request = {
        "start_date": "2013-03-08",
        "account_type_name": "Loan",
        "properties": {
            "advance": 624000,
            "payment": 0
        },
        "dates": {
            "accrual_start": "2013-03-08",
            "end_date": "2038-03-08"
        }
    }

    response = client.post("/accounts", json=request)

    assert response.status_code == 201


def create_loan():
    account = Account(account_type_name="Loan", start_date=date(2013, 3, 8))
    account.properties = {
        "advance": 624000,
        "payment": 0}
    account.dates = {
        "accrual_start": "2013-03-08",
        "end_date": "2038-03-08"}

    return account


def test_status(client):
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert data == {"status": "OK"}


def create_loan_account_type() -> AccountType:
    loan_given = AccountType(name="Loan", label="Loan")

    conversion_interest_position = loan_given.add_position_type("conversion_interest", "Conversion Interest")
    early_redemption_fee_position = loan_given.add_position_type("early_redemption_fee", "Early Redemption Fee")
    interest_accrued_position = loan_given.add_position_type("accrued", "Interest Accrued")
    interest_capitalized_position = loan_given.add_position_type("interest_capitalized", "Interest Capitalized")
    principal_position = loan_given.add_position_type("principal", "Principal")

    loan_given.add_date_type(name="accrual_start", label="Accrual Start Date")
    loan_given.add_date_type(name="end_date", label="End Date")

    accrual_schedule = ScheduleType(name="accrual", label="Accrual Schedule", frequency=ScheduleFrequency.DAILY,
                                    end_type=ScheduleEndType.NO_END,
                                    business_day_adjustment=BusinessDayAdjustment.NO_ADJUSTMENT,
                                    interval_expression="1", start_date_expression="account.start_date")

    interest_schedule = ScheduleType(name="interest", label="Interest Schedule", frequency=ScheduleFrequency.MONTHLY,
                                     end_type=ScheduleEndType.NO_END,
                                     business_day_adjustment=BusinessDayAdjustment.NO_ADJUSTMENT,
                                     interval_expression="1", start_date_expression="account.start_date",
                                     end_date_expression="account.end_date",
                                     include_dates_expression="account.end_date")

    redemption_schedule = ScheduleType(name="redemption", label="Redemption Schedule",
                                       frequency=ScheduleFrequency.MONTHLY,
                                       end_type=ScheduleEndType.NO_END,
                                       business_day_adjustment=BusinessDayAdjustment.NO_ADJUSTMENT,
                                       interval_expression="1",
                                       start_date_expression="account.start_date + relativedelta(months=+1)",
                                       end_date_expression="account.end_date",
                                       include_dates_expression="account.end_date")

    advance_schedule = ScheduleType(name="advance", label="Advance Schedule",
                                    frequency=ScheduleFrequency.DAILY,
                                    end_type=ScheduleEndType.END_DATE,
                                    business_day_adjustment=BusinessDayAdjustment.NO_ADJUSTMENT,
                                    interval_expression="1",
                                    start_date_expression="account.start_date",
                                    end_date_expression="account.start_date")

    loan_given.add_schedule_type(accrual_schedule)
    loan_given.add_schedule_type(interest_schedule)
    loan_given.add_schedule_type(redemption_schedule)
    loan_given.add_schedule_type(advance_schedule)

    interest_accrued = loan_given.add_transaction_type("interestAccrued", "Interest Accrued", True) \
        .add_position_rule(TransactionOperation.CREDIT, interest_accrued_position)

    interest_capitalized = loan_given.add_transaction_type("interestCapitalized", "Interest Capitalized") \
        .add_position_rule(TransactionOperation.CREDIT, interest_capitalized_position) \
        .add_position_rule(TransactionOperation.DEBIT, interest_accrued_position) \
        .add_position_rule(TransactionOperation.CREDIT, principal_position)

    early_redemption_fee = loan_given.add_transaction_type("earlyRedemptionFee", "Early Redemption Fee") \
        .add_position_rule(TransactionOperation.CREDIT, early_redemption_fee_position)

    conversion_interest = loan_given.add_transaction_type("conversionInterest", "Conversion Interest") \
        .add_position_rule(TransactionOperation.CREDIT, conversion_interest_position)

    redemption = loan_given.add_transaction_type("redemption", "Redemption") \
        .add_position_rule(TransactionOperation.DEBIT, principal_position)

    advance_transaction = loan_given.add_transaction_type("advance", "Advance") \
        .add_position_rule(TransactionOperation.CREDIT, principal_position)

    additional_advance_transaction = loan_given.add_transaction_type("additionalAdvance", "Additional Advance") \
        .add_position_rule(TransactionOperation.CREDIT, principal_position)

    interest_payment_transaction = loan_given.add_transaction_type("interestPayment", "Interest Payment") \
        .add_position_rule(TransactionOperation.DEBIT, interest_accrued_position)

    loan_given.add_scheduled_transaction(accrual_schedule, ScheduledTransactionTiming.END_OF_DAY,
                                         interest_accrued,
                                         "account.principal * accountType.interest.get_rate(value_date, "
                                         "account.principal) / Decimal(365)")

    loan_given.add_scheduled_transaction(interest_schedule, ScheduledTransactionTiming.END_OF_DAY,
                                         interest_capitalized,
                                         "account.accrued")

    loan_given.add_scheduled_transaction(advance_schedule, ScheduledTransactionTiming.START_OF_DAY,
                                         advance_transaction,
                                         "account.advance")

    loan_given.add_instalment_type(name="payments", label="Payments", timing=ScheduledTransactionTiming.START_OF_DAY,
                                   transaction_type=redemption.name,
                                   property_name="payment",
                                   solve_for_zero_position="principal",
                                   solve_for_date="end_date",
                                   schedule_name=redemption_schedule.name)

    loan_given.add_property_type("advance", "Advance Amount", DataType.DECIMAL, True)
    loan_given.add_property_type("payment", "Payment Amount", DataType.DECIMAL, True)

    interest_rate = loan_given.add_rate_type("interest", "Interest Rate")

    interest_rate.add_tier(date(2000, 1, 1), Decimal(2000000), Decimal(0.0304))
    interest_rate.add_tier(date(2000, 1, 1), Decimal(10000000), Decimal(0.025))
    interest_rate.add_tier(date(2000, 1, 1), Decimal(1E30), Decimal(0.02))

    return loan_given
