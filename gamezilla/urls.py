"""gamezilla URL Configuration

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
from django.contrib import admin
from django.urls import path, include

from game import views as game_views
from account.views import *
from snakeAndLadder import views as SNL_views
from ticTacToe import views as TAC_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", game_views.home, name="home"),
    path("register/", include("account.urls")),
    path("logout/", logout_, name="logout"),
    path("report/", game_views.report, name="report"),
    path("host/<str:game_code>/", game_views.host_game, name="host"),
    path("room/<slug:sp_id>/", game_views.host_room_view, name="host_room"),
    path("join/<slug:sp_id>/", game_views.join_game, name="join"),
    path("join/", game_views.join_room, name="join_room"),
    path("SNL/<slug:game_id>/", SNL_views.game),
    path("TAC/<slug:game_id>/", TAC_views.game),
    path("leave/<slug:sp_id>/", game_views.leave),
    # You MUST use an empty string as the URL prefix
    path("", include("pwa.urls")),
    path("new-home/",game_views.new_home),
   path("profile/",game_views.profile,name="profile")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
