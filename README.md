# Assistente IA para Registro de Consumo Agrícola via WhatsApp

![Python](https://img.shields.io/badge/python-3.10-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-05998b)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)

Este projeto implementa um assistente inteligente que permite a produtores rurais registrarem o consumo de insumos agrícolas de forma simples e rápida, enviando uma mensagem de texto, áudio ou imagem pelo WhatsApp.

## 📖 Sobre o Projeto

O objetivo principal é reduzir a fricção no lançamento de dados de consumo no campo. O produtor ou operador de máquina pode simplesmente enviar uma mensagem como "gastei 20kg de adubo no talhão da sede" e a aplicação, utilizando um modelo de linguagem (LLM), orquestra todo o processo de validação, busca de informações no sistema Agriwin e, finalmente, o registro do consumo.

### Funcionalidades Principais

* **Comunicação via WhatsApp:** Integrado com a Z-API para receber e responder mensagens.
* **Processamento de Linguagem Natural:** Utiliza a API da Groq com modelos da Meta (Llama 3) para entender a intenção do usuário e extrair dados estruturados de texto não estruturado.
* **Arquitetura Hexagonal:** O núcleo da aplicação é isolado de detalhes de infraestrutura, permitindo trocar facilmente o provedor de LLM, o serviço de mensageria ou o banco de dados de memória.
* **Agente com Ferramentas (Tools):** O assistente utiliza um conjunto de "ferramentas" para interagir com um sistema externo (API Agriwin) para buscar dados de produtos, talhões, safras, etc.
* **Gerenciamento de Conversa:** Mantém o estado da conversa para interações de múltiplos turnos (ex: fazer perguntas quando faltam informações).

---

## 🏛️ Arquitetura

O projeto foi construído seguindo os princípios da **Arquitetura Hexagonal (Portas e Adaptadores)**. Isso garante um baixo acoplamento e uma alta coesão, separando a lógica de negócio das preocupações com tecnologia e integrações externas.

* **Domínio (`src/comunicacao_wpp_ia/dominio`):** Contém a lógica de negócio pura, modelos (Pydantic), serviços de domínio e as interfaces dos repositórios (Portas). Não depende de nenhuma outra camada.
* **Aplicação (`src/comunicacao_wpp_ia/aplicacao`):** Orquestra o fluxo de dados e os casos de uso. Define as Portas (interfaces) que a infraestrutura deve implementar e depende apenas do Domínio.
* **Infraestrutura (`src/comunicacao_wpp_ia/infraestrutura`):** Implementa os Adaptadores. É a camada mais externa, responsável por interagir com tecnologias como a API do WhatsApp (Z-API), a API do LLM (Groq), o banco de dados de memória (Redis) e a API do ERP (Agriwin).

```
Mundo Externo <--> [Adaptadores] <--> [Portas] <--> Aplicação <--> Domínio
```

---

## 🚀 Tecnologias Utilizadas

* **Linguagem:** Python 3.10
* **Framework API:** FastAPI & Uvicorn
* **IA & LLM:** LangChain, Groq (Llama 3)
* **Banco de Dados (Memória):** Redis
* **Validação de Dados:** Pydantic
* **Containerização:** Docker & Docker Compose
* **Dependências:** `requirements.txt`

---

## 🏁 Começando

Siga os passos abaixo para configurar e executar o projeto em seu ambiente local.

### Pré-requisitos

* [Python 3.10+](https://www.python.org/downloads/)
* [Docker](https://www.docker.com/products/docker-desktop/) e [Docker Compose](https://docs.docker.com/compose/install/)
* Uma conta e chave de API da [Groq](https://console.groq.com/keys)
* Acesso a uma instância da [Z-API](https://www.z-api.io/)

### ⚙️ Configuração do Ambiente

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/MatheusCostacurta/comunicacao-wpp.git
    cd comunicacao-wpp
    ```

2.  **Crie o arquivo de ambiente:**
    Crie um arquivo chamado `.env` na raiz do projeto e preencha com suas credenciais. Você pode usar o arquivo de exemplo como base:
    ```bash
    cp .env.example .env
    ```

3.  **Preencha o `.env` com suas chaves:**
    ```env
    # 'dev' para usar memória local, 'prod' para usar Redis do Docker
    AMBIENTE="dev"

    # Suas credenciais da IA
    OPENAI_API_KEY="SUA_CHAVE_OPENAI"

    # URL da sua instância Z-API
    ZAPI_INSTANCIA_ID=
    ZAPI_INSTANCIA_TOKEN=
    ZAPI_CLIENTE_TOKEN=
    ZAPI_URL_BASE="https://api.z-api.io"

    # Configuração do Redis (usado quando AMBIENTE=prod)
    REDIS_HOST=wpp-redis
    REDIS_PORT=6379
    ```

---

### 🖥️ Rodando Localmente (Ambiente de Desenvolvimento)

Este modo é ideal para desenvolvimento, pois utiliza o Uvicorn com hot-reload.

1.  **Crie e ative um ambiente virtual (Opcional):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

2.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Inicie a API:**
    ```bash
    python main.py
    ```

    A API estará disponível em `http://localhost:8000`.

### 🐳 Rodando com Docker (Ambiente de Produção)

Este é o método recomendado para produção. Ele sobe a aplicação FastAPI e um serviço do Redis, ambos em contêineres Docker.

1.  **Certifique-se de que o Docker está em execução.**

2.  **Altere o `.env` para produção:**
    ```env
    AMBIENTE="prod"
    ```

3.  **Construa e suba os contêineres:**
    ```bash
    docker-compose up -d --build
    ```

    * `--build`: Força a reconstrução da imagem da aplicação se houver mudanças no código.
    * `-d`: Executa os contêineres em modo "detached" (em segundo plano).

4.  **Verifique os logs (Opcional):**
    ```bash
    docker-compose logs -f app
    ```

5.  **Para derrubar os contêineres:**
    ```bash
    docker-compose down
    ```

---

## 🧪 Testando a Aplicação

A principal forma de interagir com a aplicação é através do webhook da Z-API.

1.  **Configure o Webhook na Z-API:**
    * No painel da sua instância Z-API, configure o webhook de mensagens recebidas (`/webhook/zapi`) para apontar para o endereço da sua aplicação. Se estiver rodando localmente, você precisará de uma ferramenta como o [ngrok](https://ngrok.com/) para expor sua porta `8000` para a internet.

2.  **Use a Coleção do Postman:**
    * Importe o arquivo `postman/comunicacao-wpp-api.postman_collection.json` no seu Postman.
    * Use o request "Receber Webhook Z-API" para simular o envio de mensagens para o endpoint `http://localhost:8000/webhook/zapi`.
    * Altere o `body` do request para testar diferentes mensagens e cenários.

---