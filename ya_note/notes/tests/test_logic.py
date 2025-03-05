from pytils.translit import slugify
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class TestLogic(TestCase):
    """Тест-кейс проверяющий основную логику приложения."""

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
        cls.form_data = {
            'title': 'Тайтл',
            'text': 'Новый текст',
            'slug': 'slag'
        }
        cls.list_url = reverse('notes:list')
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

    def test_create_anonymous_note(self):
        """Тест для анонимного пользователяю.

        Проверка, что анонимный пользователь не может создать заметку.
        """
        self.client.post(self.add_url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_create_note(self):
        """Тест для залогиненного пользователя.

        Проверка, что авторизованный пользователь может создать заметку.
        """
        self.author_client.post(self.add_url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 2)
        note = Note.objects.get(pk=2)
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.title, self.form_data['title'])

    def test_cant_create_note_with_identical_slug(self):
        """Тест на заметку.

        Проверка, что нельзя создать заметку
        с одинаковым слагом.
        """
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(self.add_url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.note.slug + WARNING)
        )

    def test_dont_filed_slug(self):
        """Тест на создание заметки.

        Проверка, что при незаполненном слаге,
        он создаётся автоматически.
        """
        self.form_data.pop('slug')
        self.author_client.post(self.add_url, data=self.form_data)
        self.assertEqual(Note.objects.count(), 2)
        new_note = Note.objects.get(pk=2)
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        """Тест для автора заметки.

        Проверка, что автор заметки может её редактировать.
        """
        self.author_client.post(self.edit_url, data=self.form_data)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_other_user_cant_edit_note(self):
        """Тест для пользователей.

        Проверка, что авторизованный пользователь не может редактировать
        чужую заметку.
        """
        self.reader_client.post(self.edit_url, data=self.form_data)
        note = Note.objects.get()
        self.assertEqual(self.note.title, note.title)

    def test_author_can_delete_note(self):
        """Тест для автора заметки.

        Проверка, что автор заметки может её удалить.
        """
        self.author_client.post(self.delete_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        """Тест для пользователей.

        Проверка, что авторизованный пользователь, не может
        удалить чужую заметку.
        """
        self.reader_client.post(self.delete_url)
        self.assertEqual(Note.objects.count(), 1)
