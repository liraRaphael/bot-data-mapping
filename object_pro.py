from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from geradorjava import geradorjava
from bot import bot

driver = webdriver.Chrome()


class object_pro():

    bot = bot('object pro', True, tipo="pbm")
    itensVarrer = []


    def add_busca(self, nome, xPathH3,xPathDescricao,xPathTabela):
        self.itensVarrer.append(
            {
                'nome' :nome,
                'h3':xPathH3,
                'descricao':xPathDescricao,
                'tabela':xPathTabela
            }
        )

    def tratar_tabela(self, tabela):
        dados = []

        tabela_tr = tabela.find_elements_by_css_selector("tbody tr")
        for i in tabela_tr:
            dados.append(
                bot.gerar_dado(
                    i.find_element_by_css_selector("td:nth-of-type(1)").text.strip(),
                    i.find_element_by_css_selector("td:nth-of-type(4)").text.strip(),
                    i.find_element_by_css_selector("td:nth-of-type(3)").text.strip()
                )
            )

        return dados

    def processar_endpoint(self,dados):
        h3 = driver.find_element_by_xpath(dados['h3'])
        endpoint = h3.find_element_by_css_selector('small').text.strip()
        verbo = h3.text.split(" ")[0].strip()
        descricao = driver.find_element_by_xpath(dados['descricao']).text.strip()
        tabela = driver.find_element_by_xpath(dados['tabela'])

        dadosTabela = self.tratar_tabela(tabela)
        self.bot.add_endpoint(dados['nome'],endpoint,verbo,descricao,dadosTabela)

    def processar(self):
        for i in self.itensVarrer:
            self.processar_endpoint(i)

        self.bot.salvarDadosPojos()
        self.bot.criarPojos()

    def __init__(self):
        print("iniciando browser...")
        driver.get("file:///home/alpha7/Desktop/bot2/doc-object/Object%20Pro%20Tecnologia.html")

        self.add_busca('consulta','/html/body/main/h3[3]','/html/body/main/p[6]','/html/body/main/table[6]')
        self.add_busca('Envio','/html/body/main/h3[4]','/html/body/main/p[7]','/html/body/main/table[8]')

        self.add_busca('Modelo por Prêmios - reset','/html/body/main/div[3]/h3[1]','/html/body/main/div[3]/p[6]','/html/body/main/div[3]/table[1]')
        self.add_busca('Modelo por Prêmios - reset','/html/body/main/div[3]/h3[2]','/html/body/main/div[3]/p[7]','/html/body/main/div[3]/table[3]')
        self.add_busca('Modelo por Prêmios - Método para lançar venda, pagamento, devolução gerando os pontos.','/html/body/main/div[3]/h3[3]','/html/body/main/div[3]/p[8]','/html/body/main/div[3]/table[5]')
        self.add_busca('Modelo por Prêmios - Envio','/html/body/main/div[3]/h3[4]','/html/body/main/div[3]/p[9]','/html/body/main/div[3]/table[7]')
        self.add_busca('Modelo por Prêmios - Envio','/html/body/main/div[3]/h3[5]','/html/body/main/div[3]/p[10]','/html/body/main/div[3]/table[10]')

        self.add_busca('Modelo por Desconto - Consulta','/html/body/main/div[4]/h3[1]','/html/body/main/div[4]/p[1]','/html/body/main/div[4]/table[1]')
        self.add_busca('Modelo por Desconto - Envio','/html/body/main/div[4]/h3[2]','/html/body/main/div[4]/p[2]','/html/body/main/div[4]/table[4]')

        self.add_busca('Nota Fiscal de Entrada','/html/body/main/h3[5]','/html/body/main/p[9]','/html/body/main/table[10]')

        print("Processando campos levantados...")
        self.processar();

        driver.close();


object_pro()