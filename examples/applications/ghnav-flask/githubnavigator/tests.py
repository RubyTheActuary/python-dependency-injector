"""Tests module."""

from unittest import mock

import pytest
from github import Github
from flask import url_for

from .application import Application


@pytest.fixture
def application():
    application = Application()
    application.config.from_dict(
        {
            'github': {
                'auth_token': 'test-token',
                'request_timeout': 10,
            },
            'search': {
                'default_term': 'Dependency Injector',
                'default_limit': 5,
            },
        }
    )
    return application


@pytest.fixture()
def app(application: Application):
    return application.app()


def test_index(client, application: Application):
    github_client_mock = mock.Mock(spec=Github)
    github_client_mock.search_repositories.return_value = [
        mock.Mock(
            html_url='repo1-url',
            name='repo1-name',
            owner=mock.Mock(
                login='owner1-login',
                html_url='owner1-url',
                avatar_url='owner1-avatar-url',
            ),
            created_at='repo1-created-at',
            get_commits=mock.Mock(return_value=[mock.Mock()]),
        ),
        mock.Mock(
            html_url='repo2-url',
            name='repo2-name',
            owner=mock.Mock(
                login='owner2-login',
                html_url='owner2-url',
                avatar_url='owner2-avatar-url',
            ),
            created_at='repo2-created-at',
            get_commits=mock.Mock(return_value=[mock.Mock()]),
        ),
    ]

    with application.github_client.override(github_client_mock):
        response = client.get(url_for('index'))

    assert response.status_code == 200

    assert b'repo1-url' in response.data
    assert b'repo1-name' in response.data
    assert b'owner1-login' in response.data
    assert b'owner1-url' in response.data
    assert b'owner1-avatar-url' in response.data
    assert b'repo1-created-at' in response.data

    assert b'repo2-url' in response.data
    assert b'repo2-name' in response.data
    assert b'owner2-login' in response.data
    assert b'owner2-url' in response.data
    assert b'owner2-avatar-url' in response.data
    assert b'repo2-created-at' in response.data


def test_index_no_results(client, application: Application):
    github_client_mock = mock.Mock(spec=Github)
    github_client_mock.search_repositories.return_value = []

    with application.github_client.override(github_client_mock):
        response = client.get(url_for('index'))

    assert response.status_code == 200
    assert b'No search results' in response.data