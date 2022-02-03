from unidecode import unidecode
import re
class geradorjava:

    # gera o nome da classe
    @staticmethod
    def gerarClasseNome(nome: str,prefixo : str = None,sufixo : str = None):
        retorno : str = ""

        if prefixo != None:
            retorno += prefixo

        retorno += nome

        if sufixo != None:
            retorno += sufixo

        retorno = unidecode(retorno)
        retorno = re.compile("[\W]").sub(" ", retorno)
        retorno = re.sub(r'([A-Z])', r' \1', retorno)
        retorno = retorno.title().strip()

        return retorno.replace(" ", "")

    # gera o nome da classe
    @staticmethod
    def gerarConstantNome(nome: str):
        retorno : str = ""
        retorno += nome.replace('/',"_").replace('\\',"_").replace(" ","_").upper()

        return unidecode(retorno)

    @staticmethod
    def nomeClassePojo(endpoint : str, verbo : str):
        return unidecode(geradorjava.gerarClasseNome(endpoint,prefixo=verbo))

    @staticmethod
    def converterNomeClasseParaAtributo(nome: str):
        return unidecode(nome[0].lower() + nome[1:])

    @staticmethod
    def nomeMetodoPropriedade(nome: str,prefixo : str = None,sufixo : str = None):
        metodo : str = geradorjava.gerarClasseNome(nome,prefixo,sufixo)
        return unidecode(geradorjava.converterNomeClasseParaAtributo(metodo))

    @staticmethod
    def gerarMetodosEndpointsJava(
        textoJavaDoc : str,
        tipo : str,
        tipo_requisicao_class : str,
        tipo_lista : bool,
        pametros : list,
        nome:str,
        classeConstantsNome,
        endpoint:str,verbo : str,
        parametro_request : str = "null"
    ):
        metodo : str = ""
        metodo += geradorjava.gerarJavaDoc(textoJavaDoc)
        metodo += "  public "+tipo+" "+nome+"(" + ", ".join(pametros) + ") throws Exception {\n"
        if tipo_lista:
            metodo += "    Class<"+tipo+"> "+tipo_requisicao_class+" = (Class) List.class;\n\n"
        metodo += "    "
        if tipo != "void":
            metodo += "return "
        metodo += "requisicao(\""+endpoint+"\", "
        metodo += classeConstantsNome + ".HTTP_"+verbo.upper()+", "
        metodo += tipo_requisicao_class+", "
        if tipo_lista:
            metodo += tipo.replace("List<","").replace(">","") + ".class, "
        metodo += parametro_request + ");\n"
        metodo += "  }\n\n"

        return metodo

    @staticmethod
    def gerarConstantsJava(textoJavaDoc : str,tipo : str, nome:str, valor):
        constants : str = ""
        constants += geradorjava.gerarJavaDoc(textoJavaDoc)
        constants += "  public static final "+tipo+" "+nome.upper()+" = "
        if tipo == "String" or tipo == "Date":
            constants += "\"" + valor + "\""
        elif tipo == "Char" or tipo == "char" or tipo == "Character":
            constants += "\'" + valor + "\'"
        else:
            constants += str(valor)
        constants += ";\n\n"

        return constants

    @staticmethod
    def gerarClasse(pacote : str,classeNome : str,conteudo : str):
        classe : str = ""
        classe += "package " + pacote + ";\n"
        classe += "\n"
        classe += "public class "+classeNome+" {\n"
        classe += "\n"
        classe += conteudo
        classe += "}"

        return classe

    @staticmethod
    def gerarJavaDoc(texto : str):
        javaDoc : str = ""
        javaDoc += "  /**\n"
        javaDoc += "   * "+texto.replace("\n","\n   * ")+"\n"
        javaDoc += "   */\n"
        return javaDoc


    @staticmethod
    def pacoteParaPath(pacote : str):
        return pacote.replace(".","/").lower()

    @staticmethod
    def gerarJavaDocPojo(arquivoPath : str, campos):

        with open(arquivoPath, "r+") as arquivo:
            texto = arquivo.read()

            for i in campos:
                match = "    @JsonProperty(\""+i['campo']+"\")"
                substituir : str = geradorjava.gerarJavaDoc(i['descricao']) + match
                texto = texto.replace(match,substituir)

            arquivo.seek(0)
            arquivo.write(texto)

    # Gera, a partir do tipo relatado na documentação, um dado para o pojo
    @staticmethod
    def gerarDadoTipoDoc(tipo : str):
        tipo = tipo.lower()

        if tipo == 'int' or tipo == 'integer' or tipo == 'long'  or tipo == 'longer':
            return 1
        elif tipo == 'double' or tipo == 'bigdecimal' or tipo == 'number' or tipo == 'numeric' or tipo == 'float':
            return 1.2345
        elif tipo == 'bool' or tipo == 'boolean':
            return True
        elif tipo == 'char' or tipo == 'character':
            return 'A'
        else:
            return "texto"

    # Retorna o tipo para java
    @staticmethod
    def gerarTipoJava(tipo : str):
        tipo = tipo.lower()

        if tipo == 'int' or tipo == 'integer' or tipo == 'long'  or tipo == 'longer':
            return "Integer"
        elif tipo == 'double' or tipo == 'bigdecimal' or tipo == 'number' or tipo == 'numeric' or tipo == 'float':
            return "Double"
        elif tipo == 'bool' or tipo == 'boolean':
            return "Boolean"
        elif tipo == 'char' or tipo == 'character':
            return 'Character'
        else:
            return "String"