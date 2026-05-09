from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from .models import NewsArticle


class NewsApiTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='news-admin',
            email='news-admin@example.com',
            password='StrongPass123!',
            role='admin',
            is_staff=True,
            is_superuser=True,
        )
        self.organizer = User.objects.create_user(
            username='news-organizer',
            email='news-organizer@example.com',
            password='StrongPass123!',
            role='organizer',
        )
        self.team_user = User.objects.create_user(
            username='news-team',
            email='news-team@example.com',
            password='StrongPass123!',
            role='team',
        )

        self.list_url = reverse('news_list_create')

    def test_admin_can_create_news(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            self.list_url,
            {
                'title': 'Platform update',
                'content': {'type': 'doc', 'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Hello'}]}]},
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(NewsArticle.objects.count(), 1)

    def test_organizer_can_create_news(self):
        self.client.force_authenticate(user=self.organizer)
        response = self.client.post(
            self.list_url,
            {
                'title': 'Organizer news',
                'content': {'type': 'doc', 'content': []},
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_team_user_cannot_create_news(self):
        self.client.force_authenticate(user=self.team_user)
        response = self.client.post(
            self.list_url,
            {
                'title': 'Forbidden news',
                'content': {'type': 'doc', 'content': []},
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_user_can_read_news(self):
        article = NewsArticle.objects.create(
            title='Read me',
            content={'type': 'doc', 'content': []},
            created_by=self.admin,
        )
        self.client.force_authenticate(user=self.team_user)
        detail_url = reverse('news_detail', kwargs={'pk': article.id})

        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], article.id)

    def test_news_list_is_paginated(self):
        self.client.force_authenticate(user=self.team_user)
        for i in range(12):
            NewsArticle.objects.create(
                title=f'News {i}',
                content={'type': 'doc', 'content': []},
                created_by=self.admin,
            )

        response = self.client.get(self.list_url, {'page': 1, 'page_size': 10})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('results', response.data)
        self.assertEqual(response.data['count'], 12)
        self.assertEqual(len(response.data['results']), 10)

    def test_team_user_cannot_update_or_delete_news(self):
        article = NewsArticle.objects.create(
            title='Protected',
            content={'type': 'doc', 'content': []},
            created_by=self.admin,
        )
        detail_url = reverse('news_detail', kwargs={'pk': article.id})
        self.client.force_authenticate(user=self.team_user)

        update_response = self.client.patch(detail_url, {'title': 'Changed'}, format='json')
        delete_response = self.client.delete(detail_url)

        self.assertEqual(update_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_organizer_can_update_and_delete_news(self):
        article = NewsArticle.objects.create(
            title='Organizer item',
            content={'type': 'doc', 'content': []},
            created_by=self.admin,
        )
        detail_url = reverse('news_detail', kwargs={'pk': article.id})
        self.client.force_authenticate(user=self.organizer)

        update_response = self.client.patch(detail_url, {'title': 'Updated by organizer'}, format='json')
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)

        delete_response = self.client.delete(detail_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
