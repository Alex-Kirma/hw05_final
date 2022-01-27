from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from yatube.settings import VAR_NUMBER_POSTS

from .models import Group, Post, Comment, Follow
from .forms import PostForm, CommentForm


def paginator_page(request, posts):
    paginator = Paginator(posts, VAR_NUMBER_POSTS)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    posts = Post.objects.all()
    page_obj = paginator_page(request, posts)
    context = {
        "page_obj": page_obj,
    }
    return render(request, "posts/index.html", context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = paginator_page(request, posts)
    context = {
        "group": group,
        "page_obj": page_obj,
    }
    return render(request, "posts/group_list.html", context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    posts = author.posts.all()
    number_of_posts = posts.count()
    if user.is_authenticated and Follow.objects.filter(
            user=user, author=author).exists():
        following = True
    else:
        following = False
    page_obj = paginator_page(request, posts)
    context = {
        "page_obj": page_obj,
        "author": author,
        "number_of_posts": number_of_posts,
        "following": following
    }
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    number_of_posts = post.author.posts.count()
    comments = Comment.objects.all().filter(post=post)
    form = CommentForm()
    context = {
        "post": post,
        "number_of_posts": number_of_posts,
        'form': form,
        'comments': comments,
    }
    return render(request, "posts/post_detail.html", context)


@login_required
def post_create(request):

    form = PostForm(request.POST or None, files=request.FILES or None)

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("posts:profile", username=request.user)

    groups = Group.objects.all()
    context = {
        "form": form,
        "groups": groups,
    }
    return render(request, "posts/create_post.html", context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    groups = Group.objects.all()
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if post.author != request.user:
        return redirect("posts:post_detail", post_id=post.pk)
    if form.is_valid():
        post = form.save()
        return redirect("posts:post_detail", post_id=post.pk)
    context = {
        "groups": groups,
        "is_edit": True,
        "post": post,
        "form": form,
    }
    return render(request, "posts/create_post.html", context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    user = request.user
    posts = Post.objects.all().filter(author__following__user=user)
    page_obj = paginator_page(request, posts)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    if author != user:
        Follow.objects.get_or_create(user=user, author=author)
    return redirect('posts:profile', author)


@login_required
def profile_unfollow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    Follow.objects.get(user=user, author=author).delete()
    return redirect('posts:profile', user)
