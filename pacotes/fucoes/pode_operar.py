def pode_operar(cenario, dif, hora_ultimo_loss, ativo):
    
    if (ativo == 'EURGBP'):
        dif = dif/3
    if (ativo == 'EURUSD'):
        dif = dif/2
    if (ativo == 'GBPUSD'):
        dif = dif/3
    if (ativo == 'USDCAD'):
        dif = dif/2
    if (ativo == 'AUDCAD'): # USDCHF
        dif = dif/3
    if (ativo == 'USDCHF'): # USDCHF
        dif = dif/3
    if (ativo == 'AUDUSD'): # USDCHF
        dif = dif/2
    if (ativo == 'USOUSD'): # USDCHF
        dif = dif/5

    #print(dif, ativo)
    if(cenario):
        if(dif > 5):
            if(hora_ultimo_loss[0] == True):
                return True
    return False