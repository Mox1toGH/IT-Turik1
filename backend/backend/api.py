from ninja import NinjaAPI
from ninja.errors import HttpError

from backend.ninja_exceptions import error_code_for_status
from certificates.api import router as certificates_router
from evaluation.api import router as evaluation_router
from accounts.api import router as accounts_router
from teams.api import router as teams_router
from inventory.api import router as inventory_router
from news.api import router as news_router
from notifications.api import router as notifications_router
from points.api import router as points_router
from shop.api import router as shop_router
from stats.api import router as stats_router
from tournaments.api import router as tournaments_router

api = NinjaAPI(title='Backend API (Ninja)', urls_namespace='ninja-api')


@api.exception_handler(HttpError)
def http_error_handler(request, exc):
    details = getattr(exc, 'details', None)
    return api.create_response(
        request,
        {
            'code': error_code_for_status(exc.status_code),
            'message': str(exc),
            'details': details,
        },
        status=exc.status_code,
    )

api.add_router('/certificates', certificates_router)
api.add_router('/evaluation', evaluation_router)
api.add_router('/accounts', accounts_router)
api.add_router('/teams', teams_router)
api.add_router('/inventory', inventory_router)
api.add_router('/news', news_router)
api.add_router('/notifications', notifications_router)
api.add_router('/points', points_router)
api.add_router('/shop', shop_router)
api.add_router('/stats', stats_router)
api.add_router('/tournaments', tournaments_router)
