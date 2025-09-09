from typing import List, Tuple
from src.comunicacao_wpp_ia.aplicacao.dtos.consumo_informado import ConsumoInformado

class ValidadorConsumo:
    """
    Serviço de domínio responsável por validar a consistência e a completude de um objeto de Consumo.
    """
    
    _campos_obrigatorios = [
        "produtos_mencionados"
    ]

    _mapa_perguntas = {
        "produtos_mencionados": "Qual foi o produto e quantidade utilizado?",
        "local": "Em qual propriedade/talhão foi feita a aplicação?"
    }

    @classmethod
    def validar(cls, consumo: ConsumoInformado) -> Tuple[bool, List[str]]:
        """
        Verifica se o objeto Consumo possui todos os dados obrigatórios.

        Returns:
            Uma tupla contendo:
            - Um booleano (True se válido, False se inválido).
            - Uma lista com as perguntas correspondentes aos campos faltantes.
        """
        campos_faltantes = []

        # 1. Validação granular da lista de produtos
        if not consumo.produtos_mencionados:
            campos_faltantes.append(cls._mapa_perguntas["produtos_mencionados"])
        else:
            for produto in consumo.produtos_mencionados:
                if not produto.quantidade:
                    campos_faltantes.append(f"Qual foi a quantidade para o produto {produto.nome}?")

        # 2. Validação dos outros campos obrigatórios (não relacionados a produtos)
        for campo in cls._campos_obrigatorios:
            if campo != "produtos_mencionados" and not getattr(consumo, campo):
                chave_pergunta = "local" if "talhao" in campo or "propriedade" in campo else campo  # Remapeia o nome do campo para a pergunta genérica se necessário
                if cls._mapa_perguntas[chave_pergunta] not in campos_faltantes:
                    campos_faltantes.append(cls._mapa_perguntas[chave_pergunta])

        # 3. Validação do local (talhão ou propriedade)
        local_informado = False
        if consumo.tipo_rateio == 'talhao' and consumo.talhoes_mencionados:
            local_informado = True
        elif consumo.tipo_rateio == 'propriedade' and consumo.propriedades_mencionadas:
            local_informado = True
        
        if not local_informado:
            if cls._mapa_perguntas["local"] not in campos_faltantes:
                campos_faltantes.append(cls._mapa_perguntas["local"])
        
        if campos_faltantes:
            return False, campos_faltantes
        
        return True, []