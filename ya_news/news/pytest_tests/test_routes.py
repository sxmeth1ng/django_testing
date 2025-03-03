# test_routes.py
from http import HTTPStatus
import pytest

from pytest_django.asserts import assertRedirects
from django.urls import reverse


@pytest.mark.django_db
def test_home_availability_for_anonymous_user(client):
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_news_availability_for_anonymous_user(client, new):
    url = reverse('news:detail', args=(new.id,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('news:delete', 'news:edit'),
)
def test_comment_availability_for_author(author_client, name, id_for_args):
    url = reverse(name, args=(id_for_args))
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('news:delete', 'news:edit'),
)
def test_comment_not_availability_for_anonymous_user(
    client, name, id_for_args
):
    url = reverse(name, args=id_for_args)
    response = client.get(url)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    'name',
    ('news:delete', 'news:edit'),
)
def test_comment_availability_for_not_author(
    not_author_client, name, id_for_args
):
    url = reverse(name, args=(id_for_args))
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    'name',
    ('users:login', 'users:logout', 'users:signup'),
)
@pytest.mark.django_db
def test_users_pages_availability_to_anonymous_user(client, name):
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
