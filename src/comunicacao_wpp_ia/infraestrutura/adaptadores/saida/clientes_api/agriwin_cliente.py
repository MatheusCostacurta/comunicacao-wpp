import os
import requests
from typing import List, Optional, Tuple

class AgriwinCliente:
    """
    Cliente centralizado para interagir com a API Agriwin.
    Gerencia a autenticação e as requisições HTTP.
    """
    def __init__(self, base_urls: List[str]):
        if not base_urls:
            raise ValueError("A lista de URLs base da API Agriwin não pode ser vazia.")
        self._base_urls = base_urls
        self._usuario = os.getenv("AGRIWIN_USUARIO")
        self._senha = os.getenv("AGRIWIN_SENHA")
        if not self._usuario or not self._senha:
            raise ValueError("As variáveis de ambiente 'AGRIWIN_USUARIO' e 'AGRIWIN_SENHA' não foram configuradas.")
        
        self._token: Optional[str] = None
        self._url_base_atual: Optional[str] = None
        print("[INFRA] AgriwinClient inicializado.")

    def _autenticar(self) -> None:
        """
        Tenta autenticar em cada uma das URLs base fornecidas.
        Armazena o token e a URL ativa na primeira autenticação bem-sucedida.
        """
        print("[AGRIWIN CLIENT] Tentando autenticar...")
        endpoint_login = "/api/v1/autenticacao"
        
        for url in self._base_urls:
            try:
                url_completa = f"{url.rstrip('/')}{endpoint_login}"
                payload = {
                    "login": self._usuario,
                    "senha": self._senha
                }
                print(f"[AGRIWIN CLIENT] Tentando login em {url_completa}...")
                response = requests.post(url_completa, json=payload)

                if response.status_code == 200:
                    response_data = response.json()
                    dados = response_data.get("dados")
                    if isinstance(dados, dict):
                        self._token = dados.get("token")

                    if self._token:
                        self._url_base_atual = url
                        print(f"[AGRIWIN CLIENT] Autenticação bem-sucedida. Token extraído com sucesso.")
                        return
                    else:
                        print("[AGRIWIN CLIENT ERROR] Autenticação retornou sucesso (200), mas o token não foi encontrado no JSON com a chave 'token'.")
                    
                else:
                    print(f"[AGRIWIN CLIENT] Falha na autenticação em {url}: Status {response.status_code}")
                    print(f"[AGRIWIN CLIENT] Falha na autenticação em {url}: Status {response.json().get('mensagem')}")

            except requests.exceptions.RequestException as e:
                print(f"[AGRIWIN CLIENT ERROR] Erro ao tentar conectar em {url}: {e}")
                continue # Tenta a próxima URL
        
        raise ConnectionError("Não foi possível autenticar em nenhuma das URLs base da API Agriwin.")

    def _get_headers(self) -> dict:
        """Garante que a autenticação foi feita e retorna os headers necessários."""
        if not self._token or not self._url_base_atual:
            self._autenticar()
        
        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json"
        }

    def get(self, endpoint: str, params: Optional[dict] = None) -> requests.Response:
        """Executa uma requisição GET para um endpoint da API Agriwin."""
        headers = self._get_headers()
        url = f"{self._url_base_atual.rstrip('/')}{endpoint}"
        
        if params:
            # Constrói a query string manualmente para evitar a codificação do '='
            # ! NAO É BOM BASE64 PARA URL - AGR-3865
            query_string = "&".join([f"{key}={value}" for key, value in params.items()])
            url = f"{url}?{query_string}"

        print(f"[AGRIWIN CLIENT] Executando GET em: {url}")
        response = requests.get(url, headers=headers)
        
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(f"[AGRIWIN CLIENT ERROR] A API retornou um erro: {err}")
            print(f"[AGRIWIN CLIENT ERROR] Corpo da resposta: {response.text}")
            raise err
            
        return response

    def post(self, endpoint: str, data: dict) -> requests.Response:
        """Executa uma requisição POST para um endpoint da API Agriwin."""
        headers = self._get_headers()
        url = f"{self._url_base_atual.rstrip('/')}{endpoint}"
        print(f"[AGRIWIN CLIENT] Executando POST em: {url}")
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response