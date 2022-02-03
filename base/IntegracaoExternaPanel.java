  /**
   * Processa as alterações visuais de acordo com a Integração selecionada.
   */
  private void processaAlteracaoIntegracao() {
    if (comboBoxIntegracao.getSelectedItem() == null) {
      tabbedPane.removeAll();
      tabbedPane.setVisible(false);

      return;
    }
    else {
      tabbedPane.setVisible(true);
    }

    integracaoSelecionada = ((PossibleValue) comboBoxIntegracao.getSelectedItem()).getValueAsChar();

    switch (integracaoSelecionada) {
    ....
      // Remover as integrações que não serão usadas
      case IntegracaoConstants.INTEGRACAO_{nomeConstanteInseridaIntegracao}:
        configuraAbasAtivas(
            new Aba(integracaoSaidaEmbalagemListing,
            "IntegracaoExternaOperationPanel.ui.abaIntegracaoSaidaEmbalagem"),
            new Aba(integracaoEntradaOrcamentoListing,
            "IntegracaoExternaOperationPanel.ui.abaIntegracaoEntradaOrcamento"),
            new Aba(integracaoEntradaPessoaListing,
            "IntegracaoExternaOperationPanel.ui.abaIntegracaoEntradaPessoa"),
            new Aba(integracaoEntradaClienteListing,
            "IntegracaoExternaOperationPanel.ui.abaIntegracaoEntradaCliente"),
            new Aba(integracaoSaidaCfeListing,
            "IntegracaoExternaOperationPanel.ui.abaIntegracaoSaidaCfe"),
            new Aba(integracaoSaidaNfeListing,
            "IntegracaoExternaOperationPanel.ui.abaIntegracaoSaidaNfe"),
            new Aba(integracaoSaidaNfceListing,
            "IntegracaoExternaOperationPanel.ui.abaIntegracaoSaidaNfce")
        );
        break;

      default:
        throw new IllegalArgumentException("Integração " + integracaoSelecionada + " não tratada!");
    }