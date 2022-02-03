import base64, requests, json, os, zipfile
import subprocess, re
from json.encoder import JSONEncoder
from geradorjava import geradorjava

class bot:
    PATH_EXTRAIDOS : str = "chinchila-ejb-basic/src/java"
    PATH_EXTRAIDOS_CORE : str = "chinchila-ejb-core/src/java"
    PATH_ARQUIVOSBASE : str = "base/"
    PATH_ARQUIVOSGERADOS_BASE : str = "modificar"
    PATH_ARQUIVOSGERADOS : str = ""
    PATH_POJO_FALHA : str = "falhas"

    PACOTE_SESSION_BEAN : str = "com.tinoerp.chinchila.business.core"

    # Lista com todos os endpoints
    endpoints = []

    # guarda um dicionario que falharam ao ser pojeado
    dados_falhas = {}

    # Pacote padrão para o POJO
    pacoteWs : str = "com.tinoerp.chinchila.business.basic.integracaoeletronica.{tipo}.{integracao}.ws"
    pacotePadrao : str = "com.tinoerp.chinchila.business.basic.integracaoeletronica.{tipo}.{integracao}"

    definicaoTipoIntegracao : str = "eCommerce"
    integracao : str = ""
    codigoIntegracao : str = ""
    tipo : str = "integracaoexterna"

    # quando true, não esperará os campos para gerar os pojos
    gerarPojoApartirDaDoc : bool = False

    # configurações do json2pojo
    use_long : bool = True
    includeaccessors : bool = True
    initializecollections : bool = True
    propertyworddelimiters : str = "- _"
    usejodadates : bool = True
    usecommonslang3 : bool = True
    includejsr303annotations : bool = True
    includeadditionalproperties  : bool = True
    docs_por_classe  : bool = False
    # Quando true, usa no nome do método de endpoint o geradorjava.nomeMetodoPropriedade
    transformar_nome_endpoint : bool = True

    # usa o nome do método para o pacote das entidades do WS
    nome_metodo_entidade_ws : bool = True

    def __init__(self,integracao:str, gerarPojoApartirDaDoc : bool = False, codigoIntegracao : str = "", definicaoTipoIntegracao : str = "eCommerce",
            use_long : bool = True,includeaccessors : bool = True, initializecollections : bool = True, propertyworddelimiters : str = "- _",
            tipo : str = "integracaoexterna", usejodadates : bool = True, usecommonslang3 : bool = True, includejsr303annotations : bool = True,
            includeadditionalproperties  : bool = True, docs_por_classe : bool = True, transformar_nome_endpoint : bool = True,
            nome_metodo_entidade_ws : bool = True):

        self.codigoIntegracao = codigoIntegracao
        self.gerarPojoApartirDaDoc = gerarPojoApartirDaDoc
        self.integracao = integracao
        self.definicaoTipoIntegracao = definicaoTipoIntegracao
        self.tipo = tipo
        self.pacoteWs = self.pacoteWs.replace("{tipo}",tipo).replace("{integracao}",integracao.replace(" ","")).lower()
        self.pacotePadrao = self.pacotePadrao.replace("{tipo}",tipo).replace("{integracao}",integracao.replace(" ","")).lower()
        self.use_long = use_long
        self.includeaccessors = use_long
        self.initializecollections = initializecollections
        self.propertyworddelimiters = propertyworddelimiters
        self.usejodadates = usejodadates
        self.usecommonslang3 = usecommonslang3
        self.includejsr303annotations = includejsr303annotations
        self.includeadditionalproperties = includeadditionalproperties
        self.docs_por_classe = docs_por_classe
        self.transformar_nome_endpoint = transformar_nome_endpoint
        self.nome_metodo_entidade_ws = nome_metodo_entidade_ws

    # Verifica se existe o path, caso não, então cria
    @staticmethod
    def gerarPath(path : str):
        if not os.path.isdir(path):
            os.makedirs(path)

    # Gera os dados a partir da documentação
    @staticmethod
    def gerarDadosPojosAPartirDaDoc(dados):
        result = {}
        for i in dados:
            result[i['campo']] = geradorjava.gerarDadoTipoDoc(i['tipo'])
        return result

    # Gera os campos para ser tratados no json2pojo a partir da informação dada na documentação ou pojo de cada atributo
    def gerarDadosPojos(self,dados):
        if not self.gerarPojoApartirDaDoc:
            return dados
        else:
            self.gerarDadosPojosAPartirDaDoc(dados)

    # Gera um default de informações para cada atributo
    @staticmethod
    def gerar_dado(campo : str,tipo: str, descricao : str):
        return {
            "campo":campo,
            "tipo":tipo,
            "descricao":descricao
        }


    # adiciona as informações do endpoint(deve-se usar o doc para gerar os javadocs se o gerarPojoApartirDaDoc = true)
    def add_endpoint(self,nome : str, endpoint : str, verbo : str, descricao : str, dados : list,
        resposta : dict = None, doc : list = None, parametros_url : list = [], pojo_resposta_nome : str = None,
        pojo_resquest_nome : str = None, pacote_entidade : str = None
    ):

        self.endpoints.append(
            {
                'nome':nome,
                'endpoint':endpoint,
                'verbo':verbo,
                'descricao':descricao,
                'dados':dados,
                'doc':doc,
                'resposta':resposta,
                'parametros_url':parametros_url,
                'pojo_resposta_nome':pojo_resposta_nome,
                'pojo_request_nome':pojo_resquest_nome,
                'pacote_entidade' : pacote_entidade
            }
        )

    # salva os arquivos com as informações
    def salvarDadosPojo(self,nome,dados):
        path = os.path.join(self.integracao,self.PATH_ARQUIVOSGERADOS, "json/")
        self.gerarPath(path)
        self.gerarPath(os.path.join(path,self.PATH_POJO_FALHA))

        nome = nome + ".json"
        arquivo = open(os.path.join(path, nome),"w")
        arquivo.write(json.dumps(self.gerarDadosPojos(dados)))
        arquivo.close()

    # Varre todos os endpoints, afim de gerar os arquivos JSONs
    def salvarDadosPojos(self):
        for i in self.endpoints:
            # cria pojo da request caso não for null
            if i['dados'] != None:
                self.salvarDadosPojo(i['pojo_request_nome'],i['dados'])

            # cria pojo da resposta caso não for null
            if i['resposta'] != None:
                self.salvarDadosPojo(i['pojo_resposta_nome'],i['resposta'])

    # Varre todos os Dados, afim de gerar os POJOs
    def criarPojos(self):
        for i in self.endpoints:
            # cria pojo da request caso não for null
            if i['dados'] != None:
                self.criarPojo(i['pojo_request_nome'],i['dados'],i['doc'],i['pacote_entidade'])

            # cria pojo da resposta caso não for null
            if i['resposta'] != None:
                self.criarPojo(i['pojo_resposta_nome'],i['resposta'],i['doc'],i['pacote_entidade'])

    # Gera a partir dos arquivos estruturados, os POJOS do pojos2schema
    def criarPojo(self,classeNome,dados,doc, pacote : str = None):
        TEXTO_ANDAMENTO = "Pojeando " + classeNome + ".... "
        print(TEXTO_ANDAMENTO,flush=True)

        targetpackage : str = self.pacoteWs + ".entidades"
        if pacote != None:
            targetpackage += "." + pacote.replace(" ", "").lower()

        path = os.path.join(self.integracao,self.PATH_ARQUIVOSGERADOS,"pojos/")
        self.gerarPath(path)

        arquivoPath = os.path.join(path, classeNome + ".zip")

        r = requests.post("http://www.jsonschema2pojo.org/generator",
            data={
                "schema":json.dumps(self.gerarDadosPojos(dados)),
                "targetpackage": targetpackage,
                "classname": classeNome,
                "targetlanguage":"java",
                "annotationstyle":"jackson2",
                "sourcetype":"json",
                "uselongintegers":self.use_long,
                "includeaccessors": self.includeaccessors,
                "initializecollections": self.initializecollections,
                "propertyworddelimiters" : self.propertyworddelimiters,
                "usejodadates" : self.usejodadates,
                "usecommonslang3" : self.usecommonslang3,
                "includejsr303annotations" : self.includejsr303annotations,
                "includeadditionalproperties": self.includeadditionalproperties,
            }
        )

        zipFile = base64.decodebytes(str(r.text).encode())

        with open(arquivoPath, "wb") as arquivo:
            arquivo.write(zipFile)

        dadosZip = doc

        if self.gerarPojoApartirDaDoc:
            dadosZip = dados

        try:
            self.extrairPojos(arquivoPath, dadosZip)

            print(TEXTO_ANDAMENTO+ "OK",flush=True)
            print(classeNome+ " - Feito")
        except Exception as ex:
            print("Falha ao extrair o ZIP")
            print(ex)
            print("---")
            print("HTTP")
            print(r.status_code)
            print(r.content)
            print("---")
            print("JSON")
            print(json.dumps(self.gerarDadosPojos(dados)))
            print("---")
            print(TEXTO_ANDAMENTO + "FALHA",flush=True)
            print(classeNome+ " - Não concluido")

            self.salvarDadosPojo(os.path.join(self.PATH_POJO_FALHA,classeNome),dados)

        print()


    """
        UnZip dos POJOs gerados pelo json2pojo
    """
    def extrairPojos(self,arquivo : str, dados):
        path = os.path.join(self.integracao,self.PATH_EXTRAIDOS)
        self.gerarPath(path)
        try:
            print("Extraindo Pojos e gerando JavaDocs",flush=True)

            zipFile = zipfile.ZipFile(arquivo,allowZip64=False,compression=zipfile.ZIP_DEFLATED)
            zipFile.extractall(path)
            for i in zipFile.infolist():
                docs = dados
                classe_nome : str = i.filename.replace(".java","").split('/')[-1]
                if self.docs_por_classe and classe_nome in dados:
                    docs = dados[classe_nome]
                elif self.docs_por_classe:
                    docs = []
                    print("Não há descrição para os dados de " + classe_nome)
                geradorjava.gerarJavaDocPojo(os.path.join(path, i.filename), docs)
        except Exception as ex:
            raise ex


    def gerarClassesWebSerice(self):
        path = os.path.join(self.integracao,self.PATH_EXTRAIDOS, geradorjava.pacoteParaPath(self.pacoteWs))
        self.gerarPath(path)

        classeConstantsNome = geradorjava.gerarClasseNome(self.integracao,sufixo="Constants")
        classeWsNome = geradorjava.gerarClasseNome(self.integracao,sufixo="W S")
        classeContextoNome = geradorjava.gerarClasseNome(self.integracao,sufixo="Contexto")

        classeIntegracaoExternaNome = geradorjava.gerarClasseNome(self.integracao,prefixo="Integracao Externa")
        classeIntegracaoExternaAppLocalNome = geradorjava.gerarClasseNome(self.integracao,prefixo="Integracao Externa",sufixo="Local")
        classeIntegracaoSessionBeanNome = geradorjava.gerarClasseNome(self.integracao,prefixo="Integracao Externa",sufixo="Session Bean")

        # gera classe de constantes basica
        with open(os.path.join(path, classeConstantsNome + ".java"), "w") as arquivo:
            constants : str = ""
            constants += geradorjava.gerarConstantsJava("Verbo POST para requisição HTTP.","String","HTTP_POST","POST")
            constants += geradorjava.gerarConstantsJava("Verbo GET para requisição HTTP.","String","HTTP_GET","GET")
            constants += geradorjava.gerarConstantsJava("Verbo PUT para requisição HTTP.","String","HTTP_PUT","PUT")
            constants += geradorjava.gerarConstantsJava("Verbo PATCH para requisição HTTP.","String","HTTP_PATCH","PATCH")
            constants += geradorjava.gerarConstantsJava("Verbo DELETE para requisição HTTP.","String","HTTP_DELETE","DELETE")
            constants += geradorjava.gerarConstantsJava("Domínio da API.","String","URL_DOMINIO","https://dominio.com")
            arquivo.write(
                geradorjava.gerarClasse(
                    self.pacoteWs,
                    classeConstantsNome,
                    constants
                )
            )

        # Variaveis para serem substituidas
        nomeClasseIntegracao : str = geradorjava.gerarClasseNome(self.integracao)
        nomeVariavelWS : str = geradorjava.nomeMetodoPropriedade(self.integracao,sufixo="W S")
        instanciaNomeAppLocal: str = geradorjava.nomeMetodoPropriedade(self.integracao,prefixo="Integracao",sufixo="Local")
        nomeConstanteInseridaIntegracao : str = geradorjava.gerarConstantNome(self.integracao)
        chaveBaseIntegracaoChinchila : str = "IntegracaoExterna." + self.definicaoTipoIntegracao + "." + nomeClasseIntegracao

        # Carrega os arquivos de base e gera novos
        #
        #   Arquivos de base do pacote padrão
        #
        #
        pathBaseArquivos = os.path.join(self.integracao,self.PATH_EXTRAIDOS, geradorjava.pacoteParaPath(self.pacotePadrao))
        pathArquivosModificar = os.path.join(self.integracao,self.PATH_ARQUIVOSGERADOS_BASE)
        pathSessionBean = os.path.join(self.integracao,self.PATH_EXTRAIDOS_CORE, geradorjava.pacoteParaPath(self.PACOTE_SESSION_BEAN))

        self.gerarPath(pathArquivosModificar)
        self.gerarPath(pathSessionBean)

        # Classe que gera os métodos de WS
        with open(os.path.join(self.PATH_ARQUIVOSBASE, "BaseWS.java"), "r") as arquivoBase:
            texto : str = arquivoBase.read()
            metodos : str = ""

            for i in self.endpoints:
                # contém o nome da classe que irá enviar para o servidor
                pojo_request_nome : str = ""
                # nome dado ao parâmetro de envio de requisicao
                parametro_request : str = "null"
                # contém o tipo do método
                pojo_response_nome : str = "void"
                # a class que será enviada por parâmetro para o metodo requisição
                tipo_respose_class: str = "Object.class"
                # define se deve tratar a resposta como uma lista
                tipo_lista : bool = False

                if i['pojo_resposta_nome'] != None and i['pojo_resposta_nome'] != "":
                    pojo_response_nome = i['pojo_resposta_nome']

                if i['pojo_request_nome'] != None and i['pojo_request_nome'] != "":
                    pojo_request_nome = i['pojo_request_nome']

                parametros_url : list = []
                if len(i['parametros_url']) > 0:
                    parametros_url = list(i['parametros_url'])

                # trata do envio ao servidor
                if i['dados'] != None:
                    if type(i['dados']) is list:
                        pojo_request_nome = "List<" + pojo_request_nome + ">"

                    parametros_url.append(pojo_request_nome + " requisicao")
                    parametro_request = "requisicao"

                    i['descricao'] += "\n"
                    i['descricao'] += "\n@param " + parametro_request
                    i['descricao'] += "\n   Parâmetro contendo o dados de requisição."

                # trata da resposta do servidor(como o tipo do método)
                if i['resposta'] != None:
                    tipo_respose_class = pojo_response_nome + ".class"
                    if type(i['resposta']) is list:
                        pojo_response_nome = "List<" + pojo_response_nome + ">"
                        tipo_respose_class =  "listClass"
                        tipo_lista = True

                metodos += geradorjava.gerarMetodosEndpointsJava(
                    i['descricao'],
                    pojo_response_nome,
                    tipo_respose_class,
                    tipo_lista,
                    parametros_url,
                    geradorjava.nomeMetodoPropriedade(i['nome']) if self.transformar_nome_endpoint else i['nome'],
                    classeConstantsNome,
                    i['endpoint'],
                    i['verbo'],
                    parametro_request
                )

            # trata para limpar o método
            metodos = metodos.replace(" + \"\",",",")

            texto = texto.replace("{nomeVariavelWS}",nomeVariavelWS)
            texto = texto.replace("{classeConstantsNome}",classeConstantsNome)
            texto = texto.replace("{metodosWs}",metodos)
            texto = texto.replace("{codigoIntegracao}",self.codigoIntegracao)
            texto = texto.replace("{tipoIntegracao}", self.definicaoTipoIntegracao)
            texto = texto.replace("{definicaoTipoIntegracao}",self.definicaoTipoIntegracao)
            texto = texto.replace("{instanciaNomeAppLocal}",instanciaNomeAppLocal)
            texto = texto.replace("{classeNomeIntegracaoExternaBase}", classeIntegracaoExternaNome)
            texto = texto.replace("{classeNomeAppLocal}", classeIntegracaoExternaAppLocalNome)
            texto = texto.replace("{classeContexto}", classeContextoNome)
            texto = texto.replace("{classeWS}", classeWsNome)
            texto = texto.replace("{nomeConstanteInseridaIntegracao}",nomeConstanteInseridaIntegracao)
            texto = texto.replace("{nomeIntegracao}", self.integracao)
            texto = texto.replace("{pacote}",self.pacoteWs)
            texto = texto.replace("{chaveBaseIntegracaoChinchila}",chaveBaseIntegracaoChinchila)
            texto = texto.replace("{classeIntegracaoSessionBeanNome}",classeIntegracaoSessionBeanNome)
            texto = re.sub("[ ]*$","",texto,flags=re.MULTILINE|re.IGNORECASE)

            with open(os.path.join(path, classeWsNome+".java"), "w") as arquivoEscrita:
                arquivoEscrita.write(texto)

        # Classe de contexto
        with open(os.path.join(self.PATH_ARQUIVOSBASE, "ContextoBase.java"), "r") as arquivoBase:
            texto : str = arquivoBase.read()

            texto = texto.replace("{nomeVariavelWS}",nomeVariavelWS)
            texto = texto.replace("{codigoIntegracao}",self.codigoIntegracao)
            texto = texto.replace("{tipoIntegracao}", self.definicaoTipoIntegracao)
            texto = texto.replace("{definicaoTipoIntegracao}",self.definicaoTipoIntegracao)
            texto = texto.replace("{instanciaNomeAppLocal}",instanciaNomeAppLocal)
            texto = texto.replace("{classeNomeIntegracaoExternaBase}", classeIntegracaoExternaNome)
            texto = texto.replace("{classeNomeAppLocal}", classeIntegracaoExternaAppLocalNome)
            texto = texto.replace("{classeContexto}", classeContextoNome)
            texto = texto.replace("{classeWS}", classeWsNome)
            texto = texto.replace("{nomeConstanteInseridaIntegracao}",nomeConstanteInseridaIntegracao)
            texto = texto.replace("{nomeIntegracao}", self.integracao)
            texto = texto.replace("{pacote}",self.pacoteWs)
            texto = texto.replace("{chaveBaseIntegracaoChinchila}",chaveBaseIntegracaoChinchila)
            texto = texto.replace("{classeIntegracaoSessionBeanNome}",classeIntegracaoSessionBeanNome)
            texto = re.sub("[ ]*$","",texto,flags=re.MULTILINE|re.IGNORECASE)

            with open(os.path.join(path, classeContextoNome + ".java"), "w") as arquivoEscrita:
                arquivoEscrita.write(texto)

        with open(os.path.join(self.PATH_ARQUIVOSBASE, "IntegracaoExternaBase.java"), "r") as arquivoBase:
            texto : str = arquivoBase.read()

            texto = texto.replace("{nomeVariavelWS}",nomeVariavelWS)
            texto = texto.replace("{codigoIntegracao}",self.codigoIntegracao)
            texto = texto.replace("{tipoIntegracao}", self.definicaoTipoIntegracao)
            texto = texto.replace("{definicaoTipoIntegracao}",self.definicaoTipoIntegracao)
            texto = texto.replace("{instanciaNomeAppLocal}",instanciaNomeAppLocal)
            texto = texto.replace("{classeNomeIntegracaoExternaBase}", classeIntegracaoExternaNome)
            texto = texto.replace("{classeNomeAppLocal}", classeIntegracaoExternaAppLocalNome)
            texto = texto.replace("{classeContexto}", classeContextoNome)
            texto = texto.replace("{classeWS}", classeWsNome)
            texto = texto.replace("{nomeConstanteInseridaIntegracao}",nomeConstanteInseridaIntegracao)
            texto = texto.replace("{nomeIntegracao}", self.integracao)
            texto = texto.replace("{pacote}",self.pacotePadrao)
            texto = texto.replace("{pacoteWS}",self.pacoteWs)
            texto = texto.replace("{chaveBaseIntegracaoChinchila}",chaveBaseIntegracaoChinchila)
            texto = texto.replace("{classeIntegracaoSessionBeanNome}",classeIntegracaoSessionBeanNome)
            texto = re.sub("[ ]*$","",texto,flags=re.MULTILINE|re.IGNORECASE)

            with open(os.path.join(pathBaseArquivos, "IntegracaoExterna"+nomeClasseIntegracao+".java"), "w") as arquivoEscrita:
                arquivoEscrita.write(texto)

        # Carrega os arquivos de base e gera novos
        with open(os.path.join(self.PATH_ARQUIVOSBASE, "IntegracaoExternaBaseAppLocal.java"), "r") as arquivoBase:
            texto : str = arquivoBase.read()

            texto = texto.replace("{nomeVariavelWS}",nomeVariavelWS)
            texto = texto.replace("{codigoIntegracao}",self.codigoIntegracao)
            texto = texto.replace("{tipoIntegracao}", self.definicaoTipoIntegracao)
            texto = texto.replace("{definicaoTipoIntegracao}",self.definicaoTipoIntegracao)
            texto = texto.replace("{instanciaNomeAppLocal}",instanciaNomeAppLocal)
            texto = texto.replace("{classeNomeIntegracaoExternaBase}", classeIntegracaoExternaNome)
            texto = texto.replace("{classeNomeAppLocal}", classeIntegracaoExternaAppLocalNome)
            texto = texto.replace("{classeContexto}", classeContextoNome)
            texto = texto.replace("{classeWS}", classeWsNome)
            texto = texto.replace("{nomeConstanteInseridaIntegracao}",nomeConstanteInseridaIntegracao)
            texto = texto.replace("{nomeIntegracao}", self.integracao)
            texto = texto.replace("{pacote}",self.pacotePadrao)
            texto = texto.replace("{chaveBaseIntegracaoChinchila}",chaveBaseIntegracaoChinchila)
            texto = texto.replace("{classeIntegracaoSessionBeanNome}",classeIntegracaoSessionBeanNome)
            texto = re.sub("[ ]*$","",texto,flags=re.MULTILINE|re.IGNORECASE)

            with open(os.path.join(pathBaseArquivos, "IntegracaoExterna"+nomeClasseIntegracao+"Local.java"), "w") as arquivoEscrita:
                arquivoEscrita.write(texto)

        # Carrega os arquivos de base e gera novos
        with open(os.path.join(self.PATH_ARQUIVOSBASE, "IntegracaoExternaBaseSessionBean.java"), "r") as arquivoBase:
            texto : str = arquivoBase.read()

            texto = texto.replace("{nomeVariavelWS}",nomeVariavelWS)
            texto = texto.replace("{codigoIntegracao}",self.codigoIntegracao)
            texto = texto.replace("{tipoIntegracao}", self.definicaoTipoIntegracao)
            texto = texto.replace("{definicaoTipoIntegracao}",self.definicaoTipoIntegracao)
            texto = texto.replace("{instanciaNomeAppLocal}",instanciaNomeAppLocal)
            texto = texto.replace("{classeNomeIntegracaoExternaBase}", classeIntegracaoExternaNome)
            texto = texto.replace("{classeNomeAppLocal}", classeIntegracaoExternaAppLocalNome)
            texto = texto.replace("{classeContexto}", classeContextoNome)
            texto = texto.replace("{classeWS}", classeWsNome)
            texto = texto.replace("{nomeConstanteInseridaIntegracao}",nomeConstanteInseridaIntegracao)
            texto = texto.replace("{nomeIntegracao}", self.integracao)
            texto = texto.replace("{pacoteSessionBean}",self.PACOTE_SESSION_BEAN)
            texto = texto.replace("{pacotePadrao}",self.pacotePadrao)
            texto = texto.replace("{chaveBaseIntegracaoChinchila}",chaveBaseIntegracaoChinchila)
            texto = texto.replace("{classeIntegracaoSessionBeanNome}",classeIntegracaoSessionBeanNome)
            texto = re.sub("[ ]*$","",texto,flags=re.MULTILINE|re.IGNORECASE)

            with open(os.path.join(pathSessionBean, "IntegracaoExterna"+nomeClasseIntegracao+"SessionBean.java"), "w") as arquivoEscrita:
                arquivoEscrita.write(texto)

        # Carrega os arquivos de base e gera novos
        with open(os.path.join(self.PATH_ARQUIVOSBASE, "IntegracaoConstants.java"), "r") as arquivoBase:
            texto : str = arquivoBase.read()

            texto = texto.replace("{nomeVariavelWS}",nomeVariavelWS)
            texto = texto.replace("{codigoIntegracao}",self.codigoIntegracao)
            texto = texto.replace("{tipoIntegracao}", self.definicaoTipoIntegracao)
            texto = texto.replace("{definicaoTipoIntegracao}",self.definicaoTipoIntegracao)
            texto = texto.replace("{instanciaNomeAppLocal}",instanciaNomeAppLocal)
            texto = texto.replace("{classeNomeIntegracaoExternaBase}", classeIntegracaoExternaNome)
            texto = texto.replace("{classeNomeAppLocal}", classeIntegracaoExternaAppLocalNome)
            texto = texto.replace("{classeContexto}", classeContextoNome)
            texto = texto.replace("{classeWS}", classeWsNome)
            texto = texto.replace("{nomeConstanteInseridaIntegracao}",nomeConstanteInseridaIntegracao)
            texto = texto.replace("{nomeIntegracao}", self.integracao)
            texto = texto.replace("{pacote}",self.PACOTE_SESSION_BEAN)
            texto = texto.replace("{chaveBaseIntegracaoChinchila}",chaveBaseIntegracaoChinchila)
            texto = texto.replace("{classeIntegracaoSessionBeanNome}",classeIntegracaoSessionBeanNome)
            texto = re.sub("[ ]*$","",texto,flags=re.MULTILINE|re.IGNORECASE)

            with open(os.path.join(pathArquivosModificar, "IntegracaoConstants.java"), "w") as arquivoEscrita:
                arquivoEscrita.write(texto)

        # Carrega os arquivos de base e gera novos
        with open(os.path.join(self.PATH_ARQUIVOSBASE, "DefinicoesConfiguracoesAvancadasUnidadeNegocio.java"), "r") as arquivoBase:
            texto : str = arquivoBase.read()

            texto = texto.replace("{nomeVariavelWS}",nomeVariavelWS)
            texto = texto.replace("{codigoIntegracao}",self.codigoIntegracao)
            texto = texto.replace("{tipoIntegracao}", self.definicaoTipoIntegracao)
            texto = texto.replace("{definicaoTipoIntegracao}",self.definicaoTipoIntegracao)
            texto = texto.replace("{instanciaNomeAppLocal}",instanciaNomeAppLocal)
            texto = texto.replace("{classeNomeIntegracaoExternaBase}", classeIntegracaoExternaNome)
            texto = texto.replace("{classeNomeAppLocal}", classeIntegracaoExternaAppLocalNome)
            texto = texto.replace("{classeContexto}", classeContextoNome)
            texto = texto.replace("{classeWS}", classeWsNome)
            texto = texto.replace("{nomeConstanteInseridaIntegracao}",nomeConstanteInseridaIntegracao)
            texto = texto.replace("{nomeIntegracao}", self.integracao)
            texto = texto.replace("{pacote}",self.PACOTE_SESSION_BEAN)
            texto = texto.replace("{chaveBaseIntegracaoChinchila}",chaveBaseIntegracaoChinchila)
            texto = texto.replace("{classeIntegracaoSessionBeanNome}",classeIntegracaoSessionBeanNome)
            texto = re.sub("[ ]*$","",texto,flags=re.MULTILINE|re.IGNORECASE)

            with open(os.path.join(pathArquivosModificar, "DefinicoesConfiguracoesAvancadasUnidadeNegocio.java"), "w") as arquivoEscrita:
                arquivoEscrita.write(texto)

        # Carrega os arquivos de base e gera novos
        with open(os.path.join(self.PATH_ARQUIVOSBASE, "chinchilaresource.properties"), "r") as arquivoBase:
            texto : str = arquivoBase.read()

            texto = texto.replace("{nomeVariavelWS}",nomeVariavelWS)
            texto = texto.replace("{codigoIntegracao}",self.codigoIntegracao)
            texto = texto.replace("{tipoIntegracao}", self.definicaoTipoIntegracao)
            texto = texto.replace("{definicaoTipoIntegracao}",self.definicaoTipoIntegracao)
            texto = texto.replace("{instanciaNomeAppLocal}",instanciaNomeAppLocal)
            texto = texto.replace("{classeNomeIntegracaoExternaBase}", classeIntegracaoExternaNome)
            texto = texto.replace("{classeNomeAppLocal}", classeIntegracaoExternaAppLocalNome)
            texto = texto.replace("{classeContexto}", classeContextoNome)
            texto = texto.replace("{classeWS}", classeWsNome)
            texto = texto.replace("{nomeConstanteInseridaIntegracao}",nomeConstanteInseridaIntegracao)
            texto = texto.replace("{nomeIntegracao}", self.integracao)
            texto = texto.replace("{pacote}",self.PACOTE_SESSION_BEAN)
            texto = texto.replace("{chaveBaseIntegracaoChinchila}",chaveBaseIntegracaoChinchila)
            texto = texto.replace("{classeIntegracaoSessionBeanNome}",classeIntegracaoSessionBeanNome)
            texto = re.sub("[ ]*$","",texto,flags=re.MULTILINE|re.IGNORECASE)

            with open(os.path.join(pathArquivosModificar, "chinchilaresource.properties"), "w") as arquivoEscrita:
                arquivoEscrita.write(texto)

        # Carrega os arquivos de base e gera novos
        with open(os.path.join(self.PATH_ARQUIVOSBASE, "BasicIntegracaoExternaServerFacade.java"), "r") as arquivoBase:
            texto : str = arquivoBase.read()

            texto = texto.replace("{nomeVariavelWS}",nomeVariavelWS)
            texto = texto.replace("{codigoIntegracao}",self.codigoIntegracao)
            texto = texto.replace("{tipoIntegracao}", self.definicaoTipoIntegracao)
            texto = texto.replace("{definicaoTipoIntegracao}",self.definicaoTipoIntegracao)
            texto = texto.replace("{instanciaNomeAppLocal}",instanciaNomeAppLocal)
            texto = texto.replace("{classeNomeIntegracaoExternaBase}", classeIntegracaoExternaNome)
            texto = texto.replace("{classeNomeAppLocal}", classeIntegracaoExternaAppLocalNome)
            texto = texto.replace("{classeContexto}", classeContextoNome)
            texto = texto.replace("{classeWS}", classeWsNome)
            texto = texto.replace("{nomeConstanteInseridaIntegracao}",nomeConstanteInseridaIntegracao)
            texto = texto.replace("{nomeIntegracao}", self.integracao)
            texto = texto.replace("{pacote}",self.PACOTE_SESSION_BEAN)
            texto = texto.replace("{chaveBaseIntegracaoChinchila}",chaveBaseIntegracaoChinchila)
            texto = texto.replace("{classeIntegracaoSessionBeanNome}",classeIntegracaoSessionBeanNome)
            texto = re.sub("[ ]*$","",texto,flags=re.MULTILINE|re.IGNORECASE)

            with open(os.path.join(pathArquivosModificar, "BasicIntegracaoExternaServerFacade.java"), "w") as arquivoEscrita:
                arquivoEscrita.write(texto)


        # Carrega os arquivos de base e gera novos
        with open(os.path.join(self.PATH_ARQUIVOSBASE, "IntegracaoExternaPanel.java"), "r") as arquivoBase:
            texto : str = arquivoBase.read()

            texto = texto.replace("{nomeVariavelWS}",nomeVariavelWS)
            texto = texto.replace("{codigoIntegracao}",self.codigoIntegracao)
            texto = texto.replace("{tipoIntegracao}", self.definicaoTipoIntegracao)
            texto = texto.replace("{definicaoTipoIntegracao}",self.definicaoTipoIntegracao)
            texto = texto.replace("{instanciaNomeAppLocal}",instanciaNomeAppLocal)
            texto = texto.replace("{classeNomeIntegracaoExternaBase}", classeIntegracaoExternaNome)
            texto = texto.replace("{classeNomeAppLocal}", classeIntegracaoExternaAppLocalNome)
            texto = texto.replace("{classeContexto}", classeContextoNome)
            texto = texto.replace("{classeWS}", classeWsNome)
            texto = texto.replace("{nomeConstanteInseridaIntegracao}",nomeConstanteInseridaIntegracao)
            texto = texto.replace("{nomeIntegracao}", self.integracao)
            texto = texto.replace("{pacote}",self.PACOTE_SESSION_BEAN)
            texto = texto.replace("{chaveBaseIntegracaoChinchila}",chaveBaseIntegracaoChinchila)
            texto = texto.replace("{classeIntegracaoSessionBeanNome}",classeIntegracaoSessionBeanNome)
            texto = re.sub("[ ]*$","",texto,flags=re.MULTILINE|re.IGNORECASE)

            with open(os.path.join(pathArquivosModificar, "IntegracaoExternaPanel.java"), "w") as arquivoEscrita:
                arquivoEscrita.write(texto)

    @staticmethod
    def jsonToDict(texto : str):
        raw : str = texto
        raw = re.compile("(?=(?<!http\:)(?<!https\:))\/\/(.)*\n").sub("\n", raw)
        raw = raw.encode("utf-8")
        raw = raw.decode("unicode_escape")

        return json.loads(raw)