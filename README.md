# Trabalho Prático - Teste de Software

[![CI](https://github.com/EoSingle/DCC089-Teste_de_Software/actions/workflows/ci.yml/badge.svg)](https://github.com/EoSingle/DCC089-Teste_de_Software/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/EoSingle/DCC089-Teste_de_Software/branch/main/graph/badge.svg)](https://codecov.io/gh/EoSingle/DCC089-Teste_de_Software)

Repositório criado para o Trabalho Prático da disciplina de Teste de Software. O objetivo deste projeto é desenvolver um sistema simples para evidenciar como a implementação de testes automatizados auxilia na manutenção, refatoração e evolução de um sistema de software.

## 1. Membros do Grupo
* Lucas Albano Olive Cruz
* Romana Gallete Mota

## 2. Explicação do Sistema
O sistema escolhido é um **Motor de Validação de Flags e Pontuação para competições de CTF (Capture The Flag)**, desenvolvido como uma API REST. 

O sistema simula o backend de uma plataforma de cibersegurança e inclui as seguintes funcionalidades mínimas para interação via endpoints:
* **Cadastro de Desafios:** Rota para inserir novos desafios com pontuação base e a flag correta.
* **Submissão de Flags:** Rota que permite a um usuário/equipe enviar uma flag para um desafio específico.
* **Validação e Pontuação:** Lógica interna para verificar se a flag está correta, garantir que a equipe já não pontuou naquele desafio anteriormente e computar os pontos.

## 3. Tecnologias Utilizadas
Para o desenvolvimento e validação da aplicação, adotamos as seguintes ferramentas:

* **Backend:** Python 3 com FastAPI.
* **Banco de Dados & Cache:** MariaDB e Redis.
* **Framework de Testes:** PyTest.
* **Ferramenta de Cobertura:** `pytest-cov`.
* **Controle de Versão:** Git e GitHub.

## 4. Arquitetura do Sistema

O projeto segue uma arquitetura em camadas, separando responsabilidades para facilitar os testes:

```
app/
├── main.py          # Ponto de entrada: cria a aplicação FastAPI e registra middlewares
├── config.py        # Configurações via variáveis de ambiente (DATABASE_URL)
├── database.py      # Engine e sessão SQLAlchemy; dependência get_db para injeção
├── models.py        # Modelos ORM: Challenge, Team, Submission
├── schemas.py       # Schemas Pydantic para validação de entrada e saída
├── flag_utils.py    # Funções puras: hash_flag (SHA-256) e validate_flag
├── scoring.py       # Funções puras: calculate_points (decay) e is_first_blood
├── services.py      # Lógica de negócio com acesso ao banco de dados
├── routers.py       # Endpoints FastAPI; traduz HTTP ↔ chamadas de serviço
└── exceptions.py    # Exceções de domínio (ConflictError)
```

As **funções puras** (`flag_utils`, `scoring`) são testadas sem dependências. Os **serviços** são testados com SQLite em memória. Os **endpoints** são testados via `TestClient` do FastAPI.

## 5. Endpoints da API

Todos os endpoints estão sob o prefixo `/api/v1`.

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/health` | Verifica o status da API e a conectividade com o banco |
| `POST` | `/challenges` | Cria um novo desafio |
| `GET` | `/challenges` | Lista todos os desafios (suporta `?category=`) |
| `GET` | `/challenges/:id` | Retorna um desafio com contagem de solves |
| `POST` | `/teams` | Cria uma nova equipe |
| `GET` | `/teams` | Lista todas as equipes |
| `GET` | `/teams/:id` | Retorna uma equipe pelo ID |
| `GET` | `/teams/:id/solves` | Histórico de flags resolvidas pela equipe |
| `POST` | `/submissions` | Submete uma flag para validação |
| `GET` | `/scoreboard` | Placar geral (suporta `?limit=` e `?offset=`) |

## 5. Como Executar os Testes Localmente

**Pré-requisito:** Python 3.11+

```bash
# 1. Clone o repositório e entre na pasta
git clone <url-do-repositorio>
cd <nome-do-repositorio>

# 2. Crie e ative um ambiente virtual
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate           # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Execute todos os testes
pytest

# 5. Execute com relatório de cobertura
pytest --cov=app --cov-report=term-missing
```

Os testes utilizam SQLite em memória — nenhum serviço externo (MariaDB, Redis) é necessário para rodá-los.
