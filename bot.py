import configparser
import sys
import time
from collections import Counter
from datetime import datetime

import schedule
from iqoptionapi.stable_api import IQ_Option
from pytz import timezone

from pacotes.escolhe_par import escolhe_par
from pacotes.fucoes.avaliacenario import avalia_cenario
from pacotes.fucoes.retorna_ultimo_loss_hora_diferença import \
    retorna_ultimo_loss_hora_diferença


class Bot:
    def __init__(self, conta='PRACTICE') -> None:

        # Arquivo de configuraçoes
        # arq = configparser.RawConfigParser()
        # arq.read(r'/home/guilherme/bot/config.txt')
        # self.email = arq.get('LOGIN', 'email')
        # self.senha = arq.get('LOGIN', 'senha')

        # Entradas
        # self.valor_entrada = float(arq.get('PARAMETROS', 'valor_entrada'))
        self.valor_entrada = 8
        self.valor_entrada_b = float(self.valor_entrada)
        # Martingales
        # self.martingale = int(arq.get('PARAMETROS', 'martingale'))
        self.martingale = 2
        self.martingale += 1

        # conectando
        self.API = IQ_Option(self.email, self.senha)

        # Real o Demo
        self.conta = conta

        # Controles
        self.lucro = 0
        self.operacoes = 0
        self.par_dict = ''
        self.par_interesse = ''
        self.verifiquei_cores = False

    def login(self):
        self.API.connect()

        self.API.change_balance(self.conta)
        if self.API.check_connect():
            print('Conectado com sucesso!')
            return True
        else:
            print('Erro ao conectar')
            return False

    def stop_gain(self):
        if self.operacoes >= 3:
            print('Stop Gain Batido!')
            return True
        return False

    def Martingale(self, valor, payout):
        lucro_esperado = valor * payout
        perca = float(valor)

        while True:
            if round(valor * payout, 2) > round(abs(perca) + lucro_esperado, 2):
                return round(valor, 2)
                break
            valor += 0.01

    def Payout(self, par):
        self.API.subscribe_strike_list(par, 1)
        while True:
            d = self.API.get_digital_current_profit(par, 1)
            if d != False:
                d = round(int(d) / 100, 2)
                break
            time.sleep(1)
        self.API.unsubscribe_strike_list(par, 1)

        return d

    def operar_mhi(self):
        while True:
            minutos = float(((datetime.now()).strftime('%M.%S'))[1:])
            if (minutos >= 4.4 and minutos <= 4.42):
                self.verifiquei_cores = False
                self.par_dict = escolhe_par(self.API)
                self.par_interesse = self.par_dict[0]

            if (minutos >= 9.4 and minutos <= 9.42):
                self.verifiquei_cores = False
                self.par_dict = escolhe_par(self.API)
                self.par_interesse = self.par_dict[0]

            entrar = True if (minutos >= 4.588 and minutos <=
                              5) or minutos >= 9.588 else False

            if (entrar):
                dir = False

                if (self.par_interesse['pontos'] > 0):

                    cenario = self.par_interesse['cenario']
                    dif = self.par_interesse['dif']
                    hora_ultimo_loss = self.par_interesse['hora_ultimo_loss']
                    pode = self.par_interesse['pode_operar']
                    direcao_desejada = self.par_interesse['direcao_desejada']
                    par = self.par_interesse['par']

                    payout = self.Payout(par)
                    velas_analise = self.API.get_candles(
                        par, 60, 3, time.time())
                    print(
                        f'\nPar escolhido: {par}\nCenario: {cenario}\nDiferença: {dif}\nDireção recomendada: {direcao_desejada}\nHora do Ultimo Loss: {hora_ultimo_loss}')

                    if (self.verifiquei_cores == False):
                        print('\n\nIniciando operação!')
                        print('Verificando cores..', end='')
                        self.verifiquei_cores = True

                        velas_analise[0] = 'g' if velas_analise[0]['open'] < velas_analise[0][
                            'close'] else 'r' if velas_analise[0]['open'] > velas_analise[0]['close'] else 'd'
                        velas_analise[1] = 'g' if velas_analise[1]['open'] < velas_analise[1][
                            'close'] else 'r' if velas_analise[1]['open'] > velas_analise[1]['close'] else 'd'
                        velas_analise[2] = 'g' if velas_analise[2]['open'] < velas_analise[2][
                            'close'] else 'r' if velas_analise[2]['open'] > velas_analise[2]['close'] else 'd'

                        cores = velas_analise[0] + ' ' + \
                            velas_analise[1] + ' ' + velas_analise[2]
                        print(cores)
                        if (pode):
                            if (direcao_desejada == 'PUT'):
                                if cores.count('g') > cores.count('r') and cores.count('d') == 0:
                                    dir = 'put'
                            if (direcao_desejada == 'CALL'):
                                if cores.count('r') > cores.count('g') and cores.count('d') == 0:
                                    dir = 'call'
                        else:
                            print('Nao pode operar')

                        if dir:
                            print(
                                f'Iniciando Operação em {par}: {dir} com {self.valor_entrada}')

                            self.valor_entrada = self.valor_entrada_b
                            for i in range(self.martingale):

                                status, id = self.API.buy_digital_spot(
                                    par, self.valor_entrada, dir, 1)

                                if status:
                                    while True:

                                        status, valor = self.API.check_win_digital_v2(
                                            id)

                                        if status:
                                            valor = valor if valor > 0 else float(
                                                '-' + str(abs(self.valor_entrada)))
                                            self.lucro += round(valor, 2)

                                            print(
                                                'Resultado operação: ', end='')
                                            print('WIN /' if valor > 0 else 'LOSS /', round(valor, 2), '/', round(
                                                self.lucro, 2), ('/ '+str(i) + ' GALE' if i > 0 else ''))

                                            self.valor_entrada = self.Martingale(
                                                self.valor_entrada, payout)
                                            print('rodadas: ', i)

                                            break

                                    if valor > 0:
                                        self.operacoes = self.operacoes + 1
                                        print('operacoes: ', self.operacoes)
                                        gain = self.stop_gain()
                                        if (gain):
                                            return True
                                        break
                                    if (valor < 0 and i == 2):
                                        print('Stop Loss batido!')
                                        return False

                                else:
                                    print('\nERRO AO REALIZAR OPERAÇÃO\n\n')

            time.sleep(0.5)

    def operar_mhi_v2(self, par_interesse: dict):
        while True:
            minutos = float(((datetime.now()).strftime('%M.%S'))[1:])

            entrar = True if (minutos >= 4.58 and minutos <=
                              5) or minutos >= 9.58 else False

            if (entrar):
                dir = False

                if (par_interesse['pontos'] > 0):

                    cenario = par_interesse['cenario']
                    dif = par_interesse['dif']
                    hora_ultimo_loss = par_interesse['hora_ultimo_loss']
                    pode = par_interesse['pode_operar']
                    direcao_desejada = par_interesse['direcao_desejada']
                    par = par_interesse['par']

                    payout = self.Payout(par)
                    velas_analise = self.API.get_candles(
                        par, 60, 3, time.time())
                    print(
                        f'\nPar escolhido: {par}\nCenario: {cenario}\nDiferença: {dif}\nDireção recomendada: {direcao_desejada}\nHora do Ultimo Loss: {hora_ultimo_loss}')

                    if (self.verifiquei_cores == False):
                        print('Verificando cores..', end='')
                        self.verifiquei_cores = True

                        velas_analise[0] = 'g' if velas_analise[0]['open'] < velas_analise[0][
                            'close'] else 'r' if velas_analise[0]['open'] > velas_analise[0]['close'] else 'd'
                        velas_analise[1] = 'g' if velas_analise[1]['open'] < velas_analise[1][
                            'close'] else 'r' if velas_analise[1]['open'] > velas_analise[1]['close'] else 'd'
                        velas_analise[2] = 'g' if velas_analise[2]['open'] < velas_analise[2][
                            'close'] else 'r' if velas_analise[2]['open'] > velas_analise[2]['close'] else 'd'

                        cores = velas_analise[0] + ' ' + \
                            velas_analise[1] + ' ' + velas_analise[2]
                        print(cores)
                        if (pode):
                            if (direcao_desejada == 'PUT'):
                                if cores.count('g') > cores.count('r') and cores.count('d') == 0:
                                    dir = 'put'
                            if (direcao_desejada == 'CALL'):
                                if cores.count('r') > cores.count('g') and cores.count('d') == 0:
                                    dir = 'call'
                        else:
                            print('Nao pode operar')

                        if dir:
                            print(
                                f'Iniciando Operação em {par}: {dir} com {self.valor_entrada_b}')

                            self.valor_entrada = self.valor_entrada_b
                            for i in range(self.martingale):

                                status, id = self.API.buy_digital_spot(
                                    par, self.valor_entrada, dir, 1)

                                if status:
                                    while True:

                                        status, valor = self.API.check_win_digital_v2(
                                            id)

                                        if status:
                                            valor = valor if valor > 0 else float(
                                                '-' + str(abs(self.valor_entrada)))
                                            self.lucro += round(valor, 2)

                                            print(
                                                'Resultado operação: ', end='')
                                            print('WIN /' if valor > 0 else 'LOSS /', round(valor, 2), '/', round(
                                                self.lucro, 2), ('/ '+str(i) + ' GALE' if i > 0 else ''))

                                            self.valor_entrada = self.Martingale(
                                                self.valor_entrada, payout)
                                            print('rodadas: ', i)

                                            break

                                    if valor > 0:
                                        self.operacoes = self.operacoes + 1
                                        print('operacoes: ', self.operacoes)
                                        gain = self.stop_gain()
                                        if (gain):
                                            return True
                                        break
                                    if (valor < 0 and i == 2):
                                        print('Stop Loss batido!')
                                        return False

                                else:
                                    print('\nERRO AO REALIZAR OPERAÇÃO\n\n')

            time.sleep(0.5)

    def realiza_analise_mhi(self, velas,direcao_desejada):
        dir = False
        # ultimo quadrante
        ultimo_quadrante_continuo = False
        ultimo_quadrante = []
        v1 = self.retorna_cor(velas[0])
        v2 = self.retorna_cor(velas[1])
        v3 = self.retorna_cor(velas[2])
        v4 = self.retorna_cor(velas[3])
        v5 = self.retorna_cor(velas[4])
        ultimo_quadrante = [v1, v2, v3, v4, v5]
        qt_r = ultimo_quadrante.count('r')
        qt_g = ultimo_quadrante.count('g')

        if (qt_r > 4 or qt_g > 4):
            ultimo_quadrante_continuo = True


        # Quadrante atual
        vela_1 = self.retorna_cor(velas[5])
        vela_2 = self.retorna_cor(velas[6])
        vela_3 = self.retorna_cor(velas[7])
        vela_4 = self.retorna_cor(velas[8])
        vela_5 = self.retorna_cor(velas[9])

        vls = [vela_1, vela_2, vela_3, vela_4, vela_5]
        qr = vls.count('r')
        qg = vls.count('g')

        print('velas: ', vls)

        if (qg <= 3 and qr <= 3 and ultimo_quadrante_continuo == False):

            analise = vls[2:]

            qtd_r = analise.count('r')
            qtd_g = analise.count('g')
            qtd_d = analise.count('d')

            if (direcao_desejada == 'call'):
                if (qtd_r == 2 and qtd_d == 0):
                    dir = 'call'
            if (direcao_desejada == 'put'):
                if (qtd_g == 2 and qtd_d == 0):
                    dir = 'put'

        return dir

    def retorna_cor(self, vela: dict) -> str:
        cor = ''
        if (vela['open'] < vela['close']):
            cor = 'g'
        if (vela['open'] > vela['close']):
            cor = 'r'
        if (vela['open'] == vela['close']):
            cor = 'd'
        return cor

    def get_velas(self, qtd, par):

        velas_analise = self.API.get_candles(
            par, 60, qtd, time.time())
        return velas_analise

    def operar_mhi_v3(self):
        par = False
        direcao_desejada = False

        while True:
            minutos = float(((datetime.now()).strftime('%M.%S'))[1:])
            if (minutos >= 4.4 and minutos <= 4.42):
                par, direcao_desejada = self.escolhe_par_jpy()
                self.verifiquei_cores = False

            if (minutos >= 9.4 and minutos <= 9.42):
                par, direcao_desejada = self.escolhe_par_jpy()
                self.verifiquei_cores = False

            entrar = True if (minutos >= 4.58 and minutos <=
                              5) or minutos >= 9.58 else False

            if (entrar and par and direcao_desejada):
                print(f'\n\nentrando {par}')
                dir = False

                payout = self.Payout(par)
                velas_analise = self.API.get_candles(
                    par, 60, 10, time.time())

                if (self.verifiquei_cores == False):
                    print('Verificando cores..', end='')

                    self.verifiquei_cores = True

                    dir = self.realiza_analise_mhi(velas_analise, direcao_desejada)

                    if dir:
                        print(
                            f'Iniciando Operação em {par}: {dir} com {self.valor_entrada_b}')

                        self.valor_entrada = self.valor_entrada_b
                        for i in range(self.martingale):

                            status, id = self.API.buy_digital_spot(
                                par, self.valor_entrada, dir, 1)

                            if status:
                                while True:

                                    status, valor = self.API.check_win_digital_v2(
                                        id)

                                    if status:
                                        valor = valor if valor > 0 else float(
                                            '-' + str(abs(self.valor_entrada)))
                                        self.lucro += round(valor, 2)

                                        print(
                                            'Resultado operação: ', end='')
                                        print('WIN /' if valor > 0 else 'LOSS /', round(valor, 2), '/', round(
                                            self.lucro, 2), ('/ '+str(i) + ' GALE' if i > 0 else ''))

                                        self.valor_entrada = self.Martingale(
                                            self.valor_entrada, payout)
                                        print('rodadas: ', i)

                                        break

                                if valor > 0:
                                    self.operacoes = self.operacoes + 1
                                    print('operacoes: ', self.operacoes)
                                    gain = self.stop_gain()
                                    if (gain):
                                        return True
                                    break
                                if (valor < 0 and i == 2):
                                    print('Stop Loss batido!')
                                    return False

                            else:
                                print('\nERRO AO REALIZAR OPERAÇÃO\n\n')

            time.sleep(0.5)

    def logout(self):
        self.API.logout()

    def contar_velas(self, ativo):
        velas = self.API.get_candles(ativo, 60, 60, time.time())
        lista_velas = []
        dir = False
        res = False

        for vela in velas:
            cor = self.retorna_cor(vela)
            lista_velas.append(cor)

        qtd_r = lista_velas.count('r') / (len(lista_velas))  * 100
        qtd_g = lista_velas.count('g') / (len(lista_velas))* 100
        print(f'% verde: {qtd_g}  % vermelho: {qtd_r}')

        if qtd_g > qtd_r:
            res = qtd_g - qtd_r
            dir = 'put'
        else:
            res = qtd_r - qtd_g
            dir = 'call'


        return res, dir




        

    def escolhe_par_jpy(self):
        par = False
        direcao_desejada = False
        recomendado = False

        ativos_digitais_jpy = []
        ativos = self.API.get_all_open_time()

        for digital in ativos['digital']:
            # if (not 'OTC' in digital and 'JPY' in digital):
            if (ativos['digital'][digital]['open'] == True and not 'OTC' in digital and 'JPY' in digital):
                ativos_digitais_jpy.append(digital)

        print(ativos_digitais_jpy)

        if (len(ativos_digitais_jpy) == 0):
            return False, False

        for ativo in ativos_digitais_jpy:
            velas = self.API.get_candles(ativo, 60, 240, time.time())
            cenario, ultimo_loss = avalia_cenario(velas)
            recomendado = retorna_ultimo_loss_hora_diferença(
                ultimo_loss[1], '01:00:00')[0]
            
            
            dif, direcao_desejada = self.contar_velas(ativo)
            print(f'DIF : {dif} DIRECAO_DESEJADA : {direcao_desejada}  ULTIMO_LOSS: {ultimo_loss[1]}')

            if (dif and direcao_desejada):
                if dif > 5:
                    if recomendado:
                        recomendado2 = retorna_ultimo_loss_hora_diferença(
                            ultimo_loss[1], '00:20:00')[0]
                        par = ativo

                        if recomendado2:
                            par = ativo
                            return par, direcao_desejada

        return par, direcao_desejada


