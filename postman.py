from base64 import decode
from json.decoder import JSONDecoder
from typing import Collection
from geradorjava import geradorjava
from bot import bot
import ast
import urllib.request,json
import re

"""
    Usa a Collection v2.1 do Postman
"""
class postman():

    POSTMAN_PATTERN_VARIAVEL = re.compile("\{\{[0-9a-zA-Z_\-$#@\*]*\}\}")
    POSTMAN_PATTERN_VARIAVEL_CHAVES = re.compile("\{\{|\}\}")

    arquivo:str
    formato:str
    constante_integracao:str

    collection : dict = []

    schemas2pojo:dict = {}
    endpoints:dict = {}
    docs:dict = {}

    bot : bot

    def processa_url(self, paths : list):
        metodo_url : str = "/"
        parametros_url : list = []

        for path in paths:
            if self.POSTMAN_PATTERN_VARIAVEL.match(path) == None:
                metodo_url += path + "/"
            else:
                variavel = self.POSTMAN_PATTERN_VARIAVEL_CHAVES.sub("", path)
                variavel = geradorjava.nomeMetodoPropriedade(variavel)
                parametros_url.append("String " + variavel)
                metodo_url += "\" + " + variavel + " + \""

        return metodo_url, parametros_url


    """
        Processa o endpoint

        endpoint : define o  endpoint que irá resgatar
        verbo: : define o verbo que irá resgatar
    """
    def processar_endpoint(self, collection : dict, prefixo : str = ""):
        metodo_nome    : str = geradorjava.nomeMetodoPropriedade(collection["name"], prefixo = prefixo)

        metodo_verbo   : str  = ""
        metodo_url     : str  = "/"
        parametros_url : list = []
        request_body   : dict = None
        response_body  : dict = None
        description    : str  = ""

        if "request" in collection:
            request = collection["request"]

            metodo_verbo = request["method"]
            paths_url    = request["url"]["path"]

            metodo_url, parametros_url = self.processa_url(paths_url)

            if "body" in request and "raw" in request["body"]:
                request_body = bot.jsonToDict(request["body"]["raw"])
            elif "query" in request["url"] and len(request["url"]["query"]):
                request_body = {}
                for query in request["url"]["query"]:
                    if "value" in query and query["value"] != None and query["value"] != "":
                        request_body[query["key"]] = query["value"]
                    else:
                        request_body[query["key"]] = "String"


            if "description" in request:
                description = request["description"]

        if "response" in collection:
            response = collection["response"]
            if len(response) > 0:
                response = response[0]

                if "body" in response:
                    response_body = bot.jsonToDict(response["body"])

        self.bot.add_endpoint(
            geradorjava.converterNomeClasseParaAtributo(metodo_nome),
            metodo_url,
            metodo_verbo,
            description,
            request_body,
            response_body,
            [],
            parametros_url,
            "Response" + geradorjava.gerarClasseNome(collection["name"], prefixo = prefixo),
            "Request"  + geradorjava.gerarClasseNome(collection["name"], prefixo = prefixo),
            geradorjava.converterNomeClasseParaAtributo(metodo_nome)
        )

    """
        Processa os endpoints escolhidos para gerar os POJOs

        endpoints : dicionario contento [endpoint] = [verbos] || [endpoint] = * para todos os verbos do endpoint
    """
    def processar_endpoints(self, collection : dict, prefixo : str = ""):
        for elemento in collection:
            if "item" in elemento:
                self.processar_endpoints(elemento['item'])
            else:
                self.processar_endpoint(elemento)


    """
        Da inicio ao processamento
    """
    def processar(self):
        self.bot.salvarDadosPojos()
        self.bot.criarPojos()
        self.bot.gerarClassesWebSerice()

    """
        path : path da Collection
        formato : recebe o formato da respota [JSON]
        constante_integracao: recebe a constante de integração do chinchila para Integração Externa
    """
    def __init__(self,
        integracao : str,
        constante_integracao:str,
        arquivo : str,
        formato : str = "JSON"
    ):
        self.constante_integracao = constante_integracao
        self.formato = formato

        self.arquivo = arquivo

        if (formato.upper() == "JSON"):
            self.collection = json.loads(self.arquivo)

        self.bot = bot(
            integracao,
            gerarPojoApartirDaDoc = False,
            docs_por_classe = True,
            codigoIntegracao = constante_integracao
        )

        self.processar_endpoints(self.collection['item'])