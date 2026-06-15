from django.urls import path

from .urls.teams import urlpatterns as team_urls
from .urls.members import urlpatterns as member_urls
from .urls.invitations import urlpatterns as invitation_urls
from .urls.join_requests import urlpatterns as join_request_urls

urlpatterns = [
    *team_urls,
    *member_urls,
    *invitation_urls,
    *join_request_urls,
]
