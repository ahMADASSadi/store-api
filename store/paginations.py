from rest_framework.pagination import PageNumberPagination


class ProductHomePagination(PageNumberPagination):
    page_size = 20
    page_query_param = 'page'


class ReviewPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'reviews_per_page'
    max_page_size = 100
