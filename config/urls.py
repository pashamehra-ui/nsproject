from django.contrib import admin
from django.urls import path
import profiles.views as pv

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", pv.home, name="home"),
    path("graph/", pv.graph, name="graph"),
    path("api/edges", pv.edges_list, name="edges_list"),
    path("api/edges/add", pv.edges_add, name="edges_add"),
    path("api/edges/delete", pv.edges_delete, name="edges_delete"),
]
