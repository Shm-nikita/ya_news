from datetime import datetime, timedelta
import pytest
from django.test.client import Client
from django.conf import settings
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username="Автор")


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username="Не автор")


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
def news(author):
    news = News.objects.create(
        title="Заголовок",
        text="Текст новости",
    )
    return news


@pytest.fixture
def pk_for_args(news):
    return (news.id,)


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(news=news, author=author,
                                     text="Текст комментария")
    return comment


@pytest.fixture
def pk_for_args_comment(comment):
    return (comment.id,)


@pytest.fixture
def page_of_news(author):
    today = datetime.today()
    page_of_news = News.objects.bulk_create(
        News(
            title=f"Новость {index}",
            text="Просто текст.",
            date=today - timedelta(days=index),
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )
    return page_of_news


@pytest.fixture
def multi_comments(author, news):
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f"Tекст {index}",
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    return multi_comments


@pytest.fixture
def form_data(author, news):
    return {"text": "Измененный текст", }
