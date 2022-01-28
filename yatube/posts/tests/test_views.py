from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from django.core.cache import cache

from yatube.settings import VAR_NUMBER_POSTS

from posts.models import Post, Group, Comment, Follow


User = get_user_model()


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.user_follow = User.objects.create_user(username='test_follow')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Описание группы'
        )
        cls.group_1 = Group.objects.create(
            title='Тестовый заголовок_2',
            slug='test-slug_2',
            description='Описание группы_2'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            author=cls.user,
            group=cls.group,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Коментарий поста'
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_page_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:posts_list', kwargs={
                'slug': self.group.slug}): 'posts/group_list.html',
            reverse('posts:profile', kwargs={
                'username': self.user.username}): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={
                'post_id': self.post.pk}): 'posts/post_detail.html',
            reverse('posts:create_post'): 'posts/create_post.html',
            reverse('posts:edit', kwargs={
                'post_id': self.post.pk}): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Проверка контекста на странице index."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        posts_text_0 = first_object.text
        posts_author_0 = first_object.author
        posts_group_0 = first_object.group
        post_image_0 = first_object.image
        self.assertEqual(posts_text_0, self.post.text)
        self.assertEqual(posts_author_0, self.user)
        self.assertEqual(posts_group_0, self.post.group)
        self.assertEqual(post_image_0, self.post.image)

    def test_group_post_page_show_correct_context(self):
        """Проверка контекста на странице group_list."""
        response = self.authorized_client.get(

            reverse('posts:posts_list', kwargs={'slug': self.group.slug}))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_image_0, self.post.image)
        self.assertEqual(
            response.context['group'].title, self.group.title)
        self.assertEqual(
            response.context['group'].description, self.group.description)

    def test_profile_page_show_correct_context(self):
        """Проверка контекста на странице profile."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username}))
        number_of_posts_test = Post.objects.count()
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_image_0, self.post.image)
        self.assertEqual(response.context['author'], self.user)
        self.assertEqual(
            response.context['number_of_posts'], number_of_posts_test)

    def test_post_detail_page_show_correct_context(self):
        """Проверка контекста на странице post_detail."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        context = response.context.get('post')
        self.assertEqual(context.text, self.post.text)
        self.assertEqual(context.author, self.post.author)
        self.assertEqual(context.group, self.post.group)
        self.assertEqual(context.image, self.post.image)

    def test_page_create_post_form_correct_context_(self):
        """Провертка формы create_post."""
        response = self.authorized_client.get(reverse('posts:create_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_page_edit_post_form_correct_context(self):
        """Провертка формы edit_post."""
        response = self.authorized_client.get(
            reverse('posts:edit', kwargs={'post_id': self.post.pk}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

        self.assertEqual(response.context.get('is_edit'), True)

    def test_post_group_for_index_page(self):
        """Проверка что при создании поста указать группу,
        пост появляется на главной странице."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, self.post.text)

    def test_post_group_for_group_page(self):
        """Проверка что при создании поста указать группу,
        пост появляется на страницы выбранной группы."""
        response = self.authorized_client.get(
            reverse('posts:posts_list', kwargs={'slug': self.group.slug}))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, self.post.text)

    def test_post_group_for_index_page(self):
        """Проверка что при создании поста указать группу,
        пост не попал в группу для которой не блы предназначен."""
        response = self.authorized_client.get(
            reverse('posts:posts_list', kwargs={'slug': self.group.slug}))
        self.assertEqual(len(response.context['page_obj']), 1)

    def test_profile_group(self):
        """Проверка что при создании поста указать группу,
        пост появляется в профайле пользователя."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username}))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, self.post.text)

    def test_page_add_comment_form_correct_context(self):
        """Проверка формы add_comment."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}))
        form_fields = {
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_page_create_comment_(self):
        """Проверка что после отправки комментария он
        появляется на странице."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}))
        first_object = response.context['comments'][0]
        context_text = first_object.text
        self.assertEqual(context_text, self.comment.text)

    def test_cach_index_page(self):
        """Тестирование кэша inbdex."""
        response_index = self.authorized_client.get(reverse('posts:index'))
        content_index = response_index.content
        response_cash = self.authorized_client.get(reverse('posts:index'))
        content_cash = response_cash.content
        self.assertEqual(content_cash, content_index)
        cache.clear()
        response_new_index = self.authorized_client.get(reverse('posts:index'))
        content_index_new = response_new_index.content
        self.assertNotEqual(content_index_new, content_cash)


class PaginatorPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовй заголовок',
            slug='test-slug',
            description='Описание группы'
        )
        posts = []
        for i in range(1, 101):
            posts.append(Post(
                author=cls.user,
                text='Тестовый текст поста' + str(i),
                group=cls.group)
            )
        Post.objects.bulk_create(posts)
        total_posts = Post.objects.all().count()
        cls.page_paginator = (total_posts // 10) + 1
        cls.page_paginator_remains = total_posts % 10

    def setUp(self):
        self.guest_client = Client()

    def test_index_page_paginator(self):
        """Тестрование пагинатора index."""
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), VAR_NUMBER_POSTS)
        response = self.client.get(
            reverse('posts:index') + f'?page={self.page_paginator}'
        )
        if self.page_paginator_remains != 0:
            self.assertEqual(
                len(response.context['page_obj']), self.page_paginator_remains
            )

    def test_group_list_page_paginator(self):
        """Тестрование пагинатора group_list."""
        response = self.client.get(
            reverse('posts:posts_list', kwargs={'slug': self.group.slug}))
        self.assertEqual(len(response.context['page_obj']), VAR_NUMBER_POSTS)
        response = self.client.get(
            reverse('posts:posts_list', kwargs={'slug': self.group.slug})
            + f'?page={self.page_paginator}')
        if self.page_paginator_remains != 0:
            self.assertEqual(
                len(response.context['page_obj']), self.page_paginator_remains
            )

    def test_profile_page_paginator(self):
        """Тестрование пагинатора profile, автора test_user"""
        response = self.client.get(
            reverse('posts:profile', kwargs={'username': self.user.username}))
        self.assertEqual(len(response.context['page_obj']), VAR_NUMBER_POSTS)
        response = self.client.get(
            reverse('posts:profile', kwargs={'username': self.user.username})
            + f'?page={self.page_paginator}')
        if self.page_paginator_remains != 0:
            self.assertEqual(len(
                response.context['page_obj']), self.page_paginator_remains
            )


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.user_follow = User.objects.create_user(username='test_uset_follow')
        cls.user_unfollow = User.objects.create_user(
            username='test_uset_unfollow'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            author=cls.user,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.guest_client = Client()

    def test_profile_follow_autorized_client(self):
        """Авторизованный пользователь может подписываться на
        пользователей profile_follow."""
        count_no_follower = Follow.objects.all().count()
        self.authorized_client.get(Follow.objects.create(
            user=self.user_follow, author=self.user))
        self.assertEqual(count_no_follower + 1, Follow.objects.all().count())
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username}))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_author_0, self.post.author)

    def test_profile_unfollow_autorized_client(self):
        """Авторизованный пользователь может подписываться
        на пользователей profile_unfollow."""
        count_no_follower = Follow.objects.all().count()
        Follow.objects.create(user=self.user_follow, author=self.user)
        count_follower = Follow.objects.all().count()
        self.assertEqual(count_no_follower + 1, count_follower)
        Follow.objects.get(user=self.user_follow, author=self.user).delete()
        count_follower = Follow.objects.all().count()
        self.assertEqual(count_no_follower, count_follower)

    def test_profile_follow_index_autorized_client(self):
        """Новая запись пользователя появляется в ленте тех,
        кто на него подписан"""
        count_no_follower = Follow.objects.all().count()
        count_post = Post.objects.all().count()
        Follow.objects.create(user=self.user, author=self.user_follow)
        Post.objects.create(text='Тестовый текст поста для подписки',
                            author=self.user_follow)
        self.assertEqual(count_no_follower + 1, Follow.objects.all().count())
        self.assertEqual(count_post + 1, Post.objects.all().count())
        count_post_follow = Post.objects.all().filter(
            author__following__user=self.user).count()
        self.assertEqual(count_post_follow, Post.objects.all().count() - 1)

    def test_profile_follow_index_autorized_client_unfollow(self):
        """Новая запись не пользователя появляется в ленте тех,
        кто на него не подписан."""
        count_no_follower = Follow.objects.all().count()
        count_post = Post.objects.all().count()
        Follow.objects.create(user=self.user, author=self.user_follow)
        Post.objects.create(
            text='Тестовый текст поста для подписки',
            author=self.user_follow
        )
        self.assertEqual(count_no_follower + 1, Follow.objects.all().count())
        self.assertEqual(count_post + 1, Post.objects.all().count())
        count_post_follow = Post.objects.all().filter(
            author__following__user=self.user_unfollow).count(
        )
        self.assertEqual(count_post_follow, Post.objects.all().count() - 2)
