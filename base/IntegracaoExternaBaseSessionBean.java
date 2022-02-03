package {pacoteSessionBean};

import {pacotePadrao}.{classeNomeIntegracaoExternaBase};
import {pacotePadrao}.{classeNomeAppLocal};
import javax.ejb.Stateless;
import javax.ejb.TransactionManagement;
import javax.ejb.TransactionManagementType;

/**
 * {@link javax.ejb.SessionBean} para a integração com {nomeIntegracao}.
 */
@Stateless(mappedName = "{classeNomeIntegracaoExternaBase}")
@TransactionManagement(TransactionManagementType.BEAN)
public class {classeIntegracaoSessionBeanNome} extends {classeNomeIntegracaoExternaBase}
    implements {classeNomeAppLocal} {

}