# FireUAI CTF Flags API

[![CI](https://github.com/EoSingle/DCC089-Teste_de_Software/actions/workflows/ci.yml/badge.svg)](https://github.com/EoSingle/DCC089-Teste_de_Software/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/EoSingle/DCC089-Teste_de_Software/branch/main/graph/badge.svg)](https://codecov.io/gh/EoSingle/DCC089-Teste_de_Software)

API REST para validação de flags e pontuação em competições de CTF (Capture The Flag). Desenvolvida como Trabalho Prático da disciplina de Teste de Software, com foco em evidenciar como testes automatizados auxiliam na manutenção e evolução de um sistema.

---

## 1. Membros do Grupo

- Lucas Albano Olive Cruz
- Romana Gallete Mota

---

## 2. Explicação do Sistema

A **FireUAI CTF Flags API** simula o backend de uma plataforma de competição de cibersegurança. Equipes se cadastram, recebem desafios e submetem flags para acumular pontos no placar.

Funcionalidades principais:

- **Cadastro de Desafios:** criação de desafios com flag, pontuação base e dificuldade.
- **Cadastro de Equipes:** registro de equipes participantes.
- **Submissão e Validação de Flags:** verificação da flag, bloqueio de submissão duplicada e cálculo de pontos com bônus de *first blood*.
- **Placar Geral:** ranking das equipes com suporte a paginação.

### Regras de Pontuação

| Situação | Pontos |
|---|---|
| Primeira equipe a resolver (*first blood*) | `base_points + 50` |
| Demais equipes | `base_points - (10 × posição)`, mínimo 10% do base |
| Flag errada | 0 |
| Desafio já resolvido pela equipe | 0 |

---

## 3. Tecnologias Utilizadas

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.11+ com FastAPI |
| Banco de dados | SQLite (dev/testes) · MariaDB (produção) |
| ORM | SQLAlchemy 2.0 |
| Validação | Pydantic v2 |
| Testes | pytest + pytest-cov |
| CI/CD | GitHub Actions |
| Cobertura | Codecov |

---

## 4. Arquitetura do Sistema

O projeto segue uma arquitetura em camadas para facilitar os testes:

```
app/
├── main.py          # Ponto de entrada: cria a aplicação e registra middlewares
├── config.py        # Configurações via variáveis de ambiente (DATABASE_URL)
├── database.py      # Engine e sessão SQLAlchemy; dependência get_db
├── models.py        # Modelos ORM: Challenge, Team, Submission
├── schemas.py       # Schemas Pydantic para validação de entrada e saída
├── flag_utils.py    # Funções puras: hash_flag (SHA-256) e validate_flag
├── scoring.py       # Funções puras: calculate_points (decay) e is_first_blood
├── services.py      # Lógica de negócio com acesso ao banco de dados
├── routers.py       # Endpoints FastAPI; traduz HTTP ↔ chamadas de serviço
└── exceptions.py    # Exceções de domínio (ConflictError)
```

As **funções puras** (`flag_utils`, `scoring`) são testadas sem dependências. Os **serviços** são testados com SQLite em memória. Os **endpoints** são testados via `TestClient` do FastAPI.

---

## 5. Como Utilizar a API

### Iniciando o servidor

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows

pip install -r requirements.txt
uvicorn app.main:app --reload
```

A documentação interativa estará disponível em `http://localhost:8000/docs`.

---

### Exemplos de uso com `curl`

> Todos os endpoints estão sob o prefixo `/api/v1`.

#### Verificar status da API

```bash
curl http://localhost:8000/api/v1/health
```

```json
{ "status": "ok", "database": "connected" }
```

---

#### Criar um desafio

```bash
curl -s -X POST http://localhost:8000/api/v1/challenges \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Web 101",
    "description": "Inspecione os headers HTTP da página alvo.",
    "category": "web",
    "difficulty": "easy",
    "flag": "CTF{hidden_header_found}",
    "base_points": 100
  }'
```

```json
{
  "id": 1,
  "name": "Web 101",
  "description": "Inspecione os headers HTTP da página alvo.",
  "category": "web",
  "base_points": 100,
  "difficulty": "easy"
}
```

---

#### Criar uma equipe

```bash
curl -s -X POST http://localhost:8000/api/v1/teams \
  -H "Content-Type: application/json" \
  -d '{ "name": "FireUAI" }'
```

```json
{ "id": 1, "name": "FireUAI", "score": 0 }
```

---

#### Submeter uma flag

```bash
curl -s -X POST http://localhost:8000/api/v1/submissions \
  -H "Content-Type: application/json" \
  -d '{ "team_id": 1, "challenge_id": 1, "flag": "CTF{hidden_header_found}" }'
```

```json
{
  "correct": true,
  "points_awarded": 150,
  "message": "Correct! First blood! You earned 150 points."
}
```

---

#### Consultar o placar

```bash
curl http://localhost:8000/api/v1/scoreboard
```

```json
{
  "entries": [
    { "rank": 1, "team_name": "FireUAI", "score": 150, "total_solves": 1 }
  ]
}
```

> Suporta paginação: `GET /scoreboard?limit=10&offset=0`

---

#### Listar desafios por categoria

```bash
curl "http://localhost:8000/api/v1/challenges?category=web"
```

---

#### Histórico de solves de uma equipe

```bash
curl http://localhost:8000/api/v1/teams/1/solves
```

```json
{
  "team_id": 1,
  "team_name": "FireUAI",
  "solves": [
    { "challenge_id": 1, "challenge_name": "Web 101", "points_awarded": 150 }
  ]
}
```

---

## 6. Referência dos Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/api/v1/health` | Status da API e conectividade com o banco |
| `POST` | `/api/v1/challenges` | Cria um novo desafio |
| `GET` | `/api/v1/challenges` | Lista desafios (filtro opcional `?category=`) |
| `GET` | `/api/v1/challenges/:id` | Detalhe de um desafio com contagem de solves |
| `POST` | `/api/v1/teams` | Cria uma nova equipe |
| `GET` | `/api/v1/teams` | Lista todas as equipes |
| `GET` | `/api/v1/teams/:id` | Detalhe de uma equipe |
| `GET` | `/api/v1/teams/:id/solves` | Histórico de flags resolvidas pela equipe |
| `POST` | `/api/v1/submissions` | Submete uma flag para validação |
| `GET` | `/api/v1/scoreboard` | Placar geral (`?limit=` e `?offset=`) |

---

## 7. Como Executar os Testes Localmente

```bash
# Executar todos os testes
pytest

# Executar com relatório de cobertura no terminal
pytest --cov=app --cov-report=term-missing

# Gerar relatório HTML de cobertura
pytest --cov=app --cov-report=html
# Abra htmlcov/index.html no navegador
```

Os testes utilizam SQLite em memória — nenhum serviço externo é necessário.
