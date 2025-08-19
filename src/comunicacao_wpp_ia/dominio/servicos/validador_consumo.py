from typing import List, Tuple
from src.comunicacao_wpp_ia.dominio.modelos.consumo import Consumo

class ValidadorConsumo:
    """
    Serviço de domínio responsável por validar a consistência e a completude de um objeto de Consumo.
    """
    
    _campos_obrigatorios = [
        "produto_mencionado", 
        "quantidade", 
        "talhao_mencionado",
        "ponto_estoque_mencionado",
        "data_mencionada"
    ]

    _mapa_perguntas = {
        "produto_mencionado": "Qual foi o produto utilizado?",
        "quantidade": "Qual foi a quantidade consumida?",
        "talhao_mencionado": "Em qual propriedade ou talhão foi feita a aplicação?",
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
                campos_faltantes.append(cls._mapa_perguntas[campo])

        #TODO: preciso ver ainda como fazer isso, por causa que pode ser um ou outro
        # Regra específica: se o rateio é por talhão, o talhão precisa ser informado.
        if consumo.tipo_rateio == 'talhao' and not consumo.talhao_mencionado:
             if cls._mapa_perguntas["talhao_mencionado"] not in campos_faltantes:
                campos_faltantes.append(cls._mapa_perguntas["talhao_mencionado"])
        
        if campos_faltantes:
            return False, campos_faltantes
        
        return True, []