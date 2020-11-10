"""FirstProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from posts import views
from django.conf import settings
from accounts.views import (login_view, logout_view, register_view)

urlpatterns = [
    url(r"^admin/", admin.site.urls),
    url(r"^posts/", include(("posts.urls", 'posts'), namespace="posts")),
    # url(r"^accounts/", include(("accounts.urls", 'accounts'), namespace="accounts")),
    url(r"^login", login_view, name="login"),
    url(r"^logout", logout_view, name="logout"),
    url(r"^register", register_view, name="register"),
    url(r"", include(("posts.urls", 'posts'), namespace="posts")),


    # url(r"^posts/$", "posts.views.post_home"), # more cleaner way, but not working
    # path(r"posts/", views.post_home), # Either way is valid
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
