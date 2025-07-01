from rest_framework.pagination import PageNumberPagination


class CoursePaginator(PageNumberPagination):
    page_size = 10
    page_query_param = 'page_size'
    max_page_size = 1000

class LessonsPaginator(PageNumberPagination):
    page_size = 10
    page_query_param = 'page_size'
    max_page_size = 1000