from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/accounts/', include('accounts.urls')),
    path('api/teams/', include('teams.urls')),
    path('api/tournaments/', include('tournaments.urls')),
    path("api/evaluation/", include("evaluation.urls")),
    path("api/certificates/", include("certificates.urls")),
    path('api/notifications/', include('notifications.urls')),
    path('api/stats/', include('stats.urls')),
    path('api/news/', include('news.urls')),
    path('api/points/', include('points.urls')),
    path('api/shop/', include('shop.urls')),
    path('api/inventory/', include('inventory.urls')),

    # OpenAPI schema
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)