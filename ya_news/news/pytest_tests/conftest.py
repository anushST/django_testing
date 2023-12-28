from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Messi')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture()
def news():
    return News.objects.create(
        title='Title',
        text='Text',
    )


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )


@pytest.fixture
def list_news():
    today = datetime.today()
    return News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def comments(news, author):
    now = timezone.now()
    comments = Comment.objects.bulk_create(
        Comment(
            news=news, author=author, text=f'Teкст {index}',
        )
        for index in range(2)
    )
    index = 1
    for comment in comments:
        comment.created = now + timedelta(days=index)
        comment.save()
        index += 1


@pytest.fixture
def form_data():
    return {'text': 'Текст комментария'}


@pytest.fixture
def news_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def url_to_comments(news_url):
    return news_url + '#comments'


@pytest.fixture
def comment_edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def comment_delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def new_form_data():
    return {'text': 'Обновлённый комментарий'}


@pytest.fixture
def news_home_url():
    return reverse('news:home')


@pytest.fixture
def news_detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def users_login_url():
    return reverse('users:login')


@pytest.fixture
def users_logout_url():
    return reverse('users:logout')


@pytest.fixture
def users_signup_url():
    return reverse('users:signup')


@pytest.fixture
def news_edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def news_delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def comment_text():
    return 'Текст комментария'


@pytest.fixture
def new_comment_text():
    return 'Обновлённый комментарий'
