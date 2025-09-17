import os
import requests
from typing import Optional, Dict

class AgriwinCliente:
    """
    Cliente centralizado para interagir com a API Agriwin.
    Gerencia a autenticação e as requisições HTTP.
    """
    _tokens_cache: Dict[str, str] = {} # Cache de tokens por base_url
    todas_bases_urls = [
        "https://sistema.agriwin.com.br",
        "https://castrolanda.agriwin.com.br",
        "https://frisia.agriwin.com.br",
        "https://capal.agriwin.com.br",
        "https://demo.agriwin.com.br",
    ]

    def __init__(self):
        self._usuario = os.getenv("AGRIWIN_USUARIO")
        self._senha = os.getenv("AGRIWIN_SENHA")
        if not self._usuario or not self._senha:
            raise ValueError("As variáveis de ambiente 'AGRIWIN_USUARIO' e 'AGRIWIN_SENHA' não foram configuradas.")
        print("[INFRA] AgriwinClient inicializado.")

    def _autenticar(self, base_url: str) -> None:
        """
        Tenta autenticar em cada uma das URLs base fornecidas.
        Armazena o token e a URL ativa na primeira autenticação bem-sucedida.
        """
        print("[AGRIWIN CLIENT] Tentando autenticar...")
        endpoint_login = "/api/v1/autenticacao"
        url_completa = f"{base_url.rstrip('/')}{endpoint_login}"
        
        try:
            payload = {"login": self._usuario, "senha": self._senha}
            response = requests.post(url_completa, json=payload)
            response.raise_for_status() # Lança exceção para status 4xx/5xx

            response_data = response.json()
            dados = response_data.get("dados")
            token = dados.get("token") if isinstance(dados, dict) else None

            if not token:
                raise ValueError("Token não encontrado na resposta da API de autenticação.")
            
            print(f"[AGRIWIN CLIENT] Autenticação bem-sucedida em {base_url}.")
            self._tokens_cache[base_url] = token # Armazena no cache
            return token

        except requests.exceptions.RequestException as e:
            print(f"[AGRIWIN CLIENT ERROR] Erro ao tentar autenticar em {base_url}: {e}")
            raise ConnectionError(f"Não foi possível autenticar na API Agriwin em {base_url}.")

    def _get_headers(self, base_url: str) -> dict:
        """Obtém um token (do cache ou novo) e retorna os headers."""
        token = self._tokens_cache.get(base_url)
        if not token:
            token = self._autenticar(base_url)
        
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def get(self, base_url: str, endpoint: str, params: Optional[dict] = None) -> requests.Response:
        """Executa uma requisição GET para um endpoint da API Agriwin."""
        headers = self._get_headers(base_url)
        url = f"{base_url.rstrip('/')}{endpoint}"
        
        if params:
            # Constrói a query string manualmente para evitar a codificação do '='
            # ! NAO É BOM BASE64 PARA URL - AGR-3865
            query_string = "&".join([f"{key}={value}" for key, value in params.items()])
            url = f"{url}?{query_string}"

        print(f"[AGRIWIN CLIENT] Executando GET em: {url}")
        response = requests.get(url, headers=headers)
        
        # Se o token expirou (401), limpa o cache e tenta de novo
        if response.status_code == 401 and base_url in self._tokens_cache:
            print("[AGRIWIN CLIENT] Token possivelmente expirado. Tentando reautenticar...")
            del self._tokens_cache[base_url]
            return self.get(base_url, endpoint, params)
        
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(f"[AGRIWIN CLIENT ERROR] A API retornou um erro: {err}")
            print(f"[AGRIWIN CLIENT ERROR] Corpo da resposta: {response.text}")
            raise err
            
        return response

    def post(self, base_url: str, endpoint: str, data: dict) -> requests.Response:
        """Executa uma requisição POST para um endpoint da API Agriwin."""
        headers = self._get_headers(base_url)
        url = f"{base_url.rstrip('/')}{endpoint}"
        print(f"[AGRIWIN CLIENT] Executando POST em: {url}")
        response = requests.post(url, headers=headers, json=data)

        # Se o token expirou (401), limpa o cache e tenta de novo
        if response.status_code == 401 and base_url in self._tokens_cache:
            print("[AGRIWIN CLIENT] Token possivelmente expirado. Tentando reautenticar...")
            del self._tokens_cache[base_url]
            return self.post(base_url, endpoint, data)
        
        response.raise_for_status()
        return response