import pytest

from http import HTTPStatus
from django.urls import reverse

from news.models import Comment
from news.forms import BAD_WORDS


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, new):
    url = reverse('news:detail', args=(new.id,))
    client.post(url, data=form_data)
    count_comments = Comment.objects.count()
    assert count_comments == 0


def test_auth_user_create_comment(author_client, new, form_data):
    url = reverse('news:detail', args=(new.id, ))
    author_client.post(url, data=form_data)
    count_comments = Comment.objects.count()
    assert count_comments == 1


def test_user_cant_use_bad_words(author_client, new):
    url = reverse('news:detail', args=(new.id, ))
    response = author_client.post(url, data={'text': BAD_WORDS[0]})
    assert 'form' in response.context
    count_comments = Comment.objects.count()
    assert count_comments == 0


def test_author_can_delete_comment(
    author_client, id_for_args
):
    assert Comment.objects.count() == 1
    url = reverse('news:delete', args=id_for_args)
    author_client.delete(url)
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(
    author_client, id_for_args, comments
):
    url = reverse('news:edit', args=id_for_args)
    author_client.post(url, data={'text': 'Новый текст'})
    comments.refresh_from_db()
    assert comments.text == 'Новый текст'


def test_not_author_cant_delete_comment(
    not_author_client, id_for_args
):
    url = reverse('news:delete', args=id_for_args)
    response = not_author_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_not_author_cant_edit_comment(
    not_author_client, id_for_args, comments
):
    url = reverse('news:edit', args=id_for_args)
    response = not_author_client.post(url, data={'text': 'Новый текст'})
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comments.text == 'Текст комментария'
