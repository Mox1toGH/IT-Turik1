from ninja.pagination import PageNumberPagination


class APIPageNumberPagination(PageNumberPagination):
    """Default API collection contract: 20 items per page, at most 100."""

    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
