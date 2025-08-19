from typing import Dict, List, Tuple, Optional
from src.comunicacao_wpp_ia.dominio.modelos.produto import Produto
from src.comunicacao_wpp_ia.dominio.modelos.talhao import Talhao
from src.comunicacao_wpp_ia.dominio.modelos.imobilizado import Imobilizado
from src.comunicacao_wpp_ia.dominio.modelos.ponto_estoque import PontoEstoque
from src.comunicacao_wpp_ia.dominio.modelos.safra import Safra
from src.comunicacao_wpp_ia.dominio.modelos.responsavel import Responsavel

from src.comunicacao_wpp_ia.dominio.repositorios.repositorio_produto import RepositorioProduto
from src.comunicacao_wpp_ia.dominio.repositorios.repositorio_imobilizado import RepositorioImobilizado
from src.comunicacao_wpp_ia.dominio.repositorios.repositorio_talhao import RepositorioTalhao
from src.comunicacao_wpp_ia.dominio.repositorios.repositorio_ponto_estoque import RepositorioPontoEstoque
from src.comunicacao_wpp_ia.dominio.repositorios.repositorio_safra import RepositorioSafra
from src.comunicacao_wpp_ia.dominio.repositorios.repositorio_responsavel import RepositorioResponsavel

class RotasAgriwin(
    RepositorioProduto, RepositorioImobilizado, RepositorioTalhao,
    RepositorioPontoEstoque, RepositorioSafra, RepositorioResponsavel
):
    """
    Adaptador que implementa as interfaces de repositório utilizando a API do Agriwin.
    """
    def __init__(self):
        print("[INFRA] Adaptador do Repositório Agriwin inicializado.")

    def buscar_produtos_do_produtor(self, id_produtor: int) -> List[Produto]:
        print(f"\n[API MOCK] Buscando todos os produtos para o produtor {id_produtor}...")
        produtos_data = [
            {"id": 101, "nome": "Glifosato Pro", "descricao": "Herbicida de amplo espectro"},
            {"id": 102, "nome": "Adubo Super Simples", "descricao": "Fertilizante fosfatado"},
            {"id": 103, "nome": "Tordon XT", "descricao": "Herbicida para pastagem"},
            {"id": 107, "nome": "Tordon", "descricao": "Herbicida para pastagem"},
            {"id": 108, "nome": "TordonXT", "descricao": "Herbicida para pastagem"},
            {"id": 109, "nome": "Tordon H", "descricao": "Herbicida para pastagem"},
            {"id": 110, "nome": "Tordon X", "descricao": "Herbicida para pastagem"},
            {"id": 104, "nome": "Óleo Mineral Assist", "descricao": "Adjuvante agrícola"},
        ]

        return [Produto(**data) for data in produtos_data]
    
    def buscar_produtos_em_estoque(self, id_produtor: int, produtos: List[str]) -> List[Produto]:
        print(f"\n[API MOCK] Buscando {produtos} EM ESTOQUE para o produtor {id_produtor}...")
        # Simula que "Glifosato" e "Tordon" estão em estoque
        produtos_data = [
            {"id": 101, "nome": "Glifosato Pro", "descricao": "Herbicida de amplo espectro", "saldo": 50},
            {"id": 103, "nome": "Tordon XT", "descricao": "Herbicida para pastagem", "saldo": 25},
            {"id": 108, "nome": "TordonXT", "descricao": "Herbicida para pastagem", "saldo": 25},
            {"id": 109, "nome": "Tordon H", "descricao": "Herbicida para pastagem", "saldo": 25},
            {"id": 105, "nome": "Glifosato Atar", "descricao": "Outra marca de Glifosato", "saldo": 10},
        ]
    
        return [Produto(**data) for data in produtos_data]

    def buscar_produtos_mais_consumidos(self, id_produtor: int, produtos: List[str]) -> List[Produto]:
        print(f"\n[API MOCK] Buscando consumos de: {produtos} para o produtor {id_produtor}...")
        # Simula que "Tordon XT" é mais usado que outros
        produtos_data = [
            {"id": 103, "nome": "Tordon XT", "descricao": "Herbicida para pastagem", "consumo_recente": 150},
            {"id": 103, "nome": "Tordon XT", "descricao": "Herbicida para pastagem", "consumo_recente": 150},
            {"id": 103, "nome": "Tordon XT", "descricao": "Herbicida para pastagem", "consumo_recente": 150},
            {"id": 103, "nome": "Tordon XT", "descricao": "Herbicida para pastagem", "consumo_recente": 150},
            {"id": 109, "nome": "Tordon H", "descricao": "Herbicida para pastagem", "consumo_recente": 150},
            {"id": 109, "nome": "Tordon H", "descricao": "Herbicida para pastagem", "consumo_recente": 150},
            {"id": 109, "nome": "Tordon H", "descricao": "Herbicida para pastagem", "consumo_recente": 150},
            {"id": 102, "nome": "Adubo Super Simples", "descricao": "Fertilizante fosfatado", "consumo_recente": 120},
            {"id": 101, "nome": "Glifosato Pro", "descricao": "Herbicida de amplo espectro", "consumo_recente": 80},
        ]
    
        return [Produto(**data) for data in produtos_data]

    def buscar_talhoes_do_produtor(self, id_produtor: int) -> List[Talhao]:
        print(f"\n[API MOCK] Buscando todos os talhões para o produtor {id_produtor}...")
        talhoes_data = [
            {"id": 201, "nome": "Talhão Norte", "area_ha": 50},
            {"id": 202, "nome": "Campo da Sede", "area_ha": 25},
            {"id": 203, "nome": "Talhão da Estrada", "area_ha": 70},
        ]

        return [Talhao(**data) for data in talhoes_data]
    
    def buscar_maquinas_do_produtor(self, id_produtor: int) -> List[Imobilizado]:
        print(f"\n[API MOCK] Buscando todas as máquinas para o produtor {id_produtor}...")
        imobilizados_data = [
            {"id": 301, "nome": "Trator John Deere 6110J", "tipo": "Trator"},
            {"id": 302, "nome": "Pulverizador Autopropelido Uniport 3030", "tipo": "Pulverizador"},
        ]
    
        return [Imobilizado(**data) for data in imobilizados_data]
    
    def buscar_pontos_estoque_do_produtor(self, id_produtor: int) -> List[PontoEstoque]:
        print(f"\n[API MOCK] Buscando pontos de estoque para o produtor {id_produtor}...")
        estoque_data = [
            {"id": 401, "nome": "Galpão Sede"},
            {"id": 402, "nome": "Depósito Retiro"},
            {"id": 403, "nome": "Sede"},
        ]
        return [PontoEstoque(**data) for data in estoque_data]
    
    def buscar_safras_do_produtor(self, id_produtor: int) -> List[Safra]:
        print(f"\n[API MOCK] Buscando safras para o produtor {id_produtor}...")
        safra_data = [
            {"id": 501, "nome": "Safra 24/25 Soja", "esta_ativa": True},
            {"id": 502, "nome": "Safrinha 24/25 Milho", "esta_ativa": False},
            {"id": 503, "nome": "Safra 23/24 Soja", "esta_ativa": False},
        ]
        return [Safra(**data) for data in safra_data]
    
    def buscar_responsaveis_do_produtor(self, id_produtor: int) -> List[Responsavel]:
        print(f"\n[API MOCK] Buscando responsáveis para o produtor {id_produtor}...")
        responsavel_data = [
            {"id": 601, "nome": "João da Silva", "telefone": "+5511988882222"},
            {"id": 602, "nome": "Maria Oliveira", "telefone": "+5541999991111"},
        ]
        return [Responsavel(**data) for data in responsavel_data]
    
    def buscar_responsavel_por_telefone(self, id_produtor: int, telefone: str) -> Optional[Responsavel]:
        print(f"\n[API MOCK] Buscando responsável pelo telefone {telefone}...")
        todos = self.buscar_responsaveis_do_produtor(id_produtor)
        for r in todos:
            if r.telefone == telefone:
                return r
        return None
    
    def salvar_consumo(self, dados_consumo: Dict) -> Tuple[int, Dict]:
        """
        Simula o POST para salvar os dados de consumo na API interna.
        Retorna uma tupla contendo o status_code e o corpo da resposta em JSON.
        """
        print(f"\n[API MOCK] Recebido POST para salvar consumo: {dados_consumo}")
        
        # Simulação de erro de validação da API (Internal Server Error)
        if dados_consumo.get("quantidade") == "20 kg" and dados_consumo.get("id_produto") == 102:
            response_body = {
                "error": "VALIDATION_ERROR",
                "message": "Erro de validação: A quantidade '20 kg' para 'Adubo Super Simples' excede o limite permitido por aplicação."
            }
            return 500, response_body
        
        # Simulação de sucesso (OK)
        response_body = {
            "status": "sucesso",
            "message": f"Consumo do produto ID {dados_consumo.get('id_produto')} registrado com sucesso no talhão ID {dados_consumo.get('id_talhao')}.",
            "registro_id": 12345 
        }
        return 200, response_body
