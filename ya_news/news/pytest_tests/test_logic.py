import pytest

from http import HTTPStatus
from pytest_django.asserts import assertFormError

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, detail_url):
    client.post(detail_url, data=form_data)
    count_comments = Comment.objects.count()
    assert count_comments == 0


def test_auth_user_create_comment(
    author_client, form_data, detail_url, author
):
    author_client.post(detail_url, data=form_data)
    count_comments = Comment.objects.count()
    assert count_comments == 1
    comment = Comment.objects.get()
    assert comment.text == 'Новый текст'
    assert comment.author == author


@pytest.mark.parametrize(
    'bad_word',
    BAD_WORDS
)
def test_user_cant_use_bad_words(author_client, detail_url, bad_word):
    response = author_client.post(detail_url, data={'text': bad_word})
    assertFormError(response, 'form', 'text', errors=(WARNING))
    count_comments = Comment.objects.count()
    assert count_comments == 0


def test_author_can_delete_comment(
    author_client, delete_url
):
    author_client.delete(delete_url)
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(
    author_client, comment, form_data, author, edit_url
):
    author_client.post(edit_url, data=form_data)
    comment.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.author == author


def test_not_author_cant_delete_comment(
    not_author_client, comment, delete_url
):
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_not_author_cant_edit_comment(
    not_author_client, comment, form_data, edit_url
):
    response = not_author_client.post(edit_url, data=form_data)
    expected_comment = Comment.objects.get()
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comment.text == expected_comment.text
    assert comment.author == expected_comment.author
