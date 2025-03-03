from pytils.translit import slugify
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestLogic(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=cls.author
        )
        cls.form_data = {
            'title': 'Тайтл',
            'text': 'Текст',
            'slug': 'slag'
        }

    def test_create_note(self):
        url = reverse('notes:add')
        self.client.post(url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        self.client.force_login(self.author)
        self.client.post(url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 2)

    def test_cant_create_note_with_identical_slug(self):
        url = reverse('notes:add')
        self.form_data['slug'] = 'slug'
        self.client.force_login(self.author)
        self.client.post(url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_dont_filed_slug(self):
        self.form_data.pop('slug')
        self.form_data['title'] = 'Test'
        url = reverse('notes:add')
        self.client.force_login(self.author)
        self.client.post(url, data=self.form_data)
        self.assertEqual(Note.objects.count(), 2)
        new_note = Note.objects.get(title='Test')
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        url = reverse('notes:edit', args=(self.note.slug,))
        self.client.force_login(self.author)
        self.client.post(url, data=self.form_data)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Тайтл')

    def test_other_user_cant_edit_note(self):
        url = reverse('notes:edit', args=(self.note.slug,))
        self.client.force_login(self.reader)
        self.client.post(url, data=self.form_data)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Заголовок')

    def test_author_can_delete_note(self):
        url = reverse('notes:delete', args=(self.note.slug,))
        self.client.force_login(self.author)
        self.client.post(url)
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        url = reverse('notes:delete', args=(self.note.slug,))
        self.client.force_login(self.reader)
        self.client.post(url)
        self.assertEqual(Note.objects.count(), 1)
