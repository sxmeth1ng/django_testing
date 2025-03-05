from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=cls.author
        )
        cls.list_url = reverse('notes:list')
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))

    def test_note_in_note_list(self):
        client_result = (
            (self.author_client, True),
            (self.reader_client, False)
        )
        for user, result in client_result:
            with self.subTest(user=user):
                response = user.get(self.list_url)
                count_notes = Note.objects.count()
                self.assertEqual(count_notes, 1)
                object_list = response.context['object_list']
                if result:
                    self.assertIn(self.note, object_list)
                else:
                    self.assertNotIn(self.note, object_list)
                self.assertEqual(
                    self.note if result else None,
                    object_list[0] if result else None
                )

    def test_form_in_pages(self):
        urls = (
            self.add_url,
            self.edit_url
        )
        for name in urls:
            with self.subTest(name=name):
                response = self.author_client.get(name)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
