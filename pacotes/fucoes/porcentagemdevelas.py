def porcentagem_velas(velas):

        vermelhas = []
        verdes = []
        doji = []

        for vela in velas:
            if (vela['close']>vela['open']):
                #verde
                verdes.append(vela)
            if (vela['close']<vela['open']):
                #vermelha
                vermelhas.append(vela)
            if (vela['close']==vela['open']):
                #doji
                doji.append(vela)


        porcentagem_vermelhas = (len(vermelhas)/len(velas)*100).__round__(2)
        porcentagem_verdes = (len(verdes)/len(velas)*100).__round__(2)
        porcentagem_dojis = (len(doji)/len(velas)*100).__round__(2)
        return porcentagem_vermelhas, porcentagem_verdes, porcentagem_dojis




