from django.test import TestCase
from news.models import NewsArticle
from accounts.models import User

class NewsModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='news-author', email='author@example.com')

    def test_news_article_str(self):
        article = NewsArticle.objects.create(
            title='Breaking News',
            content={'type': 'doc', 'content': []},
            created_by=self.user
        )
        self.assertEqual(str(article), 'Breaking News')

    def test_news_article_slug_or_id_check(self):
        # Just verifying it has an ID and can be retrieved
        article = NewsArticle.objects.create(
            title='T', content={}, created_by=self.user
        )
        self.assertIsNotNone(article.id)

    def test_news_article_timestamps(self):
        article = NewsArticle.objects.create(
            title='T', content={}, created_by=self.user
        )
        self.assertIsNotNone(article.created_at)
        self.assertIsNotNone(article.updated_at)

    def test_news_article_content_type(self):
        article = NewsArticle.objects.create(
            title='T', content={'type': 'doc'}, created_by=self.user
        )
        self.assertEqual(article.content['type'], 'doc')

    def test_news_article_title_max_length(self):
        long_title = 'A' * 255
        article = NewsArticle.objects.create(title=long_title, content={}, created_by=self.user)
        self.assertEqual(len(article.title), 255)

    def test_news_article_meta_ordering(self):
        a1 = NewsArticle.objects.create(title='A1', content={}, created_by=self.user)
        a2 = NewsArticle.objects.create(title='A2', content={}, created_by=self.user)
        # Assuming ordering is -created_at
        articles = NewsArticle.objects.all()
        self.assertEqual(articles[0], a2)

    def test_news_author_cascade(self):
        NewsArticle.objects.create(title='T', created_by=self.user)
        self.user.delete()
        self.assertEqual(NewsArticle.objects.count(), 1)
        self.assertIsNone(NewsArticle.objects.first().created_by)

    def test_large_content_handling(self):
        large_content = {'type': 'doc', 'content': [{'type': 'text', 'text': 'A' * 1000}]}
        article = NewsArticle.objects.create(title='Large', content=large_content, created_by=self.user)
        self.assertEqual(article.content['content'][0]['text'], 'A' * 1000)

    def test_article_without_title_fails(self):
        from django.core.exceptions import ValidationError
        article = NewsArticle(content={}, created_by=self.user)
        with self.assertRaises(Exception):
            article.full_clean()

    def test_article_with_empty_content(self):
        article = NewsArticle.objects.create(title='Empty', content={}, created_by=self.user)
        self.assertEqual(article.content, {})

    def test_multiple_articles_by_same_author(self):
        NewsArticle.objects.create(title='N1', content={}, created_by=self.user)
        NewsArticle.objects.create(title='N2', content={}, created_by=self.user)
        self.assertEqual(self.user.created_news_articles.count(), 2)
