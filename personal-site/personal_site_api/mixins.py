from rest_framework.response import Response
from rest_framework import mixins

class CustomListModelMixin(mixins.ListModelMixin):
    # customized Response return since when we remove query_params 'page_size',
    # response is not the same as pagination. We add key 'results' even if page_size
    # is "turned off" or not as query_params
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        try:
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
        except Exception:
            pass

        serializer = self.get_serializer(queryset, many=True)
        return Response({'results': serializer.data})