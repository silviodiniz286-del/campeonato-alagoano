from . import views
import random
from django.shortcuts import render, redirect, get_object_or_404

from .models import (
    Time,
    Jogador,
    Jogo,
    JogoMataMata,
    EventoPartida,
    EstatisticaPartida
)


def home(request):
    return render(request, 'campeonato/home.html', {
        'total_times': Time.objects.count(),
        'total_jogos': Jogo.objects.count(),
        'jogos_finalizados': Jogo.objects.filter(
            gols_mandante__isnull=False,
            gols_visitante__isnull=False
        ).count(),
    })


def calcular_classificacao(times, jogos=None):
    if jogos is None:
        jogos = Jogo.objects.all()

    tabela = []

    for time in times:
        pontos = jogos_jogados = vitorias = empates = derrotas = 0
        gols_pro = gols_contra = 0

        for jogo in jogos:
            if jogo.gols_mandante is None or jogo.gols_visitante is None:
                continue

            if jogo.mandante == time:
                gp = jogo.gols_mandante
                gc = jogo.gols_visitante
            elif jogo.visitante == time:
                gp = jogo.gols_visitante
                gc = jogo.gols_mandante
            else:
                continue

            jogos_jogados += 1
            gols_pro += gp
            gols_contra += gc

            if gp > gc:
                pontos += 3
                vitorias += 1
            elif gp == gc:
                pontos += 1
                empates += 1
            else:
                derrotas += 1

        tabela.append({
            'time': time,
            'pontos': pontos,
            'jogos': jogos_jogados,
            'vitorias': vitorias,
            'empates': empates,
            'derrotas': derrotas,
            'gols_pro': gols_pro,
            'gols_contra': gols_contra,
            'saldo': gols_pro - gols_contra,
        })

    return sorted(
        tabela,
        key=lambda item: (
            item['pontos'],
            item['vitorias'],
            item['saldo'],
            item['gols_pro']
        ),
        reverse=True
    )


def rodadas(request, rodada_num=1):
    if request.method == 'POST':
        for jogo in Jogo.objects.filter(divisao='1', rodada=rodada_num):
            gm = request.POST.get(f'gols_mandante_{jogo.id}', '')
            gv = request.POST.get(f'gols_visitante_{jogo.id}', '')

            if gm != '' and gv != '':
                jogo.gols_mandante = int(gm)
                jogo.gols_visitante = int(gv)
                jogo.save()

        return redirect('rodada_detalhe', rodada_num=rodada_num)

    jogos = Jogo.objects.filter(
        divisao='1',
        rodada=rodada_num
    ).order_by('id')

    return render(request, 'campeonato/rodadas.html', {
        'rodadas_lista': range(1, 13),
        'jogos': jogos,
        'rodada_atual': rodada_num,
    })


def segunda_divisao(request, rodada_num=1):
    if request.method == 'POST':
        for jogo in Jogo.objects.filter(divisao='2', rodada=rodada_num):
            gm = request.POST.get(f'gols_mandante_{jogo.id}', '')
            gv = request.POST.get(f'gols_visitante_{jogo.id}', '')

            if gm != '' and gv != '':
                jogo.gols_mandante = int(gm)
                jogo.gols_visitante = int(gv)
                jogo.save()

        return redirect('segunda_divisao_rodada', rodada_num=rodada_num)

    jogos_segunda = Jogo.objects.filter(divisao='2')

    tabela = calcular_classificacao(
        Time.objects.filter(divisao='2'),
        jogos_segunda
    )

    jogos = Jogo.objects.filter(
        divisao='2',
        rodada=rodada_num
    ).order_by('id')

    return render(request, 'campeonato/segunda_divisao.html', {
        'tabela': tabela,
        'jogos': jogos,
        'rodadas_lista': range(1, 15),
        'rodada_atual': rodada_num,
    })


