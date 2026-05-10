# AGENTS.md

Este documento serve como guia para agentes de IA e desenvolvedores que trabalham no projeto **FastAPIbankSystem**. Ele detalha as tecnologias, convenções e a arquitetura do sistema para garantir consistência e qualidade no desenvolvimento.

---

## 🚀 Tecnologias Utilizadas

- **Linguagem:** Python 3.12+
- **Framework Web:** FastAPI
- **ORM / Banco de Dados:** SQLModel (SQLAlchemy + Pydantic)
- **Banco de Dados:** SQLite (via `aiosqlite` para operações assíncronas)
- **Migrações:** Alembic
- **Gerenciamento de Pacotes:** uv
- **Autenticação:** JWT (PyJWT) e Argon2 (pwdlib)
- **Qualidade de Código:** Ruff (Linter e Formatter)
- **Testes:** Pytest com `pytest-asyncio`

---

## 🏗️ Arquitetura e Estrutura de Pastas

O projeto segue um padrão MVC/Service orientado a serviços:

- `src/controllers/`: Manipuladores de rotas (Entrypoints da API).
- `src/services/`: Lógica de negócio e interação direta com o banco de dados.
- `src/models/`: Modelos do banco de dados (SQLModel).
- `src/schemas/`: Esquemas Pydantic para entrada de dados e validação interna.
- `src/views/`: Esquemas Pydantic exclusivos para saída de dados (Response Models).
- `src/core/`: Configurações globais e segurança.
- `src/utils/`: Utilitários (DB helpers, segurança, senhas).
- `migrations/`: Histórico de migrações do banco de dados (Alembic).

---

## 📏 Convenções de Código

### 1. Nomenclatura e Idioma
- **Idioma:** Todo o código (variáveis, funções, classes, arquivos, comentários e documentação) deve ser escrito em **Inglês**.
- **Variáveis/Funções:** `snake_case`.
- **Classes:** `PascalCase`.
- **Constantes:** `UPPER_SNAKE_CASE`.

### 2. Git e Commits
- Utilizamos **Conventional Commits**:
    - `feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `chore:`, `build:`.

### 3. Padrões de Desenvolvimento
- **Assincronismo:** Todas as operações de I/O (especialmente banco de dados) devem ser `async/await`.
- **Tipagem:** O uso de **Type Hints** é obrigatório.
- **Injeção de Dependência:** Utilize `Depends()` do FastAPI.
- **Docstrings:** Use docstrings (padrão Google).

### 4. Segurança e CLI
- **Criação de Usuários:** Por segurança, o cadastro de novos usuários não é público via API. Deve-se utilizar o comando CLI:
    ```bash
    uv run python -m src.commands.create_user
    ```

---

## 🛠️ Fluxo de Trabalho Recomendado

1. **Análise:** Entenda os requisitos.
2. **Modelagem:** Atualize `src/models/` e gere a migração.
3. **Esquemas:** Crie/Atualize schemas em `src/schemas/` e `src/views/`.
4. **Serviço:** Implemente a lógica em `src/services/`.
5. **Controller:** Exponha a rota em `src/controllers/`.
6. **Testes:** Adicione testes em `tests/`.
7. **Linting:** Execute `ruff check .` e `ruff format .`.

---

## ⚙️ CI/CD Pipeline

O projeto utiliza **GitHub Actions** para garantir a qualidade contínua do código. A cada `push` ou `pull request` na branch `main`, a pipeline executa automaticamente:
- **Linting & Formatting:** Via `Ruff`.
- **Type Checking:** Via `Mypy`.
- **Automated Tests:** Via `Pytest` (executados contra uma instância real de **PostgreSQL** em container para máxima fidelidade com a produção).

Certifique-se de que todos os passos passem localmente antes de enviar seu código!

---

## 🚀 Deployment

O deploy da aplicação é realizado na plataforma **Render** utilizando **Docker**.
- **Infraestrutura:** Definida no arquivo `render.yaml` (Blueprint).
- **Banco de Dados:** PostgreSQL (gerenciado pela Render).
- **Processo:** O `Dockerfile` realiza o build otimizado com `uv`, executa as migrações do Alembic e inicia o servidor Uvicorn.
- **Inicialização:** No primeiro deploy, se as variáveis de ambiente `FIRST_SUPERUSER_USERNAME` e `FIRST_SUPERUSER_PASSWORD` estiverem configuradas, o sistema criará automaticamente o primeiro usuário gerente (caso ele ainda não exista).
- **Configuração:** O validador em `src/core/config.py` converte automaticamente a URL do banco para o driver assíncrono `postgresql+asyncpg://`.

---

## 🗄️ Banco de Dados e Migrações

```bash
alembic revision --autogenerate -m "descrição"
alembic upgrade head
```

---

## 🧪 Comandos Úteis

- **Rodar a aplicação:** `fastapi dev src/main.py`
- **Rodar testes:** `pytest`
- **Executar Linter:** `ruff check .`
- **Formatar código:** `ruff format .`
