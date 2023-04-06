from django.urls import path
from base_dados.views import listar_bases, ver_base_dados

urlpatterns = [
    path('', listar_bases, name='index'),
    path('verBaseDados/<str:base_dados>', ver_base_dados, name='verBaseDados'),
]
