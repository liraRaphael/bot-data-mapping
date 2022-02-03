from requests.models import Response
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from geradorjava import geradorjava
from bot import bot
import xml.etree.ElementTree as ET
import requests, re

class omie():

    # Constantes de autenticação, caso necessário buscar por request
    OMIE_APP_KEY : str = "38333295000"
    OMIE_APP_SECRET : str = "4cea520a0e2a2ecdc267b75d3424a0ed"

    driver = None

    dados = {}
    docs  = {}

    bot = bot('Omie',
            gerarPojoApartirDaDoc= False,
            docs_por_classe= False,
            codigoIntegracao= 'Z',
            transformar_nome_endpoint = False
        )

    def processar(self):
        self.bot.salvarDadosPojos()
        self.bot.criarPojos()
        self.bot.gerarClassesWebSerice()

    def requisicao_endpoint(self, url:str,call:str,data):
        header = { 'Content-type': 'application/json' }
        r = requests.post(url,data={
            'call':call,
            'app_key': self.OMIE_APP_KEY,
            'app_secret': self.OMIE_APP_SECRET,
            'param':[data]
        }, headers=header)

        return r.content

    def processar_pagina_doc_rows(self, rows):
        docs : list = []
        dados: dict = {}

        for row in rows:
            if row.text.strip() == '':
                continue

            drive_tipo = row.find_element_by_css_selector(".parameter-type")

            campo = row.find_element_by_css_selector(".parameter-name").text.strip()
            tipo_nome  = drive_tipo.text.strip()
            descricao = row.find_element_by_css_selector(".parameter-docs").text.replace("+","\n").strip()
            tipo_exemplo = geradorjava.gerarDadoTipoDoc(tipo_nome)

            if len(drive_tipo.find_elements_by_css_selector("a")) > 0:
                tipo_exemplo,_ = self.processar_pagina_doc_tipo(tipo_nome)

            docs.append(bot.gerar_dado(campo, tipo_nome, descricao))
            dados[campo] = tipo_exemplo

        return dados,docs

    def processar_pagina_doc_tipo(self, elemento_nome):
        print("Processando elemento: " + elemento_nome)

        tipo = self.driver.find_element_by_css_selector(".complexTypeItem [name='" + elemento_nome + "']")
        tipo = tipo.find_element_by_xpath("..")

        rows = tipo.find_elements_by_css_selector("table tr")

        if elemento_nome in self.dados:
            return self.dados[elemento_nome], self.docs[elemento_nome]
        elif len(rows) > 0:
            dados,docs = self.processar_pagina_doc_rows(rows)

            self.dados[elemento_nome] = dados
            self.docs[elemento_nome]  = docs

            return self.dados[elemento_nome], self.docs[elemento_nome]
        else:
            dados,docs = self.processar_pagina_doc_tipo(tipo.find_element_by_css_selector("p span a span").text.strip())
            self.dados[elemento_nome] = [dados] if not type(dados) == list else dados
            self.docs[elemento_nome]  = docs
            return self.dados[elemento_nome], self.docs[elemento_nome]

    def processar_pagina_doc(self, url:str):
        print("Processando endpoint: " + url)
        self.driver.get(url)
        endpoint : str = self.driver.find_element_by_css_selector("#section-endpoint code").text.strip()

        docs_web = self.driver.find_elements_by_css_selector(".complexTypeItem")
        for i in docs_web:
            schema_nome : str = i.find_element_by_css_selector("h3").text.strip()

            self.processar_pagina_doc_tipo(schema_nome)


        endpoints = self.driver.find_elements_by_css_selector(".methodItem")
        for i in endpoints:
            metodo_nome : str = i.find_element_by_css_selector(".method-name").text.strip()
            metodo_descricao : str = i.find_element_by_css_selector("p").text.strip()
            request_nome : str = i.find_element_by_css_selector(".method-parameter-type").text.strip()
            request_doc = self.docs[request_nome]
            request_pojo = self.dados[request_nome]
            response_nome : str = i.find_element_by_css_selector(".panel-footer .pre a span").text.strip()
            response_doc = self.docs[response_nome]
            response_pojo = self.dados[response_nome]

            print("Processando de call: " + metodo_nome)

            doc = request_doc + response_doc

            self.bot.add_endpoint(
                geradorjava.converterNomeClasseParaAtributo(metodo_nome),
                endpoint + "|" + metodo_nome, #gambiarra para usar o action dps
                "POST",
                metodo_descricao,
                request_pojo,
                response_pojo,
                doc,
                [],
                geradorjava.gerarClasseNome(response_nome),
                geradorjava.gerarClasseNome(request_nome)
            )
            print("Processamento da call concluido: " + metodo_nome)
        print("Endpoint concluido: " + url)
        print()
        print()

    def __init__(self):
        print("iniciando browser...")
        self.driver = webdriver.Chrome()

        self.processar_pagina_doc("https://app.omie.com.br/api/v1/estoque/ajuste/")
        self.processar_pagina_doc("https://app.omie.com.br/api/v1/geral/produtos/")
        self.processar_pagina_doc("https://app.omie.com.br/api/v1/estoque/consulta/")
        self.processar_pagina_doc("https://app.omie.com.br/api/v1/produtos/pedido/")

        self.processar()
        print("Finalizado")

omie()