def classificacao(request):
    jogos_primeira = Jogo.objects.filter(divisao='1')

    grupos = {
        'A': calcular_classificacao(Time.objects.filter(grupo='A', divisao='1'), jogos_primeira),
        'B': calcular_classificacao(Time.objects.filter(grupo='B', divisao='1'), jogos_primeira),
        'C': calcular_classificacao(Time.objects.filter(grupo='C', divisao='1'), jogos_primeira),
        'D': calcular_classificacao(Time.objects.filter(grupo='D', divisao='1'), jogos_primeira),
    }

    geral = calcular_classificacao(
        Time.objects.filter(divisao='1'),
        jogos_primeira
    )

    rebaixados = geral[-2:]

    return render(request, 'campeonato/classificacao.html', {
        'grupos': grupos,
        'geral': geral,
        'rebaixados': rebaixados,
    })


def gerar_confrontos_primeira(request):
    Jogo.objects.filter(divisao='1').delete()
    JogoMataMata.objects.all().delete()

    grupos = {
        'A': list(Time.objects.filter(grupo='A', divisao='1')),
        'B': list(Time.objects.filter(grupo='B', divisao='1')),
        'C': list(Time.objects.filter(grupo='C', divisao='1')),
        'D': list(Time.objects.filter(grupo='D', divisao='1')),
    }

    for grupo in grupos:
        random.shuffle(grupos[grupo])

    rodadas = [[] for _ in range(12)]

    pares_grupos = [
        ('A', 'B'), ('C', 'D'),
        ('A', 'C'), ('B', 'D'),
        ('A', 'D'), ('B', 'C'),
    ]

    rodada_base = 0

    for i in range(0, len(pares_grupos), 2):
        par1 = pares_grupos[i]
        par2 = pares_grupos[i + 1]

        for r in range(4):
            for g1, g2 in [par1, par2]:
                times1 = grupos[g1]
                times2 = grupos[g2]

                for pos in range(4):
                    t1 = times1[pos]
                    t2 = times2[(pos + r) % 4]

                    if (rodada_base + r + pos) % 2 == 0:
                        rodadas[rodada_base + r].append((t1, t2))
                    else:
                        rodadas[rodada_base + r].append((t2, t1))

        rodada_base += 4

    ordem = list(range(12))
    random.shuffle(ordem)

    for nova_rodada, indice in enumerate(ordem, start=1):
        jogos = rodadas[indice]
        random.shuffle(jogos)

        for mandante, visitante in jogos:
            Jogo.objects.create(
                rodada=nova_rodada,
                mandante=mandante,
                visitante=visitante,
                divisao='1'
            )

    return redirect('rodadas')


def gerar_confrontos_segunda(request):
    Jogo.objects.filter(divisao='2').delete()

    times = list(Time.objects.filter(divisao='2'))
    random.shuffle(times)

    if len(times) % 2 != 0:
        return redirect('segunda_divisao')

    n = len(times)
    metade = n // 2
    rodadas_ida = []
    lista = times[:]

    for rodada in range(n - 1):
        jogos_rodada = []

        for i in range(metade):
            time1 = lista[i]
            time2 = lista[n - 1 - i]

            if rodada % 2 == 0:
                jogos_rodada.append((time1, time2))
            else:
                jogos_rodada.append((time2, time1))

        rodadas_ida.append(jogos_rodada)
        lista = [lista[0]] + [lista[-1]] + lista[1:-1]

    rodada_num = 1

    for jogos in rodadas_ida:
        random.shuffle(jogos)

        for mandante, visitante in jogos:
            Jogo.objects.create(
                rodada=rodada_num,
                mandante=mandante,
                visitante=visitante,
                divisao='2'
            )

        rodada_num += 1

    for jogos in rodadas_ida:
        jogos_volta = []

        for mandante, visitante in jogos:
            jogos_volta.append((visitante, mandante))

        random.shuffle(jogos_volta)

        for mandante, visitante in jogos_volta:
            Jogo.objects.create(
                rodada=rodada_num,
                mandante=mandante,
                visitante=visitante,
                divisao='2'
            )

        rodada_num += 1

    return redirect('segunda_divisao')


