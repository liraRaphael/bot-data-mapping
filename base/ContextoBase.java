package {pacote};

/**
 * Contexto para as configurações utilizadas na integração.
 */
public class {classeContexto} {

  /**
   * Timeout para a requisição HTTP
   */
  private Long requisicaoTimeout;

  /**
   * Timeout para a requisição HTTP
   */
  public Long getRequisicaoTimeout() {
    return requisicaoTimeout;
  }

  /**
   * Timeout para a requisição HTTP
   */
  public void setRequisicaoTimeout(Long requisicaoTimeout) {
    this.requisicaoTimeout = requisicaoTimeout;
  }
}