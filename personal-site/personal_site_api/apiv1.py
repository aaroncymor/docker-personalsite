from django.conf import settings
from django.urls import re_path, include

from rest_framework import routers

from personal_site_api.views import (
    UserViewSet,
    CategoryViewSet,
    PostViewSet,
    TagViewSet,
    DecipherViewSet,
    autocomplete_search,
    get_tags_by_post,
)

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'users', UserViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'posts', PostViewSet)
router.register(r'tags', TagViewSet)
router.register(r'deciphers', DecipherViewSet)

app_name = 'api'
urlpatterns = [
    re_path(r'^', include(router.urls), name='v1'),
    re_path(r'autocomplete', autocomplete_search, name='autocomplete-search'),
    re_path(r'post-tags', get_tags_by_post, name='tags-by-post'),
]