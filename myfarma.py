from open_api import open_api

with open("mypharma_corrigido.json","r") as arquivo:
    oapi : open_api = open_api("MyPharma","A",arquivo.read())
    endpoints = {
        '/session' : '*',
        '/integration/products' : '*'
    }

    oapi.processar_endpoints(endpoints)
    oapi.processar()
