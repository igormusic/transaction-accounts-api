"""Tests module."""

from unittest import mock

import pytest
from accounts.metadata import AccountType
from fastapi.testclient import TestClient

from .repositories import NotFoundError, AccountTypeRepository
from .application import app


@pytest.fixture
def client():
    yield TestClient(app)


def test_get_list(client):
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


def test_get_by_id(client):
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


def test_get_by_id_404(client):
    repository_mock = mock.Mock(spec=AccountTypeRepository)
    repository_mock.get_account_type_by_name.side_effect = NotFoundError("loan")

    with app.container.account_type_repository.override(repository_mock):
        response = client.get("/accounttypes/loan")

    assert response.status_code == 404


def test_add(client):
    repository_mock = mock.Mock(spec=AccountTypeRepository)

    repository_mock.create_account_type.return_value = None

    with app.container.account_type_repository.override(repository_mock):
        response = client.post("/accounttypes", json={'name': 'saving', 'label': 'Saving Account'})

    assert response.status_code == 201

    repository_mock.create_account_type.assert_called_once_with(AccountType(name="saving", label="Saving Account"))


def test_remove(client):
    repository_mock = mock.Mock(spec=AccountTypeRepository)

    with app.container.account_type_repository.override(repository_mock):
        response = client.delete("/accounttypes/saving")

    assert response.status_code == 204
    repository_mock.delete_account_type.delete_account_type('saving')


def test_remove_404(client):
    repository_mock = mock.Mock(spec=AccountTypeRepository)
    repository_mock.delete_account_type.side_effect = NotFoundError('loan')

    with app.container.account_type_repository.override(repository_mock):
        response = client.delete("/accounttypes/loan")

    assert response.status_code == 404


def test_status(client):
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert data == {"status": "OK"}
