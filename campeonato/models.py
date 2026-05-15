from django.db import models


class Time(models.Model):
    DIVISOES = [
        ('1', 'Primeira Divisão'),
        ('2', 'Segunda Divisão'),
    ]

    nome = models.CharField(max_length=100)
    grupo = models.CharField(max_length=1, blank=True, null=True)
    divisao = models.CharField(max_length=1, choices=DIVISOES, default='1')

    logo = models.ImageField(
        upload_to='logos/',
        blank=True,
        null=True
    )

    ataque = models.IntegerField(default=50)
    meio_campo = models.IntegerField(default=50)
    defesa = models.IntegerField(default=50)

    def forca_geral(self):
        return int((self.ataque + self.meio_campo + self.defesa) / 3)

    def __str__(self):
        return self.nome


class Jogador(models.Model):
    POSICOES = [
        ('GOL', 'Goleiro'),
        ('DEF', 'Defensor'),
        ('MEI', 'Meio-campista'),
        ('ATA', 'Atacante'),
    ]

    nome = models.CharField(max_length=100)
    time = models.ForeignKey(Time, on_delete=models.CASCADE)
    posicao = models.CharField(max_length=3, choices=POSICOES)
    forca = models.IntegerField(default=50)

    gols = models.IntegerField(default=0)
    assistencias = models.IntegerField(default=0)
    cartoes_amarelos = models.IntegerField(default=0)
    cartoes_vermelhos = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.nome} - {self.time.nome}"


class Jogo(models.Model):
    DIVISOES = [
        ('1', 'Primeira Divisão'),
        ('2', 'Segunda Divisão'),
    ]

    rodada = models.IntegerField()
    mandante = models.ForeignKey(
        Time,
        on_delete=models.CASCADE,
        related_name='jogos_casa'
    )
    visitante = models.ForeignKey(
        Time,
        on_delete=models.CASCADE,
        related_name='jogos_fora'
    )

    gols_mandante = models.IntegerField(null=True, blank=True)
    gols_visitante = models.IntegerField(null=True, blank=True)

    divisao = models.CharField(max_length=1, choices=DIVISOES, default='1')

    def __str__(self):
        return f"Rodada {self.rodada}: {self.mandante} x {self.visitante}"


class EstatisticaPartida(models.Model):
    jogo = models.OneToOneField(
        Jogo,
        on_delete=models.CASCADE,
        related_name='estatisticas'
    )

    posse_mandante = models.IntegerField(default=50)
    posse_visitante = models.IntegerField(default=50)

    finalizacoes_mandante = models.IntegerField(default=0)
    finalizacoes_visitante = models.IntegerField(default=0)

    finalizacoes_gol_mandante = models.IntegerField(default=0)
    finalizacoes_gol_visitante = models.IntegerField(default=0)

    escanteios_mandante = models.IntegerField(default=0)
    escanteios_visitante = models.IntegerField(default=0)

    faltas_mandante = models.IntegerField(default=0)
    faltas_visitante = models.IntegerField(default=0)

    amarelos_mandante = models.IntegerField(default=0)
    amarelos_visitante = models.IntegerField(default=0)

    vermelhos_mandante = models.IntegerField(default=0)
    vermelhos_visitante = models.IntegerField(default=0)

    penaltis_mandante = models.IntegerField(default=0)
    penaltis_visitante = models.IntegerField(default=0)

    def __str__(self):
        return f"Estatísticas - {self.jogo}"


class EventoPartida(models.Model):
    jogo = models.ForeignKey(Jogo, on_delete=models.CASCADE)
    minuto = models.IntegerField()
    tipo = models.CharField(max_length=50)
    descricao = models.CharField(max_length=250)

    jogador = models.ForeignKey(
        Jogador,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.minuto}' - {self.descricao}"


class JogoMataMata(models.Model):
    fase = models.CharField(max_length=50)

    mandante = models.CharField(max_length=100)
    visitante = models.CharField(max_length=100)

    gols_mandante = models.IntegerField(null=True, blank=True)
    gols_visitante = models.IntegerField(null=True, blank=True)

    jogo_numero = models.IntegerField(default=1)

    def vencedor(self):
        if self.gols_mandante is None or self.gols_visitante is None:
            return None

        if self.gols_mandante > self.gols_visitante:
            return self.mandante

        if self.gols_visitante > self.gols_mandante:
            return self.visitante

        return "Empate"

    def __str__(self):
        return f"{self.fase}: {self.mandante} x {self.visitante}"