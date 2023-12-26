import pytest
from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm

HOME_URL = reverse('news:home')


@pytest.mark.usefixtures('list_news')
@pytest.mark.django_db
def test_news_count(client):
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client):
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
@pytest.mark.usefixtures('comments')
def test_comments_order(detail_url, client):
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_dates = [comment.created for comment in all_comments]
    sorted_dates = sorted(all_dates)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_anonymouse_client_has_no_form(client, detail_url):
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_authorized_client_has_form(admin_client, detail_url):
    response = admin_client.get(detail_url)
    assert 'form' in response.context
    form = response.context['form']
    assert isinstance(form, CommentForm)
