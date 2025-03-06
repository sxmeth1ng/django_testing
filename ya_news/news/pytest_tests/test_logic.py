import pytest

from http import HTTPStatus
from pytest_django.asserts import assertFormError

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, detail_url):
    """Тест для анонимного пользователя.

    Проверка, что если отправить форму на комментарий
    он не создаться.
    """
    client.post(detail_url, data=form_data)
    count_comments = Comment.objects.count()
    assert count_comments == 0


def test_auth_user_create_comment(
    author_client, form_data, detail_url, author, news
):
    """Тест для авторизированного пользователя.

    Проверка, что авторизированный пользователь может
    создать комментарий.
    """
    author_client.post(detail_url, data=form_data)
    count_comments = Comment.objects.count()
    assert count_comments == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.author == author
    assert comment.news == news


@pytest.mark.parametrize(
    'bad_word',
    BAD_WORDS
)
def test_user_cant_use_bad_words(author_client, detail_url, bad_word):
    """Тест на создание комментария.

    Проверка, что при использовании запрещённый слов
    форму будет возвращать ошибку и комменатрий не создаться.
    """
    response = author_client.post(detail_url, data={'text': bad_word})
    assertFormError(response, 'form', 'text', errors=(WARNING))
    count_comments = Comment.objects.count()
    assert count_comments == 0


def test_author_can_delete_comment(
    author_client, delete_url
):
    """Тест удаление комментария.

    Проверка, что автор комментария может удалить его.
    """
    author_client.delete(delete_url)
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(
    author_client, comment, form_data, author, edit_url, news
):
    """Тест редактирования комментария.

    Проверка, что автор комментария может его изменять.
    """
    author_client.post(edit_url, data=form_data)
    comment.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.author == author
    assert comment.news == news


def test_not_author_cant_delete_comment(
    not_author_client, delete_url
):
    """Тест удаление комментария.

    Проврека, что читатель комментария, не может его удалить.
    """
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_not_author_cant_edit_comment(
    not_author_client, comment, form_data, edit_url
):
    """Тест редактирования комментария.

    Проверка, что читатель комментария,
    не сможет его отредактировать.
    """
    response = not_author_client.post(edit_url, data=form_data)
    expected_comment = Comment.objects.get(pk=comment.pk)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comment.text == expected_comment.text
    assert comment.author == expected_comment.author
    assert comment.news == expected_comment.news
