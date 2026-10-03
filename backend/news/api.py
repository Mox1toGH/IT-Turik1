import logging

from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404

from ninja import Router

from accounts.models import User
from backend.auth import JWTAuth
from backend.permissions import Permission, require_permission
from notifications.services import NotificationService

from .models import NewsArticle

from backend.schemas import ErrorResponse
from backend.errors import raise_api_error
from http import HTTPStatus
from .schemas import NewsArticleRequest, NewsArticlePatchRequest, NewsArticleResponse, NewsListResponse

logger = logging.getLogger(__name__)

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


def _notify_news_published(request, article):
    logger.info(
        'Sending news notification: news_id=%s user_id=%s',
        article.id, request.auth.id,
    )
    try:
        NotificationService.notify(
            recipients=User.objects.exclude(id=request.auth.id),
            event_type='news_published',
            context={'news_id': article.id, 'news_title': article.title},
        )
    except Exception:
        logger.exception('News notification failed: news_id=%s', article.id)
        raise


@router.get('', operation_id='listNews', response={200: NewsListResponse, 401: ErrorResponse})
def list_news(request, page: int = 1, page_size: int = 10):
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)
    logger.debug('Listing news: page=%s page_size=%s user_id=%s', page, page_size, request.auth.id)
    queryset = NewsArticle.objects.select_related('created_by').all()
    offset = (page - 1) * page_size

    return NewsListResponse(
        items=[
            _serialize_article(article)
            for article in queryset[offset:offset + page_size]
        ],
        count=queryset.count(),
    )


@router.post('', operation_id='createNews', url_name="news_list_create", response={201: NewsArticleResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse})
@transaction.atomic
def create_news(request, payload: NewsArticleRequest):
    require_permission(request, Permission.CREATE_NEWS)

    data = payload.model_dump()
    send_notification = data.pop('send_notification', False)
    logger.info('Creating news article: user_id=%s send_notification=%s', request.auth.id, send_notification)

    article = NewsArticle(created_by=request.auth)
    for field, value in data.items():
        setattr(article, field, value)

    try:
        article.full_clean()
    except ValidationError as exc:
        logger.warning(
            'News creation rejected: user_id=%s fields=%s',
            request.auth.id, sorted(exc.message_dict.keys()),
        )
        raise_api_error(HTTPStatus.BAD_REQUEST, exc.message_dict)
    article.save()
    logger.info('News article created: news_id=%s user_id=%s', article.id, request.auth.id)

    if send_notification:
        _notify_news_published(request, article)

    return 201, _serialize_article(article)



@router.get('/{article_id}', operation_id='getNews', url_name="news_detail", response={200: NewsArticleResponse, 401: ErrorResponse, 404: ErrorResponse})
def get_news(request, article_id: int):
    logger.debug('Fetching news article: news_id=%s', article_id)
    return _serialize_article(
        get_object_or_404(
            NewsArticle.objects.select_related('created_by'),
            pk=article_id,
        ),
    )


@router.patch('/{article_id}', operation_id='updateNews', url_name="news_detail", response={200: NewsArticleResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
@transaction.atomic
def update_news(request, article_id: int, payload: NewsArticlePatchRequest):
    require_permission(request, Permission.EDIT_NEWS)
    article = get_object_or_404(NewsArticle.objects.select_related('created_by'), pk=article_id)

    if request.auth.role == 'organizer' and article.created_by_id != request.auth.id:
        logger.warning(
            'News update rejected, not author: news_id=%s user_id=%s author_id=%s',
            article_id, request.auth.id, article.created_by_id,
        )
        raise_api_error(HTTPStatus.FORBIDDEN, 'You can manage only your own articles.')

    data = payload.model_dump(exclude_unset=True)
    send_notification = data.pop('send_notification', False)
    logger.info(
        'Updating news article: news_id=%s user_id=%s fields=%s send_notification=%s',
        article_id, request.auth.id, sorted(data.keys()), send_notification,
    )

    for field, value in data.items():
        setattr(article, field, value)

    try:
        article.full_clean()
    except ValidationError as exc:
        logger.warning(
            'News update rejected: news_id=%s user_id=%s fields=%s',
            article_id, request.auth.id, sorted(exc.message_dict.keys()),
        )
        raise_api_error(
            HTTPStatus.BAD_REQUEST,
            {field: messages[0] for field, messages in exc.message_dict.items()},
        )
    article.save()
    logger.info('News article updated: news_id=%s user_id=%s', article_id, request.auth.id)

    if send_notification:
        _notify_news_published(request, article)

    return _serialize_article(article)


@router.delete('/{article_id}', operation_id='deleteNews', url_name="news_detail", response={204: None, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def delete_news(request, article_id: int):
    require_permission(request, Permission.DELETE_NEWS)
    article = get_object_or_404(NewsArticle, pk=article_id)

    if request.auth.role == 'organizer' and article.created_by_id != request.auth.id:
        logger.warning(
            'News delete rejected, not author: news_id=%s user_id=%s author_id=%s',
            article_id, request.auth.id, article.created_by_id,
        )
        raise_api_error(HTTPStatus.FORBIDDEN, 'You can manage only your own articles.')

    article.delete()
    logger.info('News article deleted: news_id=%s user_id=%s', article_id, request.auth.id)
    return 204, None