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

## 4. Endpoints da API

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
