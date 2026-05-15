from django.urls import path
from django.shortcuts import redirect
from . import views

urlpatterns = [

    # HOME
    path(
        '',
        views.home,
        name='home'
    ),

    # ======================
    # 1ª DIVISÃO
    # ======================

    path(
        'rodadas/',
        lambda request: redirect(
            'rodada_detalhe',
            rodada_num=1
        ),
        name='rodadas'
    ),

    path(
        'rodadas/<int:rodada_num>/',
        views.rodadas,
        name='rodada_detalhe'
    ),

    path(
        'classificacao/',
        views.classificacao,
        name='classificacao'
    ),

    path(
        'matamata/',
        views.matamata,
        name='matamata'
    ),

    # ======================
    # 2ª DIVISÃO
    # ======================

    path(
        'segunda-divisao/',
        lambda request: redirect(
            'segunda_divisao_rodada',
            rodada_num=1
        ),
        name='segunda_divisao'
    ),

    path(
        'segunda-divisao/<int:rodada_num>/',
        views.segunda_divisao,
        name='segunda_divisao_rodada'
    ),

    # ======================
    # NOTÍCIAS
    # ======================

    path(
        'noticias/',
        views.noticias,
        name='noticias'
    ),

    path(
    'gerar-confrontos/',
    views.gerar_confrontos_primeira,
    name='gerar_confrontos'
),

path(
    'gerar-confrontos-segunda/',
    views.gerar_confrontos_segunda,
    name='gerar_confrontos_segunda'
),

path(
    'jogo/<int:jogo_id>/',
    views.detalhe_jogo,
    name='detalhe_jogo'
),

path(
    'jogo/<int:jogo_id>/simular/',
    views.simular_partida,
    name='simular_partida'
),

path(
    'gerar-jogadores/',
    views.gerar_jogadores,
    name='gerar_jogadores'
),
]