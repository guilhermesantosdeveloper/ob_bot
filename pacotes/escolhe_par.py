import sys
import time
from datetime import datetime

from iqoptionapi.stable_api import IQ_Option
from pytz import timezone

from pacotes.fucoes.avaliacenario import (avalia_cenario,
                                          retorna_tempo_recomendado)
from pacotes.fucoes.pode_operar import pode_operar
from pacotes.fucoes.porcentagemdevelas import porcentagem_velas
from pacotes.fucoes.retorna_ultimo_loss_hora_diferença import \
    retorna_ultimo_loss_hora_diferença


def encontrar_maior_pontuacao(lista):
    maior_pontuacao = max(lista, key=lambda x: x['pontos'])
    return maior_pontuacao

def ordenar_por_pontos(lista):
    lista_ordenada = sorted(lista, key=lambda x: x['pontos'], reverse=True)
    return lista_ordenada

def escolhe_par(API):
    ativos_digitais = []
    ativos = API.get_all_open_time()
    for digital in ativos['digital']:
        if (ativos['digital'][digital]['open'] == True and not 'OTC' in digital):
            ativos_digitais.append({'par': digital, 'pontos': 0})
            



    # cenario: excelente = 4pts,bom = 3pts, ruim = 2pts, pessimo = 1pts
    # dif: >5 = 1pt   >10 = 2pt  >15 = 3pt >20 = 4pt
    # 'JPY' in ativo = 4pt

    #print(ativos_digitais)
    for at in ativos_digitais:
        ponts = 0
        pts = at['pontos']
        ativo = at['par']
        #print(ativo)
        velas = API.get_candles(ativo, 60,240, time.time())
        porcentagem_vermelhas, porcentagem_verdes, porcentagem_dojis = porcentagem_velas(velas)
        cenario, ultimo_loss = avalia_cenario(velas)
        tempo_desde_ultimo_loss = retorna_tempo_recomendado(cenario, ativo)
        hora_ultimo_loss = retorna_ultimo_loss_hora_diferença(ultimo_loss[1], tempo_desde_ultimo_loss)
        # decide a direçao 
        dif = 0
        direcao_desejada = ''
        operar_maioria = False

        if (porcentagem_vermelhas > porcentagem_verdes):
            dif = (porcentagem_vermelhas - porcentagem_verdes).__round__(2)
            direcao_desejada = 'CALL'

        if (porcentagem_verdes > porcentagem_vermelhas):
            dif = (porcentagem_verdes - porcentagem_vermelhas).__round__(2)
            direcao_desejada = 'PUT'

        pode = pode_operar(cenario,dif,hora_ultimo_loss, ativo)

        #print('\nAnalisando o atSivo: ', {'par': ativo, 'pontos': pts, 'direcao_desejada': direcao_desejada,'cenario': cenario,'hora_ultimo_loss': hora_ultimo_loss[1],'dentro_do_prazo': hora_ultimo_loss[0],'dif': dif,'pode_operar': pode,'tempo_recomendado': tempo_desde_ultimo_loss,'operar_maioria': operar_maioria})
        
        if(pode):
           #print(ativo)
            if(cenario == 'EXCELENTE'):
                ponts += 3
            if(cenario == 'BOM'):
                ponts += 3
            if(cenario == 'RUIM'):
                ponts += 3
            if(cenario == 'PESSIMO'):
                ponts += 3

            if 'JPY' in ativo:
                ponts += 4
            
            ponts += float(dif)

            if (dif >= 20):
                ponts += 5
                operar_maioria = True
            
            at.update({'pontos': ponts})
            at.update({
                'direcao_desejada': direcao_desejada,
                'cenario': cenario,
                'hora_ultimo_loss': hora_ultimo_loss[1],
                'dentro_do_prazo': hora_ultimo_loss[0],
                'dif': dif,
                'pode_operar': pode,
                'tempo_recomendado': tempo_desde_ultimo_loss,
                'operar_maioria': operar_maioria
                    })



    #print(ativos_digitais)
    #maior = encontrar_maior_pontuacao(ativos_digitais)
    lista_ordenada = ordenar_por_pontos(ativos_digitais)
    return lista_ordenada




