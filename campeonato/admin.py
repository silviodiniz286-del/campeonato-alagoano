from django.contrib import admin
from .models import Time, Jogador, Jogo, EstatisticaPartida, EventoPartida, JogoMataMata


admin.site.register(Time)
admin.site.register(Jogador)
admin.site.register(Jogo)
admin.site.register(EstatisticaPartida)
admin.site.register(EventoPartida)
admin.site.register(JogoMataMata)