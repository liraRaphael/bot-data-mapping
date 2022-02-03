  /**
   * Interface local da integracao externa com a/o {nomeIntegracao}.
   */
  @EJB
  private {classeNomeAppLocal} {instanciaNomeAppLocal};

....

          if (chave.equals(DefinicoesConfiguracoesAvancadasUnidadeNegocio.//
              INTEGRACAO_EXTERNA_ECOMMERCE_{nomeConstanteInseridaIntegracao}_HABILITADO.getChave())
              && Boolean.parseBoolean(valor)) {
            integracoesExternasAtivas.add(IntegracaoConstants.INTEGRACAO_{nomeConstanteInseridaIntegracao});
          }
          
         /**
          * Adicionar o para cada "processarEvento..."
          *
          */
          IntegracaoConstants.INTEGRACAO_{nomeConstanteInseridaIntegracao}