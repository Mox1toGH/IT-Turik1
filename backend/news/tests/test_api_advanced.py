from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from accounts.models import User
from news.models import NewsArticle

class NewsApiAdvancedTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user('news_admin', 'n_a@e.com', 'pass', role='admin', is_staff=True)
        self.user = User.objects.create_user('news_user', 'n_u@e.com', 'pass')
        self.article1 = NewsArticle.objects.create(title='A1', content={}, created_by=self.admin)
        self.article2 = NewsArticle.objects.create(title='A2', content={}, created_by=self.admin)

    # 15 tests
    def test_list_news_anonymous(self):
        url = reverse('newsarticle-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 2)

    def test_list_news_authenticated(self):
        url = reverse('newsarticle-list')
        self.client.force_authenticate(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_news_anonymous(self):
        url = reverse('newsarticle-detail', kwargs={'pk': self.article1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'A1')

    def test_retrieve_news_authenticated(self):
        url = reverse('newsarticle-detail', kwargs={'pk': self.article2.id})
        self.client.force_authenticate(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_news_admin(self):
        url = reverse('newsarticle-list')
        self.client.force_authenticate(self.admin)
        response = self.client.post(url, {'title': 'A3', 'content': {}})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(NewsArticle.objects.count(), 3)

    def test_create_news_user_forbidden(self):
        url = reverse('newsarticle-list')
        self.client.force_authenticate(self.user)
        response = self.client.post(url, {'title': 'A3', 'content': {}})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_news_anonymous_forbidden(self):
        url = reverse('newsarticle-list')
        response = self.client.post(url, {'title': 'A3', 'content': {}})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_news_admin(self):
        url = reverse('newsarticle-detail', kwargs={'pk': self.article1.id})
        self.client.force_authenticate(self.admin)
        response = self.client.patch(url, {'title': 'A1 Updated'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.article1.refresh_from_db()
        self.assertEqual(self.article1.title, 'A1 Updated')

    def test_update_news_user_forbidden(self):
        url = reverse('newsarticle-detail', kwargs={'pk': self.article1.id})
        self.client.force_authenticate(self.user)
        response = self.client.patch(url, {'title': 'A1 Updated'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_news_admin(self):
        url = reverse('newsarticle-detail', kwargs={'pk': self.article2.id})
        self.client.force_authenticate(self.admin)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(NewsArticle.objects.count(), 1)

    def test_delete_news_user_forbidden(self):
        url = reverse('newsarticle-detail', kwargs={'pk': self.article2.id})
        self.client.force_authenticate(self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_search_news(self):
        url = reverse('newsarticle-list') + '?search=A1'
        response = self.client.get(url)
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], 'A1')

    def test_search_news_not_found(self):
        url = reverse('newsarticle-list') + '?search=A3'
        response = self.client.get(url)
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 0)

    def test_create_news_invalid_content(self):
        url = reverse('newsarticle-list')
        self.client.force_authenticate(self.admin)
        response = self.client.post(url, {'title': 'A3', 'content': 'not a dict'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_news_missing_title(self):
        url = reverse('newsarticle-list')
        self.client.force_authenticate(self.admin)
        response = self.client.post(url, {'content': {}})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
