from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from http import HTTPStatus

import shutil
import tempfile

from posts.models import Post, Group, Comment
from posts.forms import PostForm

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class FormsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовый заголовок группы',
            slug='test-slug',
            description='Описание группы',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            author=cls.user,
            group=cls.group,
        )
        cls.form = PostForm()
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Коментарий поста'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.guest_client = Client()

    def test_form_post_create(self):
        """Проверка создания поста."""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': self.post.text,
            'group': self.post.pk,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:create_post'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        last_post = Post.objects.first()
        self.assertEqual(last_post.text, self.post.text)
        self.assertEqual(last_post.author, self.post.author)
        self.assertEqual(last_post.group, self.post.group)

    def test_form_post_edit(self):
        """Проверка редактирования поста."""
        form_data = {
            'text': 'Редактированный текст поста',
            'group': self.post.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        post = Post.objects.get(pk=self.post.pk)
        self.assertEqual(post.text, form_data['text'])
        last_post = Post.objects.first()
        self.assertEqual(last_post.text, form_data['text'])
        self.assertEqual(last_post.author, self.post.author)
        self.assertEqual(last_post.group, self.post.group)

    def test_form_guest_client_create_post(self):
        """Проверка что неавторизованный пользователь не может создать
         пост и редирект его на страницу авторизации."""
        posts_count = Post.objects.count()
        response = self.guest_client.post(reverse('posts:create_post'))
        self.assertRedirects(response, reverse('users:login') + '?next='
                             + reverse('posts:create_post'),
                             status_code=302, target_status_code=200)
        self.assertEqual(Post.objects.count(), posts_count)

    def test_form_authorized_client_create_comment(self):
        """Проверка создания комментария авторизованным пользователем."""
        comment_count = Comment.objects.count()
        form_data = {
            'text': self.comment.text,
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        last_comment = Comment.objects.first()
        self.assertEqual(last_comment.post, self.comment.post)
        self.assertEqual(last_comment.author, self.comment.author)
        self.assertEqual(last_comment.text, self.comment.text)

    def test_form_guest_client_create_comment(self):
        """Проверка что неавторизованный пользователь не может создать
         комментарий и редирект его на страницу авторизации."""
        comment_count = Comment.objects.count()
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
        )
        self.assertRedirects(response, reverse('users:login') + '?next='
                             + reverse('posts:add_comment',
                             kwargs={'post_id': self.post.pk}),
                             status_code=302, target_status_code=200)

        self.assertEqual(Comment.objects.count(), comment_count)
