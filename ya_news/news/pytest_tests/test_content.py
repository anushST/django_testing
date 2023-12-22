from django.conf import settings
from django.urls import reverse
import pytest


class TestHomePage:
    HOME_URL = reverse('news:home')

    @pytest.mark.usefixtures('list_news')
    @pytest.mark.django_db
    def test_news_count(self, client):
        response = client.get(self.HOME_URL)
        object_list = response.context['object_list']
        news_count = len(object_list)
        assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE

    @pytest.mark.django_db
    def test_news_order(self, client):
        response = client.get(self.HOME_URL)
        object_list = response.context['object_list']
        all_dates = [news.date for news in object_list]
        sorted_dates = sorted(all_dates, reverse=True)
        assert all_dates == sorted_dates


class TestDetailPage:
    @pytest.fixture
    def detail_url(self, news):
        return reverse('news:detail', args=(news.id,))

    @pytest.mark.django_db
    @pytest.mark.usefixtures('comments')
    def test_comments_order(self, detail_url, news, client):
        response = client.get(detail_url)
        assert 'news' in response.context
        news = response.context['news']
        all_comments = news.comment_set.all()
        assert all_comments[0].created < all_comments[1].created

    @pytest.mark.django_db
    def test_anonymouse_client_has_no_form(self, client, detail_url):
        response = client.get(detail_url)
        assert 'form' not in response.context

    def test_authorized_client_has_form(self, admin_client, detail_url):
        response = admin_client.get(detail_url)
        assert 'form' in response.context
