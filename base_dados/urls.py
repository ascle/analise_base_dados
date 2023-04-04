from django.urls import path
from base_dados.views import index

urlpatterns = [
    path('', index, name='index'),
]
