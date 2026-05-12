from django.urls import path

from .views import NewsDetailView, NewsListCreateView

urlpatterns = [
    path('', NewsListCreateView.as_view(), name='news_list_create'),
    path('<int:pk>/', NewsDetailView.as_view(), name='news_detail'),
]

