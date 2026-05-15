from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('rodadas/', views.rodadas, name='rodadas'),
    path('segunda-divisao/', views.segunda_divisao, name='segunda_divisao'),
    path('classificacao/', views.classificacao, name='classificacao'),
    path('matamata/', views.matamata, name='matamata'),
    path('noticias/', views.noticias, name='noticias'),
]