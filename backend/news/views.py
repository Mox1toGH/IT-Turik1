from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from .models import NewsArticle
from .permissions import CanDeleteNews, CanEditNews, CanManageNewsOrReadOnly
from .serializers import NewsArticleSerializer


class NewsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class NewsListCreateView(generics.ListCreateAPIView):
    queryset = NewsArticle.objects.select_related('created_by').all()
    serializer_class = NewsArticleSerializer
    permission_classes = [IsAuthenticated, CanManageNewsOrReadOnly]
    pagination_class = NewsPagination


class NewsDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = NewsArticle.objects.select_related('created_by').all()
    serializer_class = NewsArticleSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.request.method == 'DELETE':
            permission_classes.append(CanDeleteNews)
        elif self.request.method in ('PUT', 'PATCH'):
            permission_classes.append(CanEditNews)
        else:
            permission_classes.append(CanManageNewsOrReadOnly)
        return [permission() for permission in permission_classes]
