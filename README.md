# FastAPI Banking System 🏦

Um sistema bancário RESTful desenvolvido com **FastAPI**, focado em gerenciamento de clientes, contas correntes e transações financeiras com autenticação JWT.

## 🚀 Funcionalidades Principais

- **Autenticação e Usuários**:
  - Login via OAuth2 com geração de token JWT.
  - Criação de usuário exclusivamente via comando CLI (sem endpoint público).
  - Usuário autenticado pode visualizar e atualizar o próprio perfil.
  - Bloqueio de acesso para usuários desabilitados.

- **Gestão de Clientes**:
  - Cadastro, listagem, atualização e remoção de clientes individuais.
  - Remoção em cascata: deletar um cliente remove também o registro pai.

- **Contas Correntes**:
  - Criação de contas correntes com limite e limite de saques.
  - Listagem e detalhamento com saldo, número e agência da conta.
  - Remoção em cascata: deletar a conta corrente remove também a conta base.

- **Transações**:
  - Registro de depósitos e saques com atualização automática de saldo.
  - Histórico de transações por conta.
  - Remoção de transação reverte o saldo automaticamente.
  - Saques exigem usuário ativo autenticado.

- **Migrações**:
  - Gerenciamento de schema com **Alembic** em modo assíncrono.

## 🛠 Tecnologias Utilizadas

- [**Python 3.12+**](https://www.python.org/): Linguagem base do projeto.
- [**FastAPI**](https://fastapi.tiangolo.com/): Framework web assíncrono de alta performance.
- [**SQLModel**](https://sqlmodel.tiangolo.com/): ORM com integração nativa ao FastAPI e Pydantic.
- [**SQLAlchemy (async)**](https://docs.sqlalchemy.org/): Engine assíncrona para acesso ao banco.
- [**Alembic**](https://alembic.sqlalchemy.org/): Migrações de banco de dados.
- [**aiosqlite**](https://github.com/omnilib/aiosqlite): Driver assíncrono para SQLite.
- [**PyJWT**](https://pyjwt.readthedocs.io/): Geração e validação de tokens JWT.
- [**pwdlib (Argon2)**](https://github.com/frankie567/pwdlib): Hash seguro de senhas.
- [**Pydantic Settings**](https://docs.pydantic.dev/latest/concepts/pydantic_settings/): Configuração via variáveis de ambiente.
- [**Typer**](https://typer.tiangolo.com/): CLI para criação de usuários.
- [**uv**](https://github.com/astral-sh/uv): Gerenciamento de dependências e ambiente virtual.

## 📐 Arquitetura

```
src/
├── commands/       # Comandos CLI (criação de usuário)
├── controllers/    # Routers FastAPI (endpoints HTTP)
├── core/           # Configurações da aplicação
├── migrations/     # Migrações Alembic
├── models/         # Modelos SQLModel (tabelas do banco)
├── schemas/        # Schemas Pydantic (entrada/saída de dados)
├── services/       # Lógica de negócio
├── utils/          # Utilitários (banco, segurança, senha)
└── views/          # Schemas de resposta (output)
```

## 🔧 Como Rodar o Projeto

### Pré-requisitos

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) instalado

### Passo a Passo

**1. Clone o repositório**
```bash
git clone https://github.com/Lidianacosta/FastAPIBankingSystem.git
cd FastAPIBankingSystem
```

**2. Crie e ative o ambiente virtual**
```bash
uv sync
```

**3. Configure as variáveis de ambiente**
```bash
cp .env.example .env
# Edite o .env com sua SECRET_KEY e demais configurações
```

**4. Aplique as migrações**
```bash
uv run alembic upgrade head
```

**5. Crie o usuário administrador**
```bash
uv run python -m src.commands.create_user
```

**6. Inicie o servidor**
```bash
uv run fastapi dev src/main.py
```

**7. Acesse a documentação interativa**

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 🔑 Autenticação

Todos os endpoints (exceto `/api/auth/token`) exigem autenticação via **Bearer Token**.

1. Crie um usuário via CLI
2. Faça `POST /api/auth/token` com `username` e `password`
3. Use o `access_token` retornado no header: `Authorization: Bearer <token>`

## 📋 Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/api/auth/token` | Login e geração de token JWT |
| `GET` | `/api/users/me/` | Perfil do usuário autenticado |
| `PATCH` | `/api/users/me/` | Atualizar perfil do usuário |
| `GET` | `/api/individual-clients/` | Listar clientes |
| `POST` | `/api/individual-clients/` | Criar cliente |
| `GET` | `/api/individual-clients/{id}` | Detalhar cliente |
| `PATCH` | `/api/individual-clients/{id}` | Atualizar cliente |
| `DELETE` | `/api/individual-clients/{id}` | Remover cliente |
| `GET` | `/api/individual-clients/{id}/checking-accounts/` | Listar contas do cliente |
| `POST` | `/api/individual-clients/{id}/checking-accounts/` | Criar conta corrente |
| `GET` | `/api/checking-accounts/{id}/deposits/` | Listar depósitos |
| `POST` | `/api/checking-accounts/{id}/deposits/` | Realizar depósito |
| `DELETE` | `/api/checking-accounts/{id}/deposits/{tid}` | Remover depósito |
| `GET` | `/api/checking-accounts/{id}/withdrawals/` | Listar saques |
| `POST` | `/api/checking-accounts/{id}/withdrawals/` | Realizar saque |
| `DELETE` | `/api/checking-accounts/{id}/withdrawals/{tid}` | Remover saque |

## 🌍 Linguagem

O código está escrito em **inglês** seguindo boas práticas de desenvolvimento. A documentação está disponível em **português**.
