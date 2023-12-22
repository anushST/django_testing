from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


class TestCommentCreation:
    COMMENT_TEXT = 'Текст комментария'

    @pytest.mark.django_db
    def test_anonymouse_user_can_create_comment(self, client,
                                                form_data, news_url):
        client.post(news_url, data=form_data)
        comment_count = Comment.objects.count()
        assert comment_count == 0

    def test_user_can_create_comment(
            self, author_client, news_url, form_data, news, author):
        response = author_client.post(news_url, data=form_data)
        assertRedirects(response, f'{news_url}#comments')
        comments_count = Comment.objects.count()
        assert comments_count == 1
        comment = Comment.objects.get()
        assert comment.text == self.COMMENT_TEXT
        assert comment.news == news
        assert comment.author == author

    def test_user_cant_use_bad_words(self, author_client, news_url):
        bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
        response = author_client.post(news_url, data=bad_words_data)
        assertFormError(
            response,
            form='form',
            field='text',
            errors=WARNING
        )
        comments_count = Comment.objects.count()
        assert comments_count == 0


class TestCommentEditDelete:
    COMMENT_TEXT = 'Текст комментария'
    NEW_COMMENT_TEXT = 'Обновлённый комментарий'

    @pytest.fixture
    def new_form_data(self):
        return {'text': 'Обновлённый комментарий'}

    @pytest.mark.usefixtures('comment')
    def test_author_can_delete_comment(
            self, author_client, comment_delete_url, url_to_comments):
        response = author_client.delete(comment_delete_url)
        assertRedirects(response, url_to_comments)
        comments_count = Comment.objects.count()
        assert comments_count == 0

    @pytest.mark.usefixtures('comment')
    def test_user_cant_delete_comment_of_another_user(
            self, admin_client, comment_delete_url):
        response = admin_client.delete(comment_delete_url)
        assert response.status_code == HTTPStatus.NOT_FOUND
        comments_count = Comment.objects.count()
        assert comments_count == 1

    def test_author_can_edit_comment(
            self, author_client, new_form_data, comment_edit_url,
            url_to_comments, comment):
        response = author_client.post(comment_edit_url, data=new_form_data)
        assertRedirects(response, url_to_comments)
        comment.refresh_from_db()
        assert comment.text == self.NEW_COMMENT_TEXT

    def test_user_cant_edit_comment_of_another_user(
            self, admin_client, comment, comment_edit_url, new_form_data):
        response = admin_client.post(comment_edit_url, data=new_form_data)
        assert response.status_code == HTTPStatus.NOT_FOUND
        comment.refresh_from_db()
        assert comment.text == self.COMMENT_TEXT
