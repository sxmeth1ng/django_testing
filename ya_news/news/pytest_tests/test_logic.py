import pytest

from http import HTTPStatus
from django.urls import reverse

from news.models import Comment
from news.forms import BAD_WORDS


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, news):
    url = reverse('news:detail', args=(news.id,))
    client.post(url, data=form_data)
    count_comments = Comment.objects.count()
    assert count_comments == 0


def test_auth_user_create_comment(author_client, news, form_data, author):
    url = reverse('news:detail', args=(news.id, ))
    author_client.post(url, data=form_data)
    count_comments = Comment.objects.count()
    assert count_comments == 1
    comment = Comment.objects.get()
    assert comment.text == 'Новый текст'
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news):
    url = reverse('news:detail', args=(news.id, ))
    response = author_client.post(url, data={'text': BAD_WORDS[0]})
    assert 'form' in response.context
    count_comments = Comment.objects.count()
    assert count_comments == 0


def test_author_can_delete_comment(
    author_client, comment
):
    url = reverse('news:delete', args=(comment.id,))
    author_client.delete(url)
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(
    author_client, comment, form_data
):
    url = reverse('news:edit', args=(comment.id,))
    author_client.post(url, data=form_data)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_not_author_cant_delete_comment(
    not_author_client, comment
):
    url = reverse('news:delete', args=(comment.id,))
    response = not_author_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_not_author_cant_edit_comment(
    not_author_client, comment, form_data
):
    url = reverse('news:edit', args=(comment.id,))
    response = not_author_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comment.text == 'Текст комментария'
