from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from http import HTTPStatus

from posts.models import Group, Post, Comment, Follow

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.user_unfollow = User.objects.create_user(
            username='test_user_unfollow')
        cls.post = Post.objects.create(
            text='Текст',
            author=cls.user,
        )
        cls.group = Group.objects.create(
            title='Тестовй заголовок',
            slug='test-slug',
            description='Описание группы',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Коментарий поста'
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.user_unfollow,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_unfollow = Client()
        self.authorized_client_unfollow.force_login(self.user_unfollow)

    def test_urls_status_code_and_correct_template_guest_client(self):
        """Проверка доступа к странице и шаблону для
        неавторизированного пользователя."""
        templates_url_name = {
            'posts/index.html': '/',
            'posts/group_list.html': f'/group/{self.group.slug}/',
            'posts/profile.html': f'/profile/{self.user.username}/',
            'posts/post_detail.html': f'/posts/{self.post.pk}/',
        }
        for template, address in templates_url_name.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_urls_status_code_and_correct_template_authorized_client(self):
        """Проверка доступа к странице и шаблону для авторизированного пользователя
        и редиректа неавторизированного пользователя."""
        templates_url_name = {
            '/follow/': 'posts/follow.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
        }
        for address, template in templates_url_name.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, 302)

    def test_urls_status_code_guest_client_404(self):
        """Проверка доступа неавторизированного пользователя
        к несуществующей странице."""
        response = self.guest_client.get('core: 404')
        self.assertEqual(response.status_code, 404)
        response = self.guest_client.get('/core/')
        self.assertTemplateUsed(response, 'core/404.html')

    def test_urls_status_code_auturized_client_comment(self):
        """Проверка доступа авторизированного пользователя
        к comment."""
        response = self.authorized_client.get(
            f'/posts/{self.post.pk}/comment/'
        )
        self.assertEqual(response.status_code, 302)

    def test_urls_status_code_authorized_client_comment_follow(self):
        """Проверка доступа авторизированного пользователя к follow"""
        response = self.authorized_client.get('/follow/')
        self.assertEqual(response.status_code, 200)

    def test_urls_status_code_authorized_client_comment_profile_follow(self):
        """Проверка доступа авторизированного пользователя к profile_follow"""
        response = self.authorized_client_unfollow.get(
            f'/profile/{self.user.username}/follow/'
        )
        self.assertEqual(response.status_code, 302)

    def test_urls_status_code_authorized_client_comment_profile_unfollow(self):
        """Проверка доступа авторизированного пользователя
        к profile_unfollow"""
        response = self.authorized_client.get(
            f'/profile/{self.user_unfollow.username}/unfollow/'
        )
        self.assertEqual(response.status_code, 302)
