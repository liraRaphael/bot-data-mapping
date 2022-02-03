from open_api import open_api

with open("leancommerce.json","r") as arquivo:
    oapi : open_api = open_api("Leancommerce","A",arquivo.read())
    oapi.processar_endpoints({
        '/api/v1/estoque' : '*',
        '/api/v1/pedidos/id/{id}' : '*',
        '/api/v1/pedidos/numero/{numero}' : '*',
        '/api/v1/pedidos' : '*',
        '/api/v1/pedidos/{numero}/nota-fiscal' : '*',
        '/api/v1/precos' : '*',
        '/api/v1/catalogo/produtos' : '*',
        '/api/v1/catalogo/produtos/{id}' : '*',
        '/api/v1/catalogo/produtos/{id}' : '*',
        '/api/v1/catalogo/produtos/{id}' : '*',
        '/api/v1/login' : '*',
        '/api/v1/pedidos/id/{id}/tracking' : '*',
        '/api/v1/pedidos/numero/{numero}/tracking' : '*'
    })
    oapi.processar()
