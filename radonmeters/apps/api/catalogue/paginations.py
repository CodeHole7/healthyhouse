from rest_framework.pagination import PageNumberPagination


class LocationPageNumberPagination(PageNumberPagination):
    page_size = 200
