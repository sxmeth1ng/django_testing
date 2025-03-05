from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

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
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.signup_url = reverse('users:signup')
        cls.login_url = reverse('users:login')
        cls.logout_url = reverse('users:logout')
        cls.home_url = reverse('notes:home')
        cls.succes_url = reverse('notes:success')

    def test_pages_availability(self):
        urls = (
            self.list_url,
            self.succes_url,
            self.add_url,
            self.signup_url,
            self.login_url,
            self.logout_url
        )
        for name in urls:
            with self.subTest(name=name):
                response = self.author_client.get(name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_author(self):
        users_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            for name in (self.edit_url, self.delete_url):
                with self.subTest(user=user, name=name):
                    response = user.get(name)
                    self.assertEqual(response.status_code, status)

    def test_pages_for_anonymous_client(self):
        urls = (
            self.list_url,
            self.succes_url,
            self.edit_url,
            self.delete_url,
            self.add_url,
            self.home_url
        )
        for name in urls:
            with self.subTest(name=name):
                if name == self.home_url:
                    response = self.client.get(name)
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                else:
                    redirect_url = f'{self.login_url}?next={name}'
                    response = self.client.get(name)
                    self.assertRedirects(response, redirect_url)
