from datetime import date

class JsonUtilidade:
    @staticmethod
    def serializar_para_json(dados):
        if hasattr(dados, 'model_dump'): # Para objetos Pydantic
            return dados.model_dump(mode='json')
        if isinstance(dados, list): # Para listas de objetos
            return [JsonUtilidade.serializar_para_json(item) for item in dados]
        if isinstance(dados, dict): # Para dicionários
            return {k: JsonUtilidade.serializar_para_json(v) for k, v in dados.items()}
        if isinstance(dados, date):
            return dados.isoformat()
        return dados