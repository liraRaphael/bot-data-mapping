from base64 import decode
from json.decoder import JSONDecoder
from geradorjava import geradorjava
from bot import bot
import urllib.request,json

"""
    Usa o OpenAPI 3.0 para pojear para JAVA e Chinchila

    https://editor.swagger.io/ -> converter OpenApi de qualquer versão para a versão 3
"""
class open_api():

    arquivo:str
    formato:str
    constante_integracao:str

    openApi : dict = []

    schemas2pojo:dict = {}
    endpoints:dict = {}
    docs:dict = {}

    bot : bot


    """
        Processar o POJO para o JSON2SCHEMA

        chavePacote : Nome do pacte da classe
    """
    def processar_schema_json2pojo(self,chavePacote):
        dados : dict = self.openApi['components']['schemas']
        pojo : dict = {}

        classe_nome : str = str(chavePacote).split('.')[-1]

        if not chavePacote in self.schemas2pojo:
            dado : dict = dados[chavePacote]
            # verifica se é do tipo o object e se terá mais filhos
            if dado['type'] == "object" and 'properties' in dado:

                for chaveAtributo in dado['properties'].keys():
                    """
                        Gera javadocs basico
                    """
                    if 'description' in dado['properties'][chaveAtributo]:
                        if not classe_nome in self.docs:
                            self.docs[classe_nome] = []

                        descr : dict = {
                            'descricao' : dado['properties'][chaveAtributo]['description'],
                            'campo' : chaveAtributo
                        }

                        self.docs[classe_nome].append(descr)

                        atributo_docs_chave : str = chaveAtributo[0].upper() + chaveAtributo[1:]

                        if 'items' in dado['properties'][chaveAtributo] and '$ref' in dado['properties'][chaveAtributo]['items']:
                            if atributo_docs_chave[-1] == 's':
                                if not atributo_docs_chave[:-1] in self.docs:
                                    self.docs[atributo_docs_chave[:-1]] = []
                                self.docs[atributo_docs_chave[:-1]].append(descr)
                            else:
                                if not atributo_docs_chave in self.docs:
                                    self.docs[atributo_docs_chave] = []
                                self.docs[atributo_docs_chave].append(descr)
                        elif '$ref' in dado['properties'][chaveAtributo]:
                            if not atributo_docs_chave in self.docs:
                                self.docs[atributo_docs_chave] = []
                            self.docs[atributo_docs_chave].append(descr)

                    """
                        Varre os atributos
                    """
                    # caso haja referencias para outro DTO e seja um array
                    if 'items' in dado['properties'][chaveAtributo] and '$ref' in dado['properties'][chaveAtributo]['items']:
                        # pega o nome do pacote com a classe para recusões, gerando um array desse objeto
                        classe_recursao : str = str(dado['properties'][chaveAtributo]['items']['$ref']).split('/')[-1]

                        classe_temp = None
                        if chavePacote != classe_recursao:
                            classe_temp = self.processar_schema_json2pojo(classe_recursao)
                        else:
                            classe_temp = dict(pojo)
                            classe_temp[chaveAtributo] = None

                        pojo[chaveAtributo] = []
                        pojo[chaveAtributo].append(dict(classe_temp))
                        pojo[chaveAtributo].append(dict(classe_temp))
                        pojo[chaveAtributo].append(dict(classe_temp))

                    # caso haja referencias para outro DTO
                    elif '$ref' in dado['properties'][chaveAtributo]:
                        # pega o nome do pacote com a classe para uma recusão
                        classe_recursao : str = str(dado['properties'][chaveAtributo]['$ref']).split('/')[-1]

                        classe_temp = {}
                        if chavePacote != classe_recursao:
                            classe_temp = self.processar_schema_json2pojo(classe_recursao)
                        else:
                            classe_temp = dict(pojo)
                            classe_temp[chaveAtributo] = None

                        if 'enum' in classe_temp:
                            pojo[chaveAtributo] = classe_temp['enum']
                        else:
                            pojo[chaveAtributo] = classe_temp

                    # gera um array de alguma coisa
                    elif 'items' in dado['properties'][chaveAtributo] and 'type' in dado['properties'][chaveAtributo]['items']:
                        tipo = dado['properties'][chaveAtributo]['items']['type']

                        pojo[chaveAtributo] = []
                        pojo[chaveAtributo].append(geradorjava.gerarDadoTipoDoc(tipo))
                        pojo[chaveAtributo].append(geradorjava.gerarDadoTipoDoc(tipo))
                        pojo[chaveAtributo].append(geradorjava.gerarDadoTipoDoc(tipo))

                    else:
                        tipo = str(dado['properties'][chaveAtributo]['type'])
                        pojo[chaveAtributo] = geradorjava.gerarDadoTipoDoc(
                            str(dado['properties'][chaveAtributo]['type'])
                        )
                pojo = dict(pojo)
            elif 'enum' in dado:
                tipo = str(dado['type'])
                pojo = {
                    'enum' : geradorjava.gerarDadoTipoDoc(str(dado['type']))
                }

            elif dado['type'] == "array" and 'items' in dado  and 'properties' in dado['items']:
                for chaveRecursao in dado['items']['properties'].keys():
                    # pega o nome do pacote com a classe para recusões, gerando um array desse objeto
                    objeto = dado['items']['properties'][chaveRecursao]

                    classe_temp : dict = {}

                    if '$ref' in objeto:
                        classe_recusao : str = str(objeto['$ref']).split('/')[-1]
                        classe_temp = self.processar_schema_json2pojo(classe_recusao)
                    else:
                        pojo[chaveRecursao] = dado['items']['properties'][chaveRecursao]['example']

            elif 'example' in dado:
                pojo = dado['example']

            elif 'type' in dado:
                pojo = geradorjava.gerarDadoTipoDoc(str(dado['type']))

            self.schemas2pojo[chavePacote] = pojo
        else:
            pojo = self.schemas2pojo[chavePacote]

        return pojo


    """
        Faz o looping para a montagem dos POJOS

        retorno_esperado : Usado para recusão, quando necesário puxar outro object
    """
    def ler_schemas_json2pojo(self, retorno_esperado:str = None):
        dados : dict = self.openApi['components']['schemas']

        # verifica se não tá esperando um schema
        if retorno_esperado == None:
            # varre o nome do pacote com a classe
            for chavePacote in dados.keys():
                self.processar_schema_json2pojo(chavePacote)
        else:
            return self.processar_schema_json2pojo(retorno_esperado)

        return None

    """
        Processa os endpoints escolhidos para gerar os POJOs

        endpoint : define o  endpoint que irá resgatar
        verbo: : define o verbo que irá resgatar
    """
    def processar_endpoint_verbo(self, endpoint : str,verbo : str):
        dados : dict = self.openApi['paths']

        if verbo in dados[endpoint]:
            dado = dados[endpoint][verbo]

            metodo_nome : str =  geradorjava.nomeMetodoPropriedade(verbo + " " + endpoint)
            if 'operationId' in dado:
                metodo_nome = dado['operationId'].replace(".", " ")

            metodo_descricao : str = ""
            if 'summary' in dado:
                metodo_descricao : str = dado['summary']

            metodo_body_request = None
            metodo_resposta = None

            parametros_url : list = []

            pojo_resposta_nome : str = ""
            pojo_request_nome : str = ""

            # Processa o retorno da resposta
            if 'responses' in dado and '200' in dado['responses'] and 'content' in dado['responses']['200']:
                resposta = dado['responses']['200']['content']
                tipo_resposta = [*resposta]
                conteudo_resposta = resposta[tipo_resposta[0]]['schema']

                if 'type' in conteudo_resposta:
                    if 'items' in conteudo_resposta and '$ref' in conteudo_resposta['items']:
                        object_temp = self.processar_schema_json2pojo(conteudo_resposta['items']['$ref'].split("/")[-1])

                        pojo_resposta_nome = conteudo_resposta['items']['$ref'].split("/")[-1]

                        metodo_resposta = []
                        metodo_resposta.append(dict(object_temp))
                        metodo_resposta.append(dict(object_temp))
                        metodo_resposta.append(dict(object_temp))
                    else:
                        metodo_resposta = geradorjava.gerarDadoTipoDoc(conteudo_resposta['type'])
                        pojo_resposta_nome = geradorjava.gerarTipoJava(metodo_resposta)

                elif '$ref' in conteudo_resposta:
                    object_temp = self.processar_schema_json2pojo(conteudo_resposta['$ref'].split("/")[-1])
                    metodo_resposta = dict(object_temp)

                    pojo_resposta_nome = conteudo_resposta['$ref'].split("/")[-1]


            if 'requestBody' in dado and 'content' in dado['requestBody']:
                tipo_requesicao = [* dado['requestBody']['content'].keys()][0]
                conteudo_requesicao = dado['requestBody']['content'][tipo_requesicao]['schema']

                if str(tipo_requesicao).lower() not in ["multipart/form-data"]:
                    if '$ref' in conteudo_requesicao:
                        pojo_request_nome = conteudo_requesicao['$ref'].split("/")[-1]
                        metodo_body_request  = self.processar_schema_json2pojo(pojo_request_nome)
                else:
                    if "properties" in conteudo_requesicao:
                        pojo_request_nome = geradorjava.gerarClasseNome(dado["operationId"],prefixo="Request")
                        metodo_body_request : dict() = {}

                        for chave in conteudo_requesicao["properties"].keys():
                            metodo_body_request[chave] = conteudo_requesicao["properties"][chave]

            if 'parameters' in dado:
                metodo_descricao += "\n"
                for parametro in dado['parameters']:
                    if parametro['in'] == 'path':
                        metodo_descricao += "\n @param " + parametro['name']
                        metodo_descricao += "\n    " + parametro['description']

                        endpoint = endpoint.replace("{" + parametro['name'] + "}", "\" + " + parametro['name'] + " + \"")

                        parametros_url.append(geradorjava.gerarTipoJava(parametro['schema']['type']) + " " + parametro['name'])

            self.bot.add_endpoint(metodo_nome,endpoint,verbo,metodo_descricao,metodo_body_request,metodo_resposta,
                self.docs,parametros_url,pojo_resposta_nome.split('.')[-1],pojo_request_nome.split('.')[-1]
            )
        else:
            print("Não existe o verbo " + verbo + " no endpoint " + endpoint + " no arquivo do OpenAPI.")

    """
        Processa os endpoints escolhidos para gerar os POJOs

        endpoints : dicionario contento [endpoint] = [verbos] || [endpoint] = * para todos os verbos do endpoint
    """
    def processar_endpoints(self, endpoints : dict):
        dados : dict = self.openApi['paths']

        for endpoint in endpoints.keys():
            if endpoint in dados:
                if endpoints[endpoint] == '*':
                    for verbo in dados[endpoint].keys():
                        self.processar_endpoint_verbo(endpoint, verbo)
                else:
                    for verbo in endpoints[endpoint]:
                        self.processar_endpoint_verbo(endpoint, verbo)
            else:
                print("Não existe o endpoint " + endpoint + " no arquivo do OpenAPI.")

    """
        Da inicio ao processamento
    """
    def processar(self):
        self.bot.salvarDadosPojos()
        self.bot.criarPojos()
        self.bot.gerarClassesWebSerice()

    """
        path : path do OpenAPI
        formato : recebe o formato da respota [JSON]
        constante_integracao: recebe a constante de integração do chinchila para Integração Externa
    """
    def __init__(self,
        integracao : str,
        constante_integracao:str,
        arquivo : str,
        formato : str = "JSON",
        tipo    : str = "integracaoexterna",
        definicaoTipoIntegracao : str = "eCommerce"
    ):
        self.constante_integracao = constante_integracao
        self.formato = formato

        self.arquivo = arquivo

        if (formato.upper() == "JSON"):
            self.openApi = json.loads(self.arquivo)

        self.bot = bot(
            integracao,
            gerarPojoApartirDaDoc= False,
            docs_por_classe= True,
            codigoIntegracao= constante_integracao,
            tipo=tipo,
            definicaoTipoIntegracao=definicaoTipoIntegracao
        )

        self.ler_schemas_json2pojo()
