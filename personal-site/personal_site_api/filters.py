import django_filters as filters
from django_filters.rest_framework import FilterSet

from blog.models import (
    Category,
    Post,
    Tag,
    Decipher
)

class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    pass

class CategoryFilter(FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    post_id = filters.NumberFilter(field_name='posts__id')
    post_title = filters.CharFilter(field_name='posts__title', lookup_expr='iexact')
    tag_id = filters.NumberFilter(field_name='posts__tags__id')
    tag = filters.CharFilter(field_name='posts__tags', lookup_expr='iexact')
    
    class Meta:
        model = Category
        fields = ['id', 'post_id', 'post_title', 'tag_id', 'tag']

class PostFilter(FilterSet):
    category_id = filters.NumberFilter(field_name='category__id')
    category_name = filters.CharFilter(field_name='category__name', lookup_expr='icontains')
    title_iexact = filters.CharFilter(field_name='title', lookup_expr='iexact')
    title_icontains = filters.CharFilter(field_name='title', lookup_expr='icontains')

    tag_id = filters.NumberFilter(field_name='tags__id')
    tag_iexact = filters.CharFilter(field_name='tags__tag', lookup_expr='iexact')
    tag_icontains = filters.CharFilter(field_name='tags__tag', lookup_expr='icontains')
    
    tags = CharInFilter(field_name='tags__tag', lookup_expr='in')
    
    class Meta:
        model = Post
        fields = ['id', 'category_id', 'category_name', 'title_iexact', 'title_icontains',
                'tag_id', 'tag_iexact', 'tag_icontains']


class TagFilter(FilterSet):
    tag = filters.CharFilter(field_name='tag', lookup_expr='icontains')
    post_id = filters.NumberFilter(field_name='post__id')
    post_title = filters.CharFilter(field_name='post__title', lookup_expr='iexact')
    category_id = filters.NumberFilter(field_name='post__category__id')
    category_name = filters.CharFilter(field_name='post__category__name', lookup_expr='icontains')

    class Meta:
        model = Tag
        fields = ['id', 'tag', 'post_id', 'post_title', 'category_id', 'category_name']


class DecipherFilter(FilterSet):
    post_id = filters.NumberFilter(field_name='post__id')
    post_title = filters.NumberFilter(field_name='post__title', lookup_expr='iexact')
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    category_id = filters.NumberFilter(field_name='post__category__id')
    category_name = filters.CharFilter(field_name='post__category__name', lookup_expr='icontains')

    class Meta:
        model = Decipher
        fields = ['id', 'post_id', 'post_title', 'name', 'category_id', 'category_name']

