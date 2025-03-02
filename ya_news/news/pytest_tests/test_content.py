import pytest

from django.urls import reverse
from django.conf import settings

@pytest.mark.django_db
def test_right_count_news_on_home_page(client, create_news):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE

@pytest.mark.django_db
def test_sort_news(client):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_news = [new.date for new in object_list]
    expected_list = sorted(all_news, reverse=True)
    assert all_news == expected_list

@pytest.mark.django_db
def test_sort_comments(client, create_comments, new):
    url = reverse('news:detail', args=(new.id, ))
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comment = news.comment_set.all()
    all_timestap = [comment.created for comment in all_comment]
    sort_comments = sorted(all_timestap)
    assert all_timestap == sort_comments

@pytest.mark.django_db
def test_form_for_anonymous_user(client, new):
    url = reverse('news:detail', args=(new.id,))
    response = client.get(url)
    assert 'form' not in response.context

def test_form_for_auth_user(author_client, new):
    url = reverse('news:detail', args=(new.id,))
    response = author_client.get(url)
    assert 'form' in response.context