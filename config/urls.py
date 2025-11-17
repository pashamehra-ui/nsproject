from django.contrib import admin
from django.urls import path
import profiles.views as pv

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", pv.home, name="home"),
    path("graph/", pv.graph, name="graph"),
]