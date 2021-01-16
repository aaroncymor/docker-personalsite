"""personal_site URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import re_path, path, include
from django.conf import settings
from django.conf.urls.static import static

#from filebrowser.sites import site


urlpatterns = [
    # django-filebrowser url requires to be before admin url
#    path('admin/filebrowser/', site.urls),
    path('grappelli/', include('grappelli.urls')),
    path('tinymce/', include('tinymce.urls')),
    path('api-auth/', include('rest_framework.urls')),

    path('admin/', admin.site.urls),

    # core
    path('', include('core.urls')),
    path('api/v1/', include('personal_site_api.apiv1', namespace='api')),

    path('blog/', include('blog.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
