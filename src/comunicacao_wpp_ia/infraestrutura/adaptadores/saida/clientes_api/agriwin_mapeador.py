from datetime import date

# --- Modelos de Domínio (Camada Interna) ---
from src.comunicacao_wpp_ia.dominio.modelos.produto import Produto, UnidadeMedida, IngredienteAtivo
from src.comunicacao_wpp_ia.dominio.modelos.talhao import Talhao
from src.comunicacao_wpp_ia.dominio.modelos.propriedade import Propriedade
from src.comunicacao_wpp_ia.dominio.modelos.imobilizado import Imobilizado
from src.comunicacao_wpp_ia.dominio.modelos.ponto_estoque import PontoEstoque
from src.comunicacao_wpp_ia.dominio.modelos.safra import Safra
from src.comunicacao_wpp_ia.dominio.modelos.responsavel import Responsavel

# --- DTOs da Infraestrutura (Camada Externa) ---
from src.comunicacao_wpp_ia.infraestrutura.adaptadores.saida.clientes_api.agriwin_dtos import (
    ProdutoAgriwinDTO,
    TalhaoAgriwinDTO,
    PropriedadeAgriwinDTO,
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
    def para_talhao_dominio(dto: TalhaoAgriwinDTO) -> Talhao:
        return Talhao(
            id=dto.identificador,
            nome=dto.nome,
            area_ha=dto.area_ha or 0.0
        )

    @staticmethod
    def para_propriedade_dominio(dto: PropriedadeAgriwinDTO) -> Propriedade:
        return Propriedade(
            id=dto.identificador,
            nome=dto.nome
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
            nome=dto.nome,
            ano_inicio=dto.ano_inicio,
            ano_termino=dto.ano_termino,
            data_inicio=date.fromisoformat(dto.data_inicio), # Converte string para date
            data_termino=date.fromisoformat(dto.data_termino)  # Converte string para date
        )

    @staticmethod
    def para_responsavel_dominio(dto: ResponsavelAgriwinDTO) -> Responsavel:
        return Responsavel(
            id=dto.identificador,
            nome=dto.nome,
            nome_fantasia=dto.nome_fantasia,
            telefone=dto.telefone
        )