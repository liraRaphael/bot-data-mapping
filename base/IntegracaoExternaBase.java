package {pacote};

import {pacoteWS}.{classeContexto};
import {pacoteWS}.{classeWS};
import com.tinoerp.chinchila.business.basic.integracaoeletronica.integracaoexterna.AbstractIntegracaoExterna;
import com.tinoerp.chinchila.business.configuracoesavancadas.DefinicoesConfiguracoesAvancadasUnidadeNegocio;
import com.tinoerp.chinchila.business.local.ClassificacaoLocalFacade;
import com.tinoerp.chinchila.business.local.EmbalagemLocalFacade;
import com.tinoerp.chinchila.business.local.FuncoesVendaLocalFacade;
import com.tinoerp.chinchila.business.local.UnidadeNegocioLocalFacade;
import com.tinoerp.chinchila.entidades.auxiliares.DadosDFeIntegracaoExterna;
import com.tinoerp.chinchila.entidades.auxiliares.PrecosEmbalagemIntegracaoExterna;
import com.tinoerp.chinchila.entidades.constantes.EntregaConstants;
import com.tinoerp.chinchila.entidades.constantes.EntregaRemessaConstants;
import com.tinoerp.chinchila.entidades.constantes.IntegracaoConstants;
import com.tinoerp.chinchila.entidades.constantes.IntegracaoEntradaOrcamentoConstants;
import com.tinoerp.chinchila.entidades.constantes.NfeConstants;
import com.tinoerp.chinchila.entidades.constantes.PessoaConstants;
import com.tinoerp.chinchila.entidades.persistentes.Embalagem;
import com.tinoerp.chinchila.entidades.persistentes.IntegracaoEntradaCliente;
import com.tinoerp.chinchila.entidades.persistentes.IntegracaoEntradaOrcamento;
import com.tinoerp.chinchila.entidades.persistentes.IntegracaoEntradaPessoa;
import com.tinoerp.chinchila.entidades.persistentes.IntegracaoSaidaCfe;
import com.tinoerp.chinchila.entidades.persistentes.IntegracaoSaidaEmbalagem;
import com.tinoerp.chinchila.entidades.persistentes.IntegracaoSaidaEntregaRemessa;
import com.tinoerp.chinchila.entidades.persistentes.IntegracaoSaidaNfe;
import com.tinoerp.chinchila.entidades.persistentes.UnidadeNegocio;
import com.tinoerp.guaxinim.entities.DomainException;
import com.tinoerp.guaxinim.permission.PermissionException;
import com.tinoerp.guaxinim.permission.SessionToken;
import com.tinoerp.guaxinim.resources.MessageResource;
import com.tinoerp.guaxinim.util.CollectionUtilities;
import com.tinoerp.guaxinim.util.NumberUtilities;
import com.tinoerp.guaxinim.util.StringUtilities;
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Stream;
import javax.ejb.EJB;
import javax.persistence.NoResultException;
import org.apache.commons.lang3.ArrayUtils;
import org.apache.log4j.Logger;

/**
 * Implementação da Integração Externa com o {nomeIntegracao}.
 */
