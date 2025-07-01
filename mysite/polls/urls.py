from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('mesclar/', views.mesclar, name='mesclar'),
    path('processar_mesclagem/', views.processar_mesclagem, name='processar_mesclagem'),
    path('clusters/', views.clusters_view, name='clusters'),
]
