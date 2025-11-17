from django.contrib import admin
from django.urls import path
from profiles.views import home

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),   # 👈 this replaces the rocket page
]