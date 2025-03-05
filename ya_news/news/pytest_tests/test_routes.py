from http import HTTPStatus
import pytest

from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'url',
    (
        pytest.lazy_fixture('login_url'),
        pytest.lazy_fixture('logout_url'),
        pytest.lazy_fixture('signup_url'),
        pytest.lazy_fixture('home_url'),
        pytest.lazy_fixture('detail_url')
    ),
)
@pytest.mark.django_db
def test_pages_availability_for_anonymous_user(client, url):
    """Тест для анонимного пользователя.

    Проверка, что анонимный пользователь может
    просматривать ряд страниц.
    """
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url',
    (
        pytest.lazy_fixture('edit_url'),
        pytest.lazy_fixture('delete_url')
    ),
)
def test_comment_availability_for_author(author_client, url):
    """Тест для автора комментария.

    Проверка, что страницы удаления и редактирования
    комментария доступны автора комментария.
    """
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url',
    (
        pytest.lazy_fixture('edit_url'),
        pytest.lazy_fixture('delete_url')
    ),
)
def test_comment_not_availability_for_anonymous_user(
    client, url, login_url
):
    """Тест для анонимного пользователя.

    Проверка, что при попытке перейти на страницу
    удаления или редактирования комментария, анонимного
    пользователя переводит на страницу авторизации.
    """
    response = client.get(url)
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    'url',
    (
        pytest.lazy_fixture('edit_url'),
        pytest.lazy_fixture('delete_url')
    ),
)
def test_comment_availability_for_not_author(
    not_author_client, url
):
    """Тест для читателя.

    Проверка, что при попытке зайти на страницу редактирования
    или удаления чужого комментария, выдаёт ошибку 404.
    """
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
