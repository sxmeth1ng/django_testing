from datetime import datetime, timedelta

import pytest
from django.test.client import Client
from django.conf import settings

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    return News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        news=news,
        text='Текст комментария',
        author=author,
    )


@pytest.fixture
def create_news():
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def create_comments(news, author):
    today = datetime.today()
    all_comments = [
        Comment(
            news=news,
            text=f'Просто {index}',
            created=today - timedelta(days=index),
            author=author
        )
        for index in range(10)
    ]
    Comment.objects.bulk_create(all_comments)


@pytest.fixture
def form_data():
    return {'text': 'Новый текст'}
