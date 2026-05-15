# views.py
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from backend.openapi import _400, _401, _403, _404

from .models import NewsArticle
from .permissions import CanDeleteNews, CanEditNews, CanManageNewsOrReadOnly
from .serializers import NewsArticleSerializer


class NewsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


@extend_schema(methods=['GET'], operation_id='listNews', responses={
    200: NewsArticleSerializer(many=True),
    401: _401,
})
@extend_schema(methods=['POST'], operation_id='createNews', responses={
    201: NewsArticleSerializer,
    400: _400,
    401: _401,
    403: _403,
})
class NewsListCreateView(generics.ListCreateAPIView):
    queryset = NewsArticle.objects.select_related('created_by').all()
    serializer_class = NewsArticleSerializer
    permission_classes = [IsAuthenticated, CanManageNewsOrReadOnly]
    pagination_class = NewsPagination


@extend_schema(methods=['GET'], operation_id='getNews', responses={
    200: NewsArticleSerializer,
    401: _401,
    404: _404,
})
@extend_schema(methods=['PUT'], operation_id='replaceNews', responses={
    200: NewsArticleSerializer,
    400: _400,
    401: _401,
    403: _403,
    404: _404,
})
@extend_schema(methods=['PATCH'], operation_id='updateNews', responses={
    200: NewsArticleSerializer,
    400: _400,
    401: _401,
    403: _403,
    404: _404,
})
@extend_schema(methods=['DELETE'], operation_id='deleteNews', responses={
    204: OpenApiResponse(description='Article deleted successfully.'),
    401: _401,
    403: _403,
    404: _404,
})
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