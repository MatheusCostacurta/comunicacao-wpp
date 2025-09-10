class ErroDominio(Exception):
    """Classe base para exceções de domínio."""
    pass

class MultiplosProdutoresError(ErroDominio):
    """Lançada quando um responsável tem acesso a mais de um produtor."""
    pass

class NenhumProdutorEncontradoError(ErroDominio):
    """Lançada quando um responsável não tem acesso a nenhum produtor."""
    pass