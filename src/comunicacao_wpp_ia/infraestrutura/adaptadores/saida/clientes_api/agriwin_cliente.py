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
        self._usuario = os.getenv("AGRIWIN_USUARIO", "secreto")
        self._senha = os.getenv("AGRIWIN_SENHA", "secreto")
        self._token: Optional[str] = None
        self._url_base_atual: Optional[str] = None
        print("[INFRA] AgriwinClient inicializado.")

    def _autenticar(self) -> None:
        """
        Tenta autenticar em cada uma das URLs base fornecidas.
        Armazena o token e a URL ativa na primeira autenticação bem-sucedida.
        """
        print("[AGRIWIN CLIENT] Tentando autenticar...")
        endpoint_login = "/api/v1/autenticacao" # Exemplo de endpoint
        
        for url in self._base_urls:
            try:
                url_completa = f"{url.rstrip('/')}{endpoint_login}"
                print(f"[AGRIWIN CLIENT] Tentando login em {url_completa}...")
                response = requests.post(url_completa, json={"usuario": self._usuario, "senha": self._senha})
                
                if response.status_code == 200:
                    self._token = response.json().get("token")
                    self._url_base_atual = url
                    print(f"[AGRIWIN CLIENT] Autenticação bem-sucedida na URL: {self._url_base_atual}")
                    return
                else:
                    print(f"[AGRIWIN CLIENT] Falha na autenticação em {url}: Status {response.status_code}")

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
        print(f"[AGRIWIN CLIENT] Executando GET em: {url}")
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status() # Lança exceção para status 4xx/5xx
        return response

    def post(self, endpoint: str, data: dict) -> requests.Response:
        """Executa uma requisição POST para um endpoint da API Agriwin."""
        headers = self._get_headers()
        url = f"{self._url_base_atual.rstrip('/')}{endpoint}"
        print(f"[AGRIWIN CLIENT] Executando POST em: {url}")
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response