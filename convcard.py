from open_api import open_api

with open("convcard.json","r") as arquivo:
    oapi : open_api = open_api("ConvCard","A",arquivo.read(),tipo="pbm",definicaoTipoIntegracao="pbm")
    oapi.processar_endpoints({
        '/service/solicita-compra' : '*',
        '/service/confirmacao-compra' : '*',
        '/service/solicitacao-cancelamento-compra' : '*',
        '/service/confirmacao-cancelamento-compra' : '*',
        '/service/consulta-saldo' : '*'
    })

    oapi.processar()