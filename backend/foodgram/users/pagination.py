from rest_framework.pagination import PageNumberPagination


class PageLimitPagination(PageNumberPagination):
    page_query_param = 'page'
    page_size = 10
    max_page_size = 100

    page_size_query_param = 'page_size'

    def get_page_size(self, request):
        limit = request.query_params.get('limit')
        if limit is not None:
            try:
                return min(int(limit), self.max_page_size)
            except ValueError:
                pass
        return super().get_page_size(request)
