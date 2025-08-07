from typing import List

class MockAPI:
    """
    Esta classe simula as chamadas para sua API interna.
    """
    def get_produtos_do_produtor(self, id_produtor: int) -> List[dict]:
        print(f"\n[API MOCK] Buscando todos os produtos para o produtor {id_produtor}...")
        return [
            {"id": 101, "nome": "Glifosato Pro", "descricao": "Herbicida de amplo espectro"},
            {"id": 102, "nome": "Adubo Super Simples", "descricao": "Fertilizante fosfatado"},
            {"id": 103, "nome": "Tordon XT", "descricao": "Herbicida para pastagem"},
            {"id": 107, "nome": "Tordon", "descricao": "Herbicida para pastagem"},
            {"id": 108, "nome": "TordonXT", "descricao": "Herbicida para pastagem"},
            {"id": 109, "nome": "Tordon H", "descricao": "Herbicida para pastagem"},
            {"id": 110, "nome": "Tordon X", "descricao": "Herbicida para pastagem"},
            {"id": 104, "nome": "Óleo Mineral Assist", "descricao": "Adjuvante agrícola"},
        ]
    
    def get_produtos_em_estoque(self, id_produtor: int, produtos: List[str]) -> List[dict]:
        print(f"\n[API MOCK] Buscando {produtos} EM ESTOQUE para o produtor {id_produtor}...")
        # Simula que "Glifosato" e "Tordon" estão em estoque
        return [
            {"id": 101, "nome": "Glifosato Pro", "descricao": "Herbicida de amplo espectro", "saldo": 50},
            {"id": 103, "nome": "Tordon XT", "descricao": "Herbicida para pastagem", "saldo": 25},
            {"id": 108, "nome": "TordonXT", "descricao": "Herbicida para pastagem", "saldo": 25},
            {"id": 109, "nome": "Tordon H", "descricao": "Herbicida para pastagem", "saldo": 25},
            {"id": 105, "nome": "Glifosato Atar", "descricao": "Outra marca de Glifosato", "saldo": 10},
        ]

    def get_produtos_mais_consumidos(self, id_produtor: int, produtos: List[str]) -> List[dict]:
        print(f"\n[API MOCK] Buscando consumos de: {produtos} para o produtor {id_produtor}...")
        # Simula que "Tordon XT" é mais usado que outros
        return [
            {"id": 103, "nome": "Tordon XT", "consumo_recente": 150},
            {"id": 103, "nome": "Tordon XT", "consumo_recente": 150},
            {"id": 103, "nome": "Tordon XT", "consumo_recente": 150},
            {"id": 103, "nome": "Tordon XT", "consumo_recente": 150},
            {"id": 109, "nome": "Tordon H", "consumo_recente": 150},
            {"id": 109, "nome": "Tordon H", "consumo_recente": 150},
            {"id": 109, "nome": "Tordon H", "consumo_recente": 150},
            {"id": 102, "nome": "Adubo Super Simples", "consumo_recente": 120},
            {"id": 101, "nome": "Glifosato Pro", "consumo_recente": 80},
        ]

    def get_talhoes_do_produtor(self, id_produtor: int) -> List[dict]:
        print(f"\n[API MOCK] Buscando todos os talhões para o produtor {id_produtor}...")
        return [
            {"id": 201, "nome": "Talhão Norte", "area_ha": 50},
            {"id": 202, "nome": "Campo da Sede", "area_ha": 25},
            {"id": 203, "nome": "Talhão da Estrada", "area_ha": 70},
        ]

    def get_maquinas_do_produtor(self, id_produtor: int) -> List[dict]:
        print(f"\n[API MOCK] Buscando todas as máquinas para o produtor {id_produtor}...")
        return [
            {"id": 301, "nome": "Trator John Deere 6110J", "tipo": "Trator"},
            {"id": 302, "nome": "Pulverizador Autopropelido Uniport 3030", "tipo": "Pulverizador"},
        ]

# Instância única da nossa API simulada para ser importada por outros módulos
api_mock = MockAPI()