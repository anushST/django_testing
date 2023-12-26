from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Messi')
        cls.client_author = Client()
        cls.client_author.force_login(cls.author)

        cls.reader = User.objects.create(username='Cristiano')
        cls.client_reader = Client()
        cls.client_reader.force_login(cls.reader)

        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author,
        )

    def test_pages_availability(self):
        parameters = (
            ('notes:home', None, self.client, HTTPStatus.OK),
            ('users:login', None, self.client, HTTPStatus.OK),
            ('users:logout', None, self.client, HTTPStatus.OK),
            ('users:signup', None, self.client, HTTPStatus.OK),
            ('notes:detail', (self.note.slug,),
             self.client_author, HTTPStatus.OK),
            ('notes:detail', (self.note.slug,),
             self.client_reader, HTTPStatus.NOT_FOUND),
            ('notes:edit', (self.note.slug,),
             self.client_author, HTTPStatus.OK),
            ('notes:edit', (self.note.slug,),
             self.client_reader, HTTPStatus.NOT_FOUND),
            ('notes:delete', (self.note.slug,),
             self.client_author, HTTPStatus.OK),
            ('notes:delete', (self.note.slug,),
             self.client_reader, HTTPStatus.NOT_FOUND),
        )
        for name, args, user, status_code in parameters:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = user.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_redirects(self):
        urls = (
            ('notes:detail', (self.note.id,)),
            ('notes:edit', (self.note.id,)),
            ('notes:delete', (self.note.id,)),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:list', None),
        )

        for name, args in urls:
            with self.subTest(name=name):
                login_url = reverse('users:login')
                url = reverse(name, args=args)
                expected_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, expected_url)
