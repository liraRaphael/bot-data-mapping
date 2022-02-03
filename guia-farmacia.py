from pdfminer import high_level
from geradorjava import geradorjava
from bot import bot

class guia_farmacia():

    PATH_ARQUIVO = "guia-farm.pdf"

    bot = bot('Guia Farmacia', True, tipo="guia")

    def __init__(self):

        pages = [0] # just the first page

        extracted_text = high_level.extract_text(self.PATH_ARQUIVO, "", pages)
        print(extracted_text)


guia_farmacia()