def escolher_jogador(time, posicoes=None):
    jogadores = Jogador.objects.filter(time=time)

    if posicoes:
        jogadores = jogadores.filter(posicao__in=posicoes)

    jogadores = list(jogadores)

    if jogadores:
        return random.choice(jogadores)

    return None


def simular_partida(request, jogo_id):
    jogo = get_object_or_404(Jogo, id=jogo_id)

    EventoPartida.objects.filter(jogo=jogo).delete()

    estatistica, criado = EstatisticaPartida.objects.get_or_create(jogo=jogo)

    gols_mandante = 0
    gols_visitante = 0

    forca_mandante = jogo.mandante.forca_geral() + 5
    forca_visitante = jogo.visitante.forca_geral()

    total_forca = forca_mandante + forca_visitante

    posse_mandante = int((forca_mandante / total_forca) * 100)
    posse_visitante = 100 - posse_mandante

    estatistica.posse_mandante = posse_mandante
    estatistica.posse_visitante = posse_visitante

    estatistica.finalizacoes_mandante = 0
    estatistica.finalizacoes_visitante = 0
    estatistica.finalizacoes_gol_mandante = 0
    estatistica.finalizacoes_gol_visitante = 0
    estatistica.escanteios_mandante = 0
    estatistica.escanteios_visitante = 0
    estatistica.faltas_mandante = 0
    estatistica.faltas_visitante = 0
    estatistica.amarelos_mandante = 0
    estatistica.amarelos_visitante = 0
    estatistica.vermelhos_mandante = 0
    estatistica.vermelhos_visitante = 0
    estatistica.penaltis_mandante = 0
    estatistica.penaltis_visitante = 0

    for minuto in range(1, 91):
        chance = random.randint(1, 100)

        lado = random.choices(
            ['mandante', 'visitante'],
            weights=[forca_mandante, forca_visitante],
            k=1
        )[0]

        if chance <= 9:
            if lado == 'mandante':
                estatistica.finalizacoes_mandante += 1
                time = jogo.mandante
            else:
                estatistica.finalizacoes_visitante += 1
                time = jogo.visitante

            EventoPartida.objects.create(
                jogo=jogo,
                minuto=minuto,
                tipo='chance',
                descricao=f"🔥 Chance perigosa para o {time.nome}!"
            )

        elif chance <= 13:
            if lado == 'mandante':
                estatistica.finalizacoes_mandante += 1
                estatistica.finalizacoes_gol_mandante += 1
                atacante = escolher_jogador(jogo.mandante, ['ATA', 'MEI'])
                gols_mandante += 1
                time = jogo.mandante
            else:
                estatistica.finalizacoes_visitante += 1
                estatistica.finalizacoes_gol_visitante += 1
                atacante = escolher_jogador(jogo.visitante, ['ATA', 'MEI'])
                gols_visitante += 1
                time = jogo.visitante

            if atacante:
                atacante.gols += 1
                atacante.save()
                nome = atacante.nome
            else:
                nome = time.nome

            EventoPartida.objects.create(
                jogo=jogo,
                minuto=minuto,
                tipo='gol',
                descricao=f"⚽ GOOOL! {nome} marca para o {time.nome}!",
                jogador=atacante
            )

        elif chance <= 17:
            time_penalti = jogo.mandante if lado == 'mandante' else jogo.visitante
            batedor = escolher_jogador(time_penalti, ['ATA', 'MEI'])

            if lado == 'mandante':
                estatistica.penaltis_mandante += 1
            else:
                estatistica.penaltis_visitante += 1

            EventoPartida.objects.create(
                jogo=jogo,
                minuto=minuto,
                tipo='penalti',
                descricao=f"🥅 PÊNALTI para o {time_penalti.nome}!"
            )

            fez = random.choice([True, False, True])

            if fez:
                if lado == 'mandante':
                    gols_mandante += 1
                    estatistica.finalizacoes_gol_mandante += 1
                else:
                    gols_visitante += 1
                    estatistica.finalizacoes_gol_visitante += 1

                if batedor:
                    batedor.gols += 1
                    batedor.save()
                    nome = batedor.nome
                else:
                    nome = time_penalti.nome

                EventoPartida.objects.create(
                    jogo=jogo,
                    minuto=minuto,
                    tipo='gol',
                    descricao=f"⚽ {nome} cobra o pênalti e marca!",
                    jogador=batedor
                )
            else:
                EventoPartida.objects.create(
                    jogo=jogo,
                    minuto=minuto,
                    tipo='penalti_perdido',
                    descricao=f"🧤 Pênalti perdido pelo {time_penalti.nome}!"
                )

        elif chance <= 23:
            if lado == 'mandante':
                estatistica.faltas_mandante += 1
                estatistica.amarelos_mandante += 1
                time_cartao = jogo.mandante
            else:
                estatistica.faltas_visitante += 1
                estatistica.amarelos_visitante += 1
                time_cartao = jogo.visitante

            jogador = escolher_jogador(time_cartao)

            if jogador:
                jogador.cartoes_amarelos += 1
                jogador.save()
                nome = jogador.nome
            else:
                nome = time_cartao.nome

            EventoPartida.objects.create(
                jogo=jogo,
                minuto=minuto,
                tipo='cartao',
                descricao=f"🟨 Cartão amarelo para {nome} do {time_cartao.nome}",
                jogador=jogador
            )

        elif chance <= 25:
            if lado == 'mandante':
                estatistica.escanteios_mandante += 1
                time = jogo.mandante
            else:
                estatistica.escanteios_visitante += 1
                time = jogo.visitante

            EventoPartida.objects.create(
                jogo=jogo,
                minuto=minuto,
                tipo='escanteio',
                descricao=f"🚩 Escanteio para o {time.nome}"
            )

    jogo.gols_mandante = gols_mandante
    jogo.gols_visitante = gols_visitante
    jogo.save()

    estatistica.save()

    EventoPartida.objects.create(
        jogo=jogo,
        minuto=90,
        tipo='fim',
        descricao="🏁 Fim de jogo!"
    )

    return redirect('detalhe_jogo', jogo_id=jogo.id)


def detalhe_jogo(request, jogo_id):
    jogo = get_object_or_404(Jogo, id=jogo_id)

    eventos = EventoPartida.objects.filter(
        jogo=jogo
    ).order_by('minuto')

    estatistica = EstatisticaPartida.objects.filter(
        jogo=jogo
    ).first()

    return render(request, 'campeonato/detalhe_jogo.html', {
        'jogo': jogo,
        'eventos': eventos,
        'estatistica': estatistica,
    })


def criar_quartas_pela_classificacao():
    jogos_primeira = Jogo.objects.filter(divisao='1')

    grupos = {
        'A': calcular_classificacao(Time.objects.filter(grupo='A', divisao='1'), jogos_primeira),
        'B': calcular_classificacao(Time.objects.filter(grupo='B', divisao='1'), jogos_primeira),
        'C': calcular_classificacao(Time.objects.filter(grupo='C', divisao='1'), jogos_primeira),
        'D': calcular_classificacao(Time.objects.filter(grupo='D', divisao='1'), jogos_primeira),
    }

    JogoMataMata.objects.all().delete()

    if all(len(grupos[g]) >= 2 for g in ['A', 'B', 'C', 'D']):
        quartas = [
            (grupos['A'][0], grupos['A'][1]),
            (grupos['B'][0], grupos['B'][1]),
            (grupos['C'][0], grupos['C'][1]),
            (grupos['D'][0], grupos['D'][1]),
        ]

        for i, jogo in enumerate(quartas, start=1):
            JogoMataMata.objects.create(
                fase='Quartas',
                mandante=jogo[0]['time'].nome,
                visitante=jogo[1]['time'].nome,
                jogo_numero=i
            )


