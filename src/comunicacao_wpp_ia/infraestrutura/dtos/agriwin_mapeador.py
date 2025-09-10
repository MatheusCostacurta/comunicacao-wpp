from datetime import datetime

# --- Modelos de Domínio (Camada Interna) ---
from src.comunicacao_wpp_ia.dominio.modelos.produto import Produto
from src.comunicacao_wpp_ia.dominio.modelos.talhao import Talhao
from src.comunicacao_wpp_ia.dominio.modelos.propriedade import Propriedade
from src.comunicacao_wpp_ia.dominio.modelos.imobilizado import Imobilizado
from src.comunicacao_wpp_ia.dominio.modelos.ponto_estoque import PontoEstoque
from src.comunicacao_wpp_ia.dominio.modelos.safra import Safra
from src.comunicacao_wpp_ia.dominio.modelos.responsavel import Responsavel

# --- DTOs da Infraestrutura (Camada Externa) ---
from src.comunicacao_wpp_ia.infraestrutura.dtos.agriwin_dtos import (
    ProdutoAgriwinDTO,
    PlantioAgriwinDTO,
    ImobilizadoAgriwinDTO,
    PontoEstoqueAgriwinDTO,
    SafraAgriwinDTO,
    ResponsavelAgriwinDTO
)

class AgriwinMapeador:
    """
    Componente da Camada Anti-Corrupção.
    É o único local que "conhece" tanto os DTOs da API Agriwin quanto os
    Modelos de Domínio, sendo responsável por traduzir um no outro.
    """
    @staticmethod
    def para_produto_dominio(dto: ProdutoAgriwinDTO) -> Produto:
        unidades = [um.sigla for um in (dto.unidades_medida or [])]
        ingredientes = [ia.nome for ia in (dto.ingredientes_ativo or [])]

        return Produto(
            id=dto.identificador,
            nome=dto.nome,
            unidades_medida=unidades,
            ingredientes_ativos=ingredientes
        )

    @staticmethod
    def para_talhao_dominio(dto: PlantioAgriwinDTO) -> Talhao:
        return Talhao(
            id=dto.talhao.identificador,
            nome=dto.talhao.descricao,
            area_ha=0.0  # O endpoint de plantios não fornece a área
        )

    @staticmethod
    def para_propriedade_dominio(dto: PlantioAgriwinDTO) -> Propriedade:
        return Propriedade(
            id=dto.talhao.propriedade.identificador,
            nome=dto.talhao.propriedade.descricao
        )
    
    @staticmethod
    def para_imobilizado_dominio(dto: ImobilizadoAgriwinDTO) -> Imobilizado:
        return Imobilizado(
            id=dto.identificador,
            nome=dto.descricao, # Mapeia 'descricao' do DTO para 'nome' no domínio
            ativo=dto.ativo if dto.ativo is not None else True,
            numero_serie=dto.numero_serie,
            horimetro_atual=dto.horimetro_atual
        )

    @staticmethod
    def para_ponto_estoque_dominio(dto: PontoEstoqueAgriwinDTO) -> PontoEstoque:
        return PontoEstoque(
            id=dto.identificador,
            nome=dto.descricao, # Mapeia 'descricao' do DTO para 'nome' no domínio
            ativo=dto.ativo if dto.ativo is not None else True
        )
    
    @staticmethod
    def para_safra_dominio(dto: SafraAgriwinDTO) -> Safra:
        return Safra(
            id=dto.identificador,
            nome="Safra " + str(dto.ano_inicio) + " - " + str(dto.ano_termino),
            ano_inicio=dto.ano_inicio,
            ano_termino=dto.ano_termino,
            data_inicio=datetime.strptime(dto.data_inicio, "%d/%m/%Y").date(),
            data_termino=datetime.strptime(dto.data_termino, "%d/%m/%Y").date()
        )

    @staticmethod
    def para_responsavel_dominio(dto: ResponsavelAgriwinDTO) -> Responsavel:
        return Responsavel(
            id=dto.identificador,
            nome=dto.nome,
            nome_fantasia=dto.nome_fantasia,
            telefone=dto.telefone
        )