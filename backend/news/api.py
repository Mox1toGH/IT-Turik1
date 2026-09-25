from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404

from ninja import Router
from ninja.errors import HttpError

from accounts.models import User
from backend.auth import JWTAuth
from backend.permissions import Permission, has_permission
from notifications.services import NotificationService

from .models import NewsArticle

from backend.schemas import ErrorResponse
from .schemas import NewsArticleRequest, NewsArticleResponse, NewsListResponse

router = Router(tags=['news'], auth=JWTAuth())


def _serialize_article(article):
    author = article.created_by
    return NewsArticleResponse(
        id=article.id,
        title=article.title,
        content=article.content,
        created_by=article.created_by_id,
        created_by_name=(author.full_name or author.username) if author else '',
        created_at=article.created_at,
        updated_at=article.updated_at,
    )


def _require_permission(request, permission, article=None):
    if not has_permission(request.auth, permission):
        raise HttpError(403, 'News permission required.')
    if article and request.auth.role == 'organizer' and article.created_by_id != request.auth.id:
        raise HttpError(403, 'You can manage only your own articles.')


def _save_article(request, article, payload):
    data = payload.model_dump()
    send_notification = data.pop('send_notification', False)
    
    for field, value in data.items():
        setattr(article, field, value)
    try:
        article.full_clean()
    except ValidationError as exc:
        raise HttpError(400, exc.message_dict) from None
    
    article.save()
    
    if send_notification:
        NotificationService.notify(
            recipients=User.objects.exclude(id=request.auth.id),
            event_type='news_published',
            context={'news_id': article.id, 'news_title': article.title},
        )
    
    return article


@router.get('', operation_id='listNews', response={200: NewsListResponse, 401: ErrorResponse})
def list_news(request, page: int = 1, page_size: int = 10):
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)
    queryset = NewsArticle.objects.select_related('created_by').all()
    offset = (page - 1) * page_size

    return NewsListResponse(
        items=[
            _serialize_article(article)
            for article in queryset[offset:offset + page_size]
        ],
        count=queryset.count(),
    )


@router.post('', operation_id='createNews', response={201: NewsArticleResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse})
@transaction.atomic
def create_news(request, payload: NewsArticleRequest):
    _require_permission(request, Permission.CREATE_NEWS)
    
    return 201, _serialize_article(
        _save_article(request, NewsArticle(created_by=request.auth), payload),
    )


@router.get('/{article_id}', operation_id='getNews', response={200: NewsArticleResponse, 401: ErrorResponse, 404: ErrorResponse})
def get_news(request, article_id: int):
    return _serialize_article(
        get_object_or_404(
            NewsArticle.objects.select_related('created_by'),
            pk=article_id,
        ),
    )


@router.put('/{article_id}', operation_id='replaceNews', response={200: NewsArticleResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
@router.patch('/{article_id}', operation_id='updateNews', response={200: NewsArticleResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
@transaction.atomic
def update_news(request, article_id: int, payload: NewsArticleRequest):
    article = get_object_or_404(NewsArticle.objects.select_related('created_by'), pk=article_id)
    _require_permission(request, Permission.EDIT_NEWS, article)
    
    return _serialize_article(_save_article(request, article, payload))


@router.delete('/{article_id}', operation_id='deleteNews', response={204: None, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def delete_news(request, article_id: int):
    article = get_object_or_404(NewsArticle, pk=article_id)
    _require_permission(request, Permission.DELETE_NEWS, article)
    
    article.delete()
    return 204, None
