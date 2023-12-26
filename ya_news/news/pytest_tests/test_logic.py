from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


COMMENT_TEXT = 'Текст комментария'
NEW_COMMENT_TEXT = 'Обновлённый комментарий'


@pytest.mark.django_db
def test_anonymouse_user_can_create_comment(client, form_data, news_url):
    comment_count_before = Comment.objects.count()
    client.post(news_url, data=form_data)
    comment_count_after = Comment.objects.count()
    assert comment_count_after == comment_count_before


def test_user_can_create_comment(
        author_client, news_url, form_data, news, author):
    comments_count_at_start = Comment.objects.count()
    response = author_client.post(news_url, data=form_data)
    assertRedirects(response, f'{news_url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == comments_count_at_start + 1
    comment = Comment.objects.latest('id')
    assert comment.text == COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news_url):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    comments_count_at_start = Comment.objects.count()
    response = author_client.post(news_url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == comments_count_at_start


@pytest.mark.usefixtures('comment')
def test_author_can_delete_comment(
        author_client, comment_delete_url, url_to_comments, comment):
    response = author_client.delete(comment_delete_url)
    assertRedirects(response, url_to_comments)
    comment_deleted = False
    try:
        Comment.objects.get(id=comment.id)
    except Comment.DoesNotExist:
        comment_deleted = True
    assert comment_deleted


@pytest.mark.usefixtures('comment')
def test_user_cant_delete_comment_of_another_user(
        admin_client, comment_delete_url, comment):
    response = admin_client.delete(comment_delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_deleted = False
    try:
        Comment.objects.get(id=comment.id)
    except Comment.DoesNotExist:
        comment_deleted = True
    assert comment_deleted is False


def test_author_can_edit_comment(
        author_client, new_form_data, comment_edit_url,
        url_to_comments, comment):
    comment_before = comment
    response = author_client.post(comment_edit_url, data=new_form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == NEW_COMMENT_TEXT
    assert comment.id == comment_before.id
    assert comment.news == comment_before.news
    assert comment.author == comment_before.author
    assert comment.created == comment_before.created


def test_user_cant_edit_comment_of_another_user(
        admin_client, comment, comment_edit_url, new_form_data):
    comment_before = comment
    response = admin_client.post(comment_edit_url, data=new_form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT
    assert comment.id == comment_before.id
    assert comment.news == comment_before.news
    assert comment.author == comment_before.author
    assert comment.created == comment_before.created
