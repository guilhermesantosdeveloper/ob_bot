from datetime import datetime

from pytz import timezone


def resultado(operacao):

    vela1 = operacao[0][0]
    vela2 = operacao[1][0]
    vela3 = operacao[2][0]
    vela4 = operacao[3][0]
    vela5 = operacao[4][0]
    vela6 = operacao[5][0]

    #print(vela1, vela2, vela3, vela4, vela5, vela6)
    analise = []
    analise.append(vela1)
    analise.append(vela2)
    analise.append(vela3)

    direcao = None


    if analise.count('d'):
        return 'tem doji', direcao

    if (analise.count('g') > analise.count('r')):
        direcao = 'put'
        if vela4 == 'r':
            return 'win', direcao
        if vela5 == 'r':
            return 'win 1 gale', direcao
        if vela6 == 'r':
            return 'win 2 gale', direcao
        return 'loss', direcao
        

    if (analise.count('g') < analise.count('r')):
        direcao = 'call'
        if vela4 == 'g':
            return 'win', direcao
        if vela5 == 'g':
            return 'win 1 gale', direcao
        if vela6 == 'g':
            return 'win 2 gale', direcao
        return 'loss', direcao
    



def operaceos_passadas(velas):

    operacoes = []
    nova_operacao = []
    outra_operacao = []
    for item in velas:

        val = 'g' if item['open'] < item['close'] else 'r'

        if (item['open'] == item['close']):
            val = 'd'

        timestamp = item['from']
        dt = datetime.fromtimestamp(timestamp, tz = timezone("America/Sao_Paulo"))
        min = dt.strftime("%M")
        dt = dt.strftime("%d/%m/%Y %H:%M:%S")

        
        if (min[1] == '2'):
            nova_operacao.append((val,dt))

        if (len(nova_operacao) >= 1):
    
                    
            if (min[1] == '3' or min[1] == '4' or min[1] == '5' or min[1] == '6' or min[1] == '7'):
                    nova_operacao.append((val,dt))

        if (len(nova_operacao) == 6):
            res = resultado(nova_operacao)
            operacoes.append((nova_operacao, res))
            nova_operacao = []



        if (min[1] == '7'):
            outra_operacao.append((val,dt))


        if (len(outra_operacao) >= 1):
    
                    
            if (min[1] == '8' or min[1] == '9' or min[1] == '0' or min[1] == '1' or (min[1] == '2' and len(outra_operacao)==5)):
                    outra_operacao.append((val,dt))

        if (len(outra_operacao) == 6):
            res = resultado(outra_operacao)
            operacoes.append((outra_operacao, res))
            
            outra_operacao = []




    


            
        #print(val, dt, len(velas), min[1]) 

    # criar lista de dicionarios

    ops = []
    for n in operacoes:
        result = n[1][0]
        dir = n[1][1]
        velas = f"{n[0][0][0]},{n[0][1][0]},{n[0][2][0]},{n[0][3][0]},{n[0][4][0]},{n[0][5][0]}"
        inicio_em = n[0][0][1]
        termino_em = n[0][5][1]

        op = {
            "resultado": result,
            "direcao": dir,
            "inicio_em": inicio_em,
            "termino_em": termino_em,
            "velas": velas
        }
        
        ops.append(op)
    
    return ops


def avalia_cenario(velas):

    ops = operaceos_passadas(velas)
    qtd_loss = []


    for op in ops:
        if(op['resultado'] == 'loss'):
            qtd_loss.append((op['resultado'], op['termino_em'], op['direcao']))



    cenario = ''
    #print(len(qtd_loss))
    if(len(qtd_loss) >= 6):
        cenario = 'EXCELENTE'
    if(len(qtd_loss) >= 3 and len(qtd_loss) <= 5):
        cenario = 'BOM'
    if(len(qtd_loss) >= 1 and len(qtd_loss) < 3):
        cenario = 'RUIM'
    if(len(qtd_loss) == 0):
        cenario = 'PESSIMO'

    if (len(qtd_loss) == 0):
        return cenario,('loss', '13/06/2023 00:00:00', 'call')

    return cenario,qtd_loss[len(qtd_loss)-1]



def retorna_tempo_recomendado(cenario,ativo):
    tempo_recomendado = None


    if (cenario == 'EXCELENTE'):
        tempo_recomendado = '01:20:00'
    if (cenario == 'BOM'):
        tempo_recomendado = '01:00:00'
    if (cenario == 'RUIM'):
        tempo_recomendado = '00:45:00'
    if (cenario == 'PESSIMO'):
        tempo_recomendado = '00:45:00'

    if (ativo == 'USDCAD'):
        tempo_recomendado = '00:10:00'
    
    if (ativo == 'EURGBP'):
        tempo_recomendado = '00:10:00'

    if (ativo == 'AUDUSD'):
        tempo_recomendado = '00:10:00'
    
    if (ativo == 'GBPUSD'):
        tempo_recomendado = '00:10:00'

    if (ativo == 'AUDCAD'):
        tempo_recomendado = '00:10:00'

    if (ativo == 'EURUSD'):
        tempo_recomendado = '00:30:00'

    if (ativo == 'USDCHF'):
        tempo_recomendado = '00:10:00'
    if (ativo == 'USOUSD'):
        tempo_recomendado = '00:01:00'


    return tempo_recomendado


