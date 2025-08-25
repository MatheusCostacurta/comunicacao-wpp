from typing import List, Tuple
from src.comunicacao_wpp_ia.dominio.modelos.consumo import Consumo

class ValidadorConsumo:
    """
    Serviço de domínio responsável por validar a consistência e a completude de um objeto de Consumo.
    """
    
    _campos_obrigatorios = [
        "produto_mencionado", 
        "quantidade", 
        "ponto_estoque_mencionado",
        "data_mencionada"
    ]

    _mapa_perguntas = {
        "produto_mencionado": "Qual foi o produto utilizado?",
        "quantidade": "Qual foi a quantidade consumida?",
        "local": "Em qual propriedade/talhão foi feita a aplicação?",
        "ponto_estoque_mencionado": "De qual depósito/ponto de estoque o produto saiu?",
        "data_mencionada": "Em que data foi a aplicação?"
    }

    @classmethod
    def validar(cls, consumo: Consumo) -> Tuple[bool, List[str]]:
        """
        Verifica se o objeto Consumo possui todos os dados obrigatórios.

        Returns:
            Uma tupla contendo:
            - Um booleano (True se válido, False se inválido).
            - Uma lista com as perguntas correspondentes aos campos faltantes.
        """
        campos_faltantes = []
        for campo in cls._campos_obrigatorios:
            if not getattr(consumo, campo):
                chave_pergunta = "local" if "talhao" in campo or "propriedade" in campo else campo  # Remapeia o nome do campo para a pergunta genérica se necessário
                if cls._mapa_perguntas[chave_pergunta] not in campos_faltantes:
                    campos_faltantes.append(cls._mapa_perguntas[chave_pergunta])

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