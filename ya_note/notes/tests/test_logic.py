from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class LogicTest(TestCase):
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
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }

    def test_user_can_create_note(self):
        url = reverse('notes:add')
        note_count_at_start = Note.objects.count()
        response = self.client_author.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), note_count_at_start + 1)
        new_note = Note.objects.latest('id')
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        url = reverse('notes:add')
        note_count_at_start = Note.objects.count()
        response = self.client.post(url, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), note_count_at_start)

    def test_not_unique_slug(self):
        url = reverse('notes:add')
        self.form_data['slug'] = self.note.slug
        note_count_at_start = Note.objects.count()
        response = self.client_author.post(url, data=self.form_data)
        self.assertFormError(response, 'form', 'slug',
                             errors=(self.note.slug + WARNING))
        self.assertEqual(Note.objects.count(), note_count_at_start)

    def test_empty_slug(self):
        url = reverse('notes:add')
        self.form_data.pop('slug')
        note_count_at_start = Note.objects.count()
        response = self.client_author.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), note_count_at_start + 1)
        new_note = Note.objects.latest('id')
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        url = reverse('notes:edit', args=(self.note.slug,))
        note_at_start = self.note
        response = self.client_author.post(url, self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.author, note_at_start.author)
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_other_user_cant_edit_note(self):
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client_reader.post(url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.author, note_from_db.author)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.client_author.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        deleted = False
        try:
            Note.objects.get(id=self.note.id)
        except Note.DoesNotExist:
            deleted = True
        self.assertTrue(deleted)

    def test_other_user_cant_delete_note(self):
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.client_reader.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        deleted = False
        try:
            Note.objects.get(id=self.note.id)
        except Note.DoesNotExist:
            deleted = True
        self.assertFalse(deleted)
