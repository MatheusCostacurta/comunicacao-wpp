from typing import List, Optional
from src.comunicacao_wpp_ia.dominio.modelos.produto import Produto
from src.comunicacao_wpp_ia.dominio.modelos.talhao import Talhao
from src.comunicacao_wpp_ia.dominio.modelos.propriedade import Propriedade
from src.comunicacao_wpp_ia.dominio.modelos.imobilizado import Imobilizado
from src.comunicacao_wpp_ia.dominio.modelos.ponto_estoque import PontoEstoque
from src.comunicacao_wpp_ia.dominio.modelos.safra import Safra
from src.comunicacao_wpp_ia.dominio.modelos.responsavel import Responsavel

from src.comunicacao_wpp_ia.dominio.repositorios.repositorio_ferramentas import RepositorioFerramentas
from src.comunicacao_wpp_ia.infraestrutura.adaptadores.saida.clientes_api.agriwin_cliente import AgriwinCliente


class RepoAgriwinFerramentas(RepositorioFerramentas):
    """
    Adaptador que implementa as interfaces de repositório utilizando a API do Agriwin.
    """
    def __init__(self, cliente: AgriwinCliente):
        self._cliente = cliente
        print("[INFRA] Adaptador do Repositório Agriwin inicializado.")

    def buscar_produtos_do_produtor(self, id_produtor: int) -> List[Produto]:
        print(f"\n[API MOCK] Buscando todos os produtos para o produtor {id_produtor}...")
        produtos_data = [
            {
                "id": 101, "nome": "Glifosato Pro", "descricao": "Herbicida de amplo espectro",
                "unidades_medida": ["Litros", "Galões"],
                "ingredientes_ativos": ["Glifosato"]
            },
            {
                "id": 102, "nome": "Adubo Super Simples", "descricao": "Fertilizante fosfatado",
                "unidades_medida": ["Kg", "Sacos"],
                "ingredientes_ativos": ["Fósforo", "Enxofre"]
            },
            {
                "id": 103, "nome": "Tordon XT", "descricao": "Herbicida para pastagem",
                "unidades_medida": ["Litros"],
                "ingredientes_ativos": ["Picloram", "2,4-D"]
            },
            {
                "id": 107, "nome": "Produto B", "descricao": "Herbicida para pastagem",
                "unidades_medida": ["Litros"],
                "ingredientes_ativos": ["Picloram"]
            },
            {
                "id": 108, "nome": "TordonXT", "descricao": "Herbicida para pastagem",
                "unidades_medida": ["Litros"],
                "ingredientes_ativos": ["Picloram", "2,4-D"]
            },
            {
                "id": 109, "nome": "Tordon H", "descricao": "Herbicida para pastagem",
                "unidades_medida": ["Litros"],
                "ingredientes_ativos": ["Picloram", "Halauxifen-metil"]
            },
            {
                "id": 110, "nome": "Tordon X", "descricao": "Herbicida para pastagem",
                "unidades_medida": ["Litros"],
                "ingredientes_ativos": ["Picloram"]
            },
            {
                "id": 104, "nome": "Óleo Mineral Assist", "descricao": "Adjuvante agrícola",
                "unidades_medida": ["Litros"],
                "ingredientes_ativos": ["Óleo mineral"]
            },
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
    
    def buscar_propriedades_do_produtor(self, id_produtor: int) -> List[Propriedade]:
        print(f"\n[API MOCK] Buscando todas as propriedades para o produtor {id_produtor}...")
        propriedades_data = [
            {"id": 701, "nome": "Fazenda São João"},
            {"id": 702, "nome": "Fazenda Vitória"},
        ]
        return [Propriedade(**data) for data in propriedades_data]
    
    def buscar_maquinas_do_produtor(self, id_produtor: int) -> List[Imobilizado]:
        print(f"\n[API MOCK] Buscando todas as máquinas para o produtor {id_produtor}...")
        imobilizados_data = [
            {
                "id": 301, "nome": "Trator John Deere 6110J", "numero_serie": "JD6110JBR",
                "horimetro_inicio": 1250.5, "horimetro_fim": None
            },
            {
                "id": 302, "nome": "Pulverizador Autopropelido Uniport 3030", "numero_serie": "UN3030PR",
                "horimetro_inicio": 875.0, "horimetro_fim": None
            },
             {
                "id": 303, "nome": "Trator Valtra A950", "numero_serie": "VTA950SP",
                "horimetro_inicio": 2100.0, "horimetro_fim": None
            },
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
            {
                "id": 500, "nome": "Safra 2025/2026", "ano_inicio": 2025, "ano_termino": 2026,
                "data_inicio": "2025-09-01", "data_termino": "2026-08-31"
            },
            {
                "id": 501, "nome": "Safra 2024/2025", "ano_inicio": 2024, "ano_termino": 2025,
                "data_inicio": "2024-09-01", "data_termino": "2025-08-31"
            },
            {
                "id": 502, "nome": "Safra 2023/2024", "ano_inicio": 2023, "ano_termino": 2024,
                "data_inicio": "2023-09-01", "data_termino": "2024-08-31"
            },
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
    