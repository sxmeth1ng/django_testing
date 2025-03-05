from http import HTTPStatus
import pytest

from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'name',
    (
        pytest.lazy_fixture('login_url'),
        pytest.lazy_fixture('logout_url'),
        pytest.lazy_fixture('signup_url'),
        pytest.lazy_fixture('home_url'),
        pytest.lazy_fixture('detail_url')
    ),
)
@pytest.mark.django_db
def test_pages_availability_for_anonymous_user(client, name):
    response = client.get(name)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    (
        pytest.lazy_fixture('edit_url'),
        pytest.lazy_fixture('delete_url')
    ),
)
def test_comment_availability_for_author(author_client, name):
    response = author_client.get(name)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    (
        pytest.lazy_fixture('edit_url'),
        pytest.lazy_fixture('delete_url')
    ),
)
def test_comment_not_availability_for_anonymous_user(
    client, name, login_url
):
    response = client.get(name)
    expected_url = f'{login_url}?next={name}'
    assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    'name',
    (
        pytest.lazy_fixture('edit_url'),
        pytest.lazy_fixture('delete_url')
    ),
)
def test_comment_availability_for_not_author(
    not_author_client, name
):
    response = not_author_client.get(name)
    assert response.status_code == HTTPStatus.NOT_FOUND