public class {classeNomeIntegracaoExternaBase} extends AbstractIntegracaoExterna
    implements {classeNomeAppLocal} {

  /**
   * Façade de Embalagem.
   */
  @EJB
  private EmbalagemLocalFacade embalagemFacade;

  /**
   * Façade de Classificação.
   */
  @EJB
  private ClassificacaoLocalFacade classificacaoFacade;

  /**
   * Façade de Unidade Negócio.
   */
  @EJB
  private UnidadeNegocioLocalFacade unidadeNegocioFacade;

  /**
   * Façade de Funções Venda.
   */
  @EJB
  private FuncoesVendaLocalFacade funcoesVendaFacade;


  /**
   * Logger de {classeNomeIntegracaoExternaBase}.
   */
  private static final Logger LOGGER = Logger.getLogger({classeNomeIntegracaoExternaBase}.class);

  /**
   * {@inheritDoc}
   */
  @Override
  public void integrarElementosFaltantes(SessionToken token, long idUnidadeNegocio)
      throws PermissionException, DomainException, Exception {

    boolean integracaoHabilitada =
        configuracaoFacade.getConfiguracaoAvancadaUnidadeNegocio(token, idUnidadeNegocio,
        DefinicoesConfiguracoesAvancadasUnidadeNegocio//
        .INTEGRACAO_EXTERNA_ECOMMERCE_{nomeConstanteInseridaIntegracao}_HABILITADO, true);

    if (!integracaoHabilitada) {
      return;
    }

    String macAddressServidor = integracaoExternaFacade.getMACAddressFromAppServer(token);

    String macAddressConfiguracao = configuracaoFacade.getConfiguracaoAvancadaUnidadeNegocio(token,
        idUnidadeNegocio, DefinicoesConfiguracoesAvancadasUnidadeNegocio//
        .INTEGRACAO_EXTERNA_ECOMMERCE_{nomeConstanteInseridaIntegracao}_MACADDRESS_SERVIDOR, true);

    if (!macAddressConfiguracao.equalsIgnoreCase(macAddressServidor)) {
      throw new DomainException(new MessageResource(
          "{chaveBaseIntegracaoChinchila}.erroMACAddressServidorInvalido",
          new Object[]{DefinicoesConfiguracoesAvancadasUnidadeNegocio.//
        INTEGRACAO_EXTERNA_ECOMMERCE_{nomeConstanteInseridaIntegracao}_MACADDRESS_SERVIDOR.getChave(),
        macAddressConfiguracao, macAddressServidor}));
    }

    Boolean integracaoDFeHabilitada = configuracaoFacade.getConfiguracaoAvancadaUnidadeNegocio(
        token, idUnidadeNegocio, DefinicoesConfiguracoesAvancadasUnidadeNegocio//
        .INTEGRACAO_EXTERNA_ECOMMERCE_{nomeConstanteInseridaIntegracao}_INTEGRAR_DFE_HABILITADO, true);

    Boolean integracaoPedido = configuracaoFacade.getConfiguracaoAvancadaUnidadeNegocio(token,
        idUnidadeNegocio, DefinicoesConfiguracoesAvancadasUnidadeNegocio//
        .INTEGRACAO_EXTERNA_ECOMMERCE_{nomeConstanteInseridaIntegracao}_INTEGRAR_PEDIDO_HABILITADO, true);

    Boolean integracaoProduto = configuracaoFacade.getConfiguracaoAvancadaUnidadeNegocio(token,
        idUnidadeNegocio, DefinicoesConfiguracoesAvancadasUnidadeNegocio//
        .INTEGRACAO_EXTERNA_ECOMMERCE_{nomeConstanteInseridaIntegracao}_INTEGRAR_PRODUTO_HABILITADO, true);

    Boolean integracaoEnvioEntregaRemessa =
        configuracaoFacade.getConfiguracaoAvancadaUnidadeNegocio(token,
        idUnidadeNegocio, DefinicoesConfiguracoesAvancadasUnidadeNegocio//
        .INTEGRACAO_EXTERNA_ECOMMERCE_{nomeConstanteInseridaIntegracao}_INTEGRAR_ENVIO_HABILITADO, true);

    Long requisicaoTimeout = configuracaoFacade.getConfiguracaoAvancadaUnidadeNegocio(token,
        idUnidadeNegocio, DefinicoesConfiguracoesAvancadasUnidadeNegocio//
        .INTEGRACAO_EXTERNA_ECOMMERCE_{nomeConstanteInseridaIntegracao}_REQUISICAO_TIMEOUT, true);

    {classeContexto} contexto = new {classeContexto}();
    contexto.setRequisicaoTimeout(requisicaoTimeout);

    {classeWS} {nomeVariavelWS} = new {classeWS}(contexto);

    if (integracaoProduto) {
      integrarProdutos(token, idUnidadeNegocio, {nomeVariavelWS});
    }

    if (integracaoPedido) {
      integrarPedidos(token, idUnidadeNegocio, {nomeVariavelWS});
    }

    if (integracaoDFeHabilitada) {
      integrarDocumentosFiscaisVinculados(token, idUnidadeNegocio, {nomeVariavelWS});
    }

    /** caso não usar, excluir aqui e a assinatura */
    if (integracaoEnvioEntregaRemessa) {
      integrarEnvioEntregaRemessa(token, idUnidadeNegocio, {nomeVariavelWS});
    }
  }

  /**
   * Realiza a integração de Produtos com o {nomeIntegracao}, atualizando preços e estoque dos Produtos.
   *
   * @param token
   *   Identificador de uma sessão autenticada e validada de usuário.
   * @param idUnidadeNegocio
   *   ID da Unidade de negócio em que a integração deve ser executada.
   * @param {nomeVariavelWS}
   *   {classeWS} com as configurações necessárias para execução da integração.
   *
   * @throws Exception uma exceção qualquer.
   */
  private void integrarProdutos(SessionToken token, long idUnidadeNegocio,
      {classeWS} {nomeVariavelWS}) throws Exception {

  }

  /**
   * Envia os dados dos Documentos Fiscais Eletrônicos de pedidos que foram gerados através da
   * {nomeIntegracao}.
   *
   *  @param token
   *   Identificador de uma sessão autenticada e validada de usuário.
   * @param idUnidadeNegocio
   *   ID da Unidade de negócio em que a integração deve ser executada.
   * @param {nomeVariavelWS}
   *   {classeWS} com as configurações necessárias para execução da integração.
   *
   * @throws Exception Exceção qualquer.
   */
  private void integrarDocumentosFiscaisVinculados(SessionToken token, long idUnidadeNegocio,
      {classeWS} {nomeVariavelWS}) throws Exception {

  }

  /**
   * Realiza a integração de Pedidos com o {nomeIntegracao}, importando novos Pedidos, ou atualizando
   * Pedidos já cadastrados.
   *
   * @param token
   *   Identificador de uma sessão autenticada e validada de usuário.
   * @param idUnidadeNegocio
   *   ID da Unidade de negócio em que a integração deve ser executada.
   * @param {nomeVariavelWS}
   *   {classeWS} com as configurações necessárias para execução da integração.
   *
   * @throws Exception uma exceção qualquer.
   */
  private void integrarPedidos(SessionToken token, long idUnidadeNegocio,
      {classeWS} {nomeVariavelWS}) throws Exception {

  }

  /**
   * Realiza a integração dos envios de Entregas com o {nomeIntegracao}, o avisando quando o pedido foi
   * enviado ou entregue
   *
   * @param token
   *   Identificador de uma sessão autenticada e validada de usuário.
   * @param idUnidadeNegocio
   *   ID da Unidade de negócio em que a integração deve ser executada.
   * @param {nomeVariavelWS}
   *   {classeWS} com as configurações necessárias para execução da integração.
   *
   * @throws Exception uma exceção qualquer.
   */
  private void integrarEnvioEntregaRemessa(SessionToken token, long idUnidadeNegocio,
      {classeWS} {nomeVariavelWS}) throws Exception {

  }
}