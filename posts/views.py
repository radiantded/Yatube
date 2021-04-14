from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Comment, Follow
from .settings import POSTS_PER_PAGE


def index(request):
    page = Paginator(
        Post.objects.all(),
        POSTS_PER_PAGE).get_page(request.GET.get('page'))
    return render(request, 'index.html', {'page': page})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    page = Paginator(
        group.posts.all(),
        POSTS_PER_PAGE).get_page(request.GET.get('page'))
    return render(request, 'group.html', {'page': page, 'group': group})


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'new.html', {'form': form})
    new_post = form.save(commit=False)
    new_post.author = request.user
    new_post.save()
    return redirect('index')


def profile(request, username):
    author = get_object_or_404(User, username=username)
    page = Paginator(
        author.posts.all(),
        POSTS_PER_PAGE).get_page(request.GET.get('page'))
    try:
        following = Follow.objects.get(author=author, user=request.user)
        return render(request, 'profile.html', {'author': author,
                                                'page': page,
                                                'following': following})
    except Exception:
        return render(request, 'profile.html', {'author': author,
                                                'page': page})


def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    comments = Comment.objects.filter(post=post)
    context = {
        'author': post.author,
        'comments': comments,
        'form': form,
        'post': post
    }
    return render(request, 'post.html', context=context)


@login_required
def add_comment(request, username, post_id):
    form = CommentForm(request.POST or None)
    if not form.is_valid():
        return redirect('post', username=username, post_id=post_id)
    comment = form.save(commit=False)
    comment.author = request.user
    comment.post_id = post_id
    comment.save()
    return redirect('post', username=username, post_id=post_id)


@login_required
def post_edit(request, username, post_id):
    if request.user.username != username:
        return redirect('post', username=username, post_id=post_id)
    post = Post.objects.get(
        id=post_id,
        author__username=username
    )
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if not form.is_valid():
        return render(request, 'new.html', {'form': form, 'post': post})
    form.save()
    return redirect('post', username=username, post_id=post_id)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    page = Paginator(posts, POSTS_PER_PAGE).get_page(request.GET.get('page'))
    return render(request, 'follow.html', {'page': page})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(author=author, user=request.user)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(author=author, user=request.user).delete()
    return redirect('profile', username=username)
