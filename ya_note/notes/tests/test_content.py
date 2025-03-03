from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

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

    def test_note_in_note_list(self):
        url = reverse('notes:list')
        self.client.force_login(self.author)
        response = self.client.get(url)
        count_notes = Note.objects.count()
        self.assertEqual(count_notes, 1)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_note_not_in_list_other_user(self):
        url = reverse('notes:list')
        self.client.force_login(self.reader)
        response = self.client.get(url)
        count_notes = Note.objects.count()
        self.assertEqual(count_notes, 1)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)

    def test_form_in_pages(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', self.note.slug)
        )
        for name, args in urls:
            with self.subTest(name=name):
                if args is None:
                    url = reverse(name)
                else:
                    url = reverse(name, args=(args,))
                self.client.force_login(self.author)
                response = self.client.get(url)
                self.assertIn('form', response.context)
