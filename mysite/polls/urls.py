from django.urls import path
from . import views

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # upload inicial, se precisar
    path('inicio/', views.index_sem_limpar, name='index_sem_limpar'),  # Só renderiza sem apagar nada
    path('analise/', views.analiseEstatistica, name='analise'),
    path('processar_mesclagem/', views.processar_mesclagem, name='processar_mesclagem'),
    path('clusters/', views.clusters_view, name='clusters'),
    path('gerar_grafico/', views.gerar_grafico_view, name='gerar_grafico'),
    path('upload_armazenar/', views.upload_armazenar, name='upload_armazenar'),
    path('gerar/', views.gerar, name='gerar'),  # <-- novo endpoint para gerar CSV
    path('listar_colunas_anos/', views.listar_colunas_anos, name='listar_colunas_anos'),
    path('baixar_resultado/', views.baixar_resultado, name='baixar_resultado'),
    path('analise_clusters/', views.analise_clusters, name='analise_clusters'),
    path('baixar_clusters_excel/', views.baixar_clusters_excel, name='baixar_clusters_excel'),
]
