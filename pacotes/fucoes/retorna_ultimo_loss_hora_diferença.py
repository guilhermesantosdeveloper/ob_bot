from datetime import datetime, timedelta


def string_para_hora(string):
    formato = '%d/%m/%Y %H:%M:%S'
    data_hora = datetime.strptime(string, formato)
    hora = data_hora.time()
    return hora


def string_para_hora2(string):
    formato = '%H:%M:%S'
    data_hora = datetime.strptime(string, formato)
    hora = data_hora.time()
    return hora



def subtrair_tempos(tempo1, tempo2):
    # Obter a data atual para combinar com os tempos
    data_atual = datetime.now().date()



    # Criar objetos datetime para realizar a subtração
    dt1 = datetime.combine(data_atual, tempo1)
    dt2 = datetime.combine(data_atual, tempo2)

    # Realizar a subtração dos tempos
    diff = dt1 - dt2


   

    # Converter a diferença em um formato legível
    horas = diff.seconds // 3600
    minutos = (diff.seconds // 60) % 60
    segundos = diff.seconds % 60

    resultado = f"{horas:02d}:{minutos:02d}:{segundos:02d}"

    return resultado



def retorna_ultimo_loss_hora_diferença(termina_em, recomendado):
    # retorna false se passou do horario recomendo para abrir operação
    hora = string_para_hora(termina_em)
    horario_atual = datetime.now().time()
    recomendado = string_para_hora2(recomendado)
    resultado = subtrair_tempos(horario_atual, hora)
    res = resultado
    resultado = string_para_hora2(resultado)

    if (resultado > recomendado):
        return (False, res)
    else:
        return (True,res)


