from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestContent(TestCase):
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

    def test_notes_list_for_different_users(self):
        users = (
            (self.client_author, self.assertIn),
            (self.client_reader, self.assertNotIn),
        )

        for client, method in users:
            with self.subTest():
                url = reverse('notes:list')
                response = client.get(url)
                object_list = response.context['object_list']
                method(self.note, object_list)

    def test_pages_contains_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )

        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client_author.get(url)
                self.assertIsInstance(response['form'], NoteForm)