def escrever_meia_noite():
    with open("/home/guilherme/bot/pode.txt", "w") as arquivo:
        arquivo.write("sim")


def operar(conta='REAL'):

    with open("/home/guilherme/bot/pode.txt", "r") as arquivo:
        pode = arquivo.read()

    if (pode == 'nao'):
        print('nao vou operar')
        return False

    print('pode operar')
    robo = Bot()
    login = robo.login()
    if login:
        res = robo.operar_mhi_v3()
        robo.logout()
        if (res == False):
            with open("/home/guilherme/bot/pode.txt", "w") as arquivo:
                arquivo.write("nao")


def agendar_tarefa():
    tz = timezone("America/Sao_Paulo")

    schedule.every().day.at("00:00", "America/Sao_Paulo").do(escrever_meia_noite)

    schedule.every().monday.at("03:00", "America/Sao_Paulo").do(operar).tag("minha_tarefa")
    schedule.every().tuesday.at("03:00", "America/Sao_Paulo").do(operar).tag("minha_tarefa")
    schedule.every().wednesday.at(
        "03:00", "America/Sao_Paulo").do(operar).tag("minha_tarefa")
    schedule.every().thursday.at(
        "03:00", "America/Sao_Paulo").do(operar).tag("minha_tarefa")
    schedule.every().friday.at("03:00", "America/Sao_Paulo").do(operar).tag("minha_tarefa")

    schedule.every().monday.at("08:30", "America/Sao_Paulo").do(operar).tag("minha_tarefa")
    schedule.every().tuesday.at("08:30", "America/Sao_Paulo").do(operar).tag("minha_tarefa")
    schedule.every().wednesday.at(
        "08:30", "America/Sao_Paulo").do(operar).tag("minha_tarefa")
    schedule.every().thursday.at(
        "08:30", "America/Sao_Paulo").do(operar).tag("minha_tarefa")
    schedule.every().friday.at("08:30", "America/Sao_Paulo").do(operar).tag("minha_tarefa")


if __name__ == '__main__':

    agendar_tarefa()

    while True:
        schedule.run_pending()
        time.sleep(1)
