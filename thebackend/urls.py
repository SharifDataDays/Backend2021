"""thebackend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('api/', include('apps.homepage.urls')),
    path('api/accounts/', include('apps.accounts.urls')),
    path('martor/', include('martor.urls')),
    path('api/resources/', include('apps.resources.urls')),
    path('api/blog/', include('apps.blog.urls')),
    path('api/subscribe/', include('apps.notification.urls')),
    path('api/contest/', include('apps.contest.urls')),
    path('api/question/', include('apps.question.urls')),
    path('api/participation/', include('apps.participation.urls')),
    path('api/private_files/', include('private_files.urls')),
    path('go/', include('apps.go.urls')),
    path('api/staff/', include('apps.staff.urls')),
    path('api/rrank/', include('apps.rrank.urls')),
]

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    urlpatterns += \
        static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