def matamata(request):
    if request.method == 'POST':
        acao = request.POST.get('acao', '')

        if acao == 'atualizar_mata_mata':
            criar_quartas_pela_classificacao()
            return redirect('matamata')

        for jogo in JogoMataMata.objects.all():
            gm = request.POST.get(f'gols_mandante_{jogo.id}', '')
            gv = request.POST.get(f'gols_visitante_{jogo.id}', '')

            if gm != '' and gv != '':
                jogo.gols_mandante = int(gm)
                jogo.gols_visitante = int(gv)
                jogo.save()

        return redirect('matamata')

    return render(request, 'campeonato/matamata.html', {
        'quartas': JogoMataMata.objects.filter(fase='Quartas').order_by('jogo_numero'),
        'semifinais': JogoMataMata.objects.filter(fase='Semifinal').order_by('jogo_numero'),
        'final': JogoMataMata.objects.filter(fase='Final').order_by('jogo_numero'),
    })


def noticias(request):
    jogos = Jogo.objects.filter(
        gols_mandante__isnull=False,
        gols_visitante__isnull=False
    ).order_by('-rodada')

    noticias_lista = []

    for jogo in jogos:
        if jogo.gols_mandante > jogo.gols_visitante:
            titulo = f"{jogo.mandante.nome} vence {jogo.visitante.nome}"
            texto = f"{jogo.mandante.nome} derrotou {jogo.visitante.nome} por {jogo.gols_mandante} x {jogo.gols_visitante} pela rodada {jogo.rodada}."
        elif jogo.gols_visitante > jogo.gols_mandante:
            titulo = f"{jogo.visitante.nome} vence {jogo.mandante.nome}"
            texto = f"{jogo.visitante.nome} bateu {jogo.mandante.nome} por {jogo.gols_visitante} x {jogo.gols_mandante} pela rodada {jogo.rodada}."
        else:
            titulo = f"{jogo.mandante.nome} e {jogo.visitante.nome} empatam"
            texto = f"{jogo.mandante.nome} e {jogo.visitante.nome} empataram em {jogo.gols_mandante} x {jogo.gols_visitante} pela rodada {jogo.rodada}."

        noticias_lista.append({
            'titulo': titulo,
            'texto': texto,
            'rodada': jogo.rodada,
        })

    return render(request, 'campeonato/noticias.html', {
        'noticias': noticias_lista
    })

def gerar_jogadores(request):
    
    nomes = [
        "João", "Pedro", "Lucas", "Gabriel", "Carlos",
        "Mateus", "Rafael", "Felipe", "Bruno", "André",
        "Caio", "Gustavo", "Thiago", "Diego", "Vinicius",
        "Rodrigo", "Henrique", "Paulo", "Daniel", 
    "Marcos",
        "Eduardo", "Leonardo", "Fernando", "Alex", 
    "Roberto",
        "Cristiano", "Wesley", "Murilo", "Nathan", 
    "Samuel"
    ]

    sobrenomes = [
        "Silva", "Souza", "Oliveira", "Santos", "Costa",
        "Pereira", "Rodrigues", "Almeida", "Nascimento",
        "Lima", "Araújo", "Fernandes", "Gomes", "Martins",
        "Barbosa", "Melo", "Freitas", "Carvalho"
    ]

    Jogador.objects.all().delete()

    for time in Time.objects.all():

        elenco = []

        # 3 goleiros
        elenco += ['GOL'] * 3

        # 8 defensores
        elenco += ['DEF'] * 8

        # 9 meio-campistas
        elenco += ['MEI'] * 9

        # 10 atacantes
        elenco += ['ATA'] * 10

        random.shuffle(elenco)

        for posicao in elenco[:30]:

            nome = (
                random.choice(nomes)
                + ' ' +
                random.choice(sobrenomes)
            )

            Jogador.objects.create(
                nome=nome,
                time=time,
                posicao=posicao,
                forca=random.randint(45, 95)
            )

            return redirect('/admin/')