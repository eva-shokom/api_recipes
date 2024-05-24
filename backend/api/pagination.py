from rest_framework.pagination import PageNumberPagination

from foodgram.constants import PAGINATION_PAGE_SIZE


class CustomPagination(PageNumberPagination):
    page_size_query_param = 'limit'
    page_size = PAGINATION_PAGE_SIZE
