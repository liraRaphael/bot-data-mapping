package {pacote};

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.type.CollectionType;
import com.tinoerp.guaxinim.util.IOUtilities;
import java.net.URI;
import java.util.List;
import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.client.config.RequestConfig;
import org.apache.http.client.methods.HttpEntityEnclosingRequestBase;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.client.methods.HttpPut;
import org.apache.http.client.methods.HttpDelete;
import org.apache.http.client.methods.HttpPatch;
import org.apache.http.client.methods.HttpRequestBase;
import org.apache.http.entity.ContentType;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClientBuilder;
import org.apache.log4j.Logger;
import com.fasterxml.jackson.databind.JsonNode;
import java.net.URLDecoder;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.Map;
import org.apache.http.NameValuePair;
import org.apache.http.client.entity.UrlEncodedFormEntity;
import org.apache.http.client.utils.URLEncodedUtils;
import org.apache.http.message.BasicNameValuePair;

public class {classeWS} {

  /**
   * Contexto com as configurações
   */
  private {classeContexto} contexto;
  
  /**
   * Logger de {classeWS}.
   */
  private static final Logger LOGGER = Logger.getLogger({classeWS}.class);
  
  public {classeWS}({classeContexto} contexto){
    this.contexto = contexto;
  }  
   
  public {classeContexto} getContexto() {
    return contexto;
  }

  public void setContexto({classeContexto} contexto) {
    this.contexto = contexto;
  }

{metodosWs}
  /**
   * Transforma uma instância de um POJO que seria usado para JSON, em um FormData.
   *
   * @param pojo
   *    O objeto que será transformado em FormData.
   *
   * @return
   *    {@code HttpEntity} com o FormData.
   *
   * @throws Exception
   *    Uma exception qualquer.
   */
  private HttpEntity pojoJsonParaFormData(Object pojo) throws Exception {
    return new UrlEncodedFormEntity(pojoJsonParaListNameValuePair(pojo), "UTF-8");
  }

  /**
   * Transforma uma instância de um POJO que seria usado para JSON, em um parâmetros de url (query
   * string).
   *
   * @param pojo
   *    O objeto que será transformado em parâmetro de url (query string).
   *
   * @return
   *    {@code String} com parâmetro de url (query string).
   *
   * @throws Exception
   *    Uma exception qualquer.
   */
  private String pojoJsonParaUrlQuery(Object pojo) throws Exception {
    return "?" + URLDecoder.decode(URLEncodedUtils.format(pojoJsonParaListNameValuePair(pojo),
        "UTF-8"), "UTF-8");
  }

  /**
   * Transforma uma instância de um POJO que seria usado para JSON, em um
   * {@code List<NameValuePair>}.
   *
   * @param pojo
   *    O objeto que será transformado em {@code List<NameValuePair>}.
   *
   * @return
   *    {@code List<NameValuePair>}.
   *
   * @throws Exception
   *    Uma exception qualquer.
   */
  private List<NameValuePair> pojoJsonParaListNameValuePair(Object pojo) throws Exception {
    ObjectMapper objectMapper = new ObjectMapper();
    List<NameValuePair> parametros = new ArrayList<>();

    JsonNode jsonNode = objectMapper.readTree(objectMapper.writeValueAsString(pojo));
    Iterator<Map.Entry<String, JsonNode>> campos = jsonNode.fields();

    while (campos.hasNext()) {
      Map.Entry<String, JsonNode> campo = campos.next();
      parametros.add(new BasicNameValuePair(campo.getKey(), campo.getValue().asText()));
    }

    return parametros;
  }
  
  
  /**
   * Realiza uma requisição HTTP padrão para um Endpoint.
   *
   * @param endpoint
   *    O Endpoint sem o domínio e a base.
   * @param verbo
   *    O verbo HTTP para a requisição.
   * @param resposta
   *    Classe que devolverá a resposta do WebService.
   * @param body
   *    Corpo da requisição em formato de classe qualquer, para ser transformado em JSON.
   *
   * @return
   *    Um objeto construído a partir da resposta retornada na chamada ao Web Service.
   *
   * @throws Exception
   *    Uma exceção qualquer.
   */
  private <T> T requisicao(String endpoint, String verbo, Class<T> resposta, Object body)
      throws Exception {
    return requisicao(endpoint,verbo,resposta,Object.class,body);
  }

