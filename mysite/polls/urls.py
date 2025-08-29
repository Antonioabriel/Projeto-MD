from django.urls import path
from . import views

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # upload inicial, se precisar
    path('mesclar/', views.mesclar, name='mesclar'),
    path('processar_mesclagem/', views.processar_mesclagem, name='processar_mesclagem'),
    path('clusters/', views.clusters_view, name='clusters'),
    path('gerar_grafico/', views.gerar_grafico_view, name='gerar_grafico'),
    path('selecionar_colunas/', views.selecionar_colunas, name='selecionar_colunas'),
    path('gerar/', views.gerar, name='gerar'),  # <-- novo endpoint para gerar CSV
]
