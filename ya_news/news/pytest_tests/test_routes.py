from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'name, model, parametrized_client, expected_status',
    (
        ('news:home', None, pytest.lazy_fixture('client'), HTTPStatus.OK),
        ('news:detail', pytest.lazy_fixture('news'),
         pytest.lazy_fixture('client'), HTTPStatus.OK),
        ('users:login', None, pytest.lazy_fixture('client'), HTTPStatus.OK),
        ('users:logout', None, pytest.lazy_fixture('client'), HTTPStatus.OK),
        ('users:signup', None, pytest.lazy_fixture('client'), HTTPStatus.OK),
        ('news:edit', pytest.lazy_fixture('comment'),
         pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        ('news:edit', pytest.lazy_fixture('comment'),
         pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        ('news:delete', pytest.lazy_fixture('comment'),
         pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        ('news:delete', pytest.lazy_fixture('comment'),
         pytest.lazy_fixture('author_client'), HTTPStatus.OK),
    )
)
@pytest.mark.django_db
def test_pages_availability(
        name, model, parametrized_client, expected_status):
    if model is not None:
        url = reverse(name, args=(model.id,))
    else:
        url = reverse(name)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_redirect_for_anonymouse_client(name, comment, client):
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.id,))
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, redirect_url)
