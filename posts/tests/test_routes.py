from django.test import TestCase
from django.urls import reverse

from posts.models import Post, Group, User


USERNAME = 'Zhorik666'
GROUP_SLUG = 'slug'


class RoutesURLTests(TestCase):
    def test_routes_valid_url(self):
        self.user = User.objects.create(username=USERNAME)
        self.group = Group.objects.create(
            slug=GROUP_SLUG
        )
        self.post = Post.objects.create(
            text='text',
            author=self.user,
        )
        self.post_url = reverse(
            'post', kwargs={
                'username': USERNAME,
                'post_id': self.post.id
            }
        )
        self.POST_EDIT_URL = reverse(
            'post_edit', args=[USERNAME, self.post.id]
        )
        routes = {
            reverse('index'): '/',
            reverse('new_post'): '/new/',
            reverse('post', args=[
                USERNAME, self.post.id]):
            f'/{USERNAME}/{self.post.id}/',
            reverse('post_edit', args=[
                USERNAME, self.post.id]): f'/{USERNAME}/{self.post.id}/edit/',
            reverse('group_posts', args=[
                GROUP_SLUG]):
            f'/group/{GROUP_SLUG}/',
            reverse('profile', kwargs={'username': USERNAME}): f'/{USERNAME}/',
            reverse('follow_index'): '/follow/',
            reverse('profile_follow', args=[USERNAME]): f'/{USERNAME}/follow/',
            reverse('profile_unfollow',
                    args=[USERNAME]): f'/{USERNAME}/unfollow/',
        }
        for route, expected_url in routes.items():
            self.assertEqual(route, expected_url)