  /**
   * Realiza uma requisição HTTP padrão para um Endpoint.
   *
   * @param endpoint
   *    O Endpoint sem o domínio e a base.
   * @param verbo
   *    O verbo HTTP para a requisição.
   * @param resposta
   *    Classe que devolverá a resposta do WebService.
   * @param typeOf
   *    Classe usada para gerar retorno específico da List. <b>OBS:</b> Usado somente quando a
   *    resposta for do tipo {@code List<E>}.
   * @param body
   *    Corpo da requisição em formato de classe qualquer, para ser transformado em JSON.
   *
   * @return
   *    Um objeto construído a partir da resposta retornada na chamada ao Web Service.
   *
   * @throws Exception
   *    Uma exceção qualquer.
   */
  private <T, U> T requisicao(String endpoint, String verbo, Class<T> resposta, Class<U> typeOf,
      Object body) throws Exception {
    ObjectMapper objectMapper = new ObjectMapper();
    objectMapper.setTimeZone(TimeZone.getDefault());
    
    HttpEntity bodyEntity = new StringEntity(
        objectMapper.writeValueAsString(body), ContentType.APPLICATION_JSON);

    return requisicao({classeConstantsNome}.URL_DOMINIO + endpoint, verbo, resposta, typeOf,
        bodyEntity);
  }

  /**
   * Realiza uma requisição HTTP.
   *
   * @param url
   *    O Endpoint sem o domínio.
   * @param verbo
   *    Recebe o verbo HTTP para a requisição.
   * @param body
   *    Corpo da requisição bruto. Podendo ser {@code null}.
   * @param resposta
   *    Classe que devolverá a resposta do WebService.
   * @param typeOf
   *    Classe usada para gerar retorno específico da List. <b>OBS:</b> Usado somente quando a
   *    resposta for do tipo {@code List<E>}.
   * @param body
   *    Envia os parametros o corpo bruto da requisição.
   * @param bearerToken
   *    Bearer token a ser enviado no cabelho de requisição. Pode ser {@code null} para o não uso.
   *
   * @return
   *    Um objeto construído a partir da resposta retornada na chamada ao Web Service.
   *
   * @throws Exception
   *    Uma exceção qualquer.
   */
  @SuppressWarnings("unchecked")
  private <T, U> T requisicao(String url, String verbo, Class<T> resposta, Class<U> typeOf,
      HttpEntity body) throws Exception {

    // Deserealiza o JSON e trata os campos de forma insensitve
    ObjectMapper objectMapper = new ObjectMapper();
    objectMapper.configure(MapperFeature.ACCEPT_CASE_INSENSITIVE_PROPERTIES, true);

    String conteudoResposta = null;
    Integer statusCode = null;
    String bodyString = "";

    HttpRequestBase httpClient;

    verbo = verbo.toUpperCase();
    if (verbo.equals({classeConstantsNome}.HTTP_POST)) {
      httpClient = HttpPost.class.newInstance();
    }
    else if (verbo.equals({classeConstantsNome}.HTTP_GET)) {
      httpClient = HttpGet.class.newInstance();
    }
    else if (verbo.equals({classeConstantsNome}.HTTP_PUT)) {
      httpClient = HttpPut.class.newInstance();
    }
    else if (verbo.equals({classeConstantsNome}.HTTP_DELETE)) {
      httpClient = HttpDelete.class.newInstance();
    }
    else if (verbo.equals({classeConstantsNome}.HTTP_PATCH)) {
      httpClient = HttpPatch.class.newInstance();
    }
    else {
      throw new Exception("Verbo inválido.");
    }
    httpClient.setURI(new URI(url));

    httpClient.setConfig(RequestConfig.custom()
        .setConnectTimeout(contexto.getRequisicaoTimeout().intValue())
        .setSocketTimeout(contexto.getRequisicaoTimeout().intValue())
        .build());

    if (body != null) {
      ((HttpEntityEnclosingRequestBase) httpClient).setEntity(body);
      bodyString = IOUtilities.getInputStreamDataAsString(body.getContent());
    }
    
    // Headers
    // TODO:Headers

    CloseableHttpClient closeableHttpClient = HttpClientBuilder.create().build();
    HttpResponse respostaHttp = closeableHttpClient.execute(httpClient);
    
    statusCode = respostaHttp.getStatusLine().getStatusCode();

    try {
      conteudoResposta = IOUtilities.getInputStreamDataAsString(respostaHttp.getEntity()
          .getContent());
    }
    catch (NullPointerException ex) {
      conteudoResposta = null;
    }
 
    LOGGER.info("{nomeIntegracao}: Requisição HTTP"
        + "\nEndpoint: " + url
        + "\nVerbo: " + verbo
        + "\nStatus: " + statusCode
        + "\nCorpo da requisição:\n" + bodyString
        + "\nResposta da requisição:\n" + (conteudoResposta != null ? conteudoResposta : ""));

    if (statusCode >= 300) {
      throw new Exception("{nomeIntegracao}: " + conteudoResposta);
    }

    if (resposta == String.class) {
      return (T) conteudoResposta;
    }
    else if (resposta.getCanonicalName().equals(List.class.getCanonicalName())) {
      CollectionType listType =
          objectMapper.getTypeFactory().constructCollectionType(ArrayList.class, typeOf);
      return objectMapper.readValue(conteudoResposta, listType);
    }
    else if(conteudoResposta != null) {
      return objectMapper.readValue(conteudoResposta, resposta);
    }else{
      return null;
    }

}