import pytest

from django.conf import settings

from news.forms import CommentForm


@pytest.mark.django_db
def test_right_count_news_on_home_page(client, create_news, home_url):
    response = client.get(home_url)
    assert 'object_list' in response.context
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_sort_news(client, home_url):
    response = client.get(home_url)
    assert 'object_list' in response.context
    object_list = response.context['object_list']
    all_news = [new.date for new in object_list]
    expected_list = sorted(all_news, reverse=True)
    assert all_news == expected_list


@pytest.mark.django_db
def test_sort_comments(client, create_comments, detail_url):
    response = client.get(detail_url)
    assert 'news' in response.context
    new = response.context['news']
    all_comment = new.comment_set.all()
    all_timestap = [comment.created for comment in all_comment]
    sort_comments = sorted(all_timestap)
    assert all_timestap == sort_comments


@pytest.mark.django_db
def test_form_for_anonymous_user(client, detail_url):
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_form_for_auth_user(author_client, detail_url):
    response = author_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm) is True
