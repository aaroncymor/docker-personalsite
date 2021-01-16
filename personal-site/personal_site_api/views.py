from django.contrib.auth.models import User
from django.conf import settings
from django.urls import reverse

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import mixins, status,viewsets, serializers
from rest_framework.views import Response
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.authentication import BasicAuthentication

from blog.models import (
    Category,
    Post,
    Tag,
    Decipher
)

from .serializers import (
    UserSerializer,
    CategorySerializer,
    PostSerializer,
    PostSearchSerializer,
    TagSerializer,
    DecipherSerializer,
)

from .filters import (
    CategoryFilter,
    PostFilter,
    TagFilter,
    DecipherFilter,
)

from .pagination import CustomPagination
from .mixins import CustomListModelMixin
from .authentication import CsrfExemptSessionAuthentication

# Create your views here.


class UserViewSet(mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CategoryViewSet(mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = CategoryFilter


class PostViewSet(CustomListModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filter_backends = (DjangoFilterBackend,)    
    filter_class = PostFilter
    pagination_class = CustomPagination


class TagViewSet(CustomListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_backends = (DjangoFilterBackend,)    
    filter_class = TagFilter
    pagination_class = CustomPagination


class DecipherViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    queryset = Decipher.objects.all()
    serializer_class = DecipherSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = DecipherFilter

    @action(detail=True, methods=['POST'], url_name='check-code',
            authentication_classes=(CsrfExemptSessionAuthentication,
            BasicAuthentication))
    def check_code(self, request, pk=None, *args, **kwargs):
        """
        TODO: Using below reference, we need to implement a custom
        SesionAuthentication and override enforce csrf so that this
        method gets passed csrf check. 
        
        ref:
        https://www.cnblogs.com/AmilyWilly/p/6438448.html
        https://github.com/encode/django-rest-framework/blob/master/rest_framework/authentication.py
        """
        response = {}
        request_data = request.data
        
        if 'code' not in request_data.keys():
            response['error'] = 'The code is required.'
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        code = request_data['code']
        instance = self.get_object()
        
        if instance.code:
            if code != instance.code:
                response['error'] = 'The code is not matching with decipher code.'
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        headers = {'content-type': 'application/json'}
        response.update({'hidden_text':instance.hidden_text})
        return Response(response, status=status.HTTP_200_OK, headers=headers)


@api_view(['POST'])
def autocomplete_search(request):
    response = {}
    search_results = []
    headers = {'content-type': 'application/json'}
    if request.method == 'POST':
        if 'search' in request.data:
            search = request.data['search']

            title_search = PostFilter({'title_icontains': search}, Post.objects.all()).qs.values('id', 'title')
            category_search = PostFilter({'category_name': search}, Post.objects.all()).qs.values('id', 'title', 'category__name')
            tag_search = PostFilter({'tag_iexact': search}, Post.objects.all()).qs.values('id', 'title')

            for item in title_search:
                # add new key value pair for search type
                item['type'] = 'post'
                item['link'] = reverse('post-detail', kwargs={'pk': item['id']})
                search_results.append(item)
            

            for item in category_search:
                # pop values from 'title' and 'category__name' keys
                temp_title = item.pop('title')
                category_name = item.pop('category__name')
                
                # update title
                item['title'] = temp_title + ' ' + category_name

                # add new key value pair for search type
                item['type'] = 'category'
                item['link'] = reverse('post-detail', kwargs={'pk': item['id']})

                search_results.append(item)

            for item in tag_search:
                # pop values from 'title'
                temp_title = item.pop('title')

                # update title. Assumes that search is tag
                item['title'] = temp_title + ' ' + search

                # add new key value pair for search type
                item['type'] = 'tag'

                item['link'] = reverse('post-detail', kwargs={'pk': item['id']})
                                
                search_results.append(item)

        return Response(search_results, status=status.HTTP_200_OK, headers=headers)


@api_view(['POST'])
def get_tags_by_post(request):
    response = {}
    tag_list = []
    
    headers = {'Content-Type': 'application/json'}
    if request.method == 'POST':
        request_data_keys = request.data.keys()

        if not 'post_id' in request_data_keys:
            # throw error
            pass
        
        post_id = request.data['post_id']
        tag_list = Tag.objects.filter(post__id=post_id).values_list('tag', flat=True)
            
    return Response(tag_list, status=status.HTTP_200_OK, headers=headers)

