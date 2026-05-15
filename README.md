# 🐾 Abrigo de Animais — API

Sistema de gestao interna para um abrigo de animais, construido com **FastAPI + PostgreSQL + SQLAlchemy**.
Acesso restrito a usuarios internos autenticados — sem endpoints publicos.

---

## 📋 Stack

| Layer      | Technology                   |
|------------|------------------------------|
| Framework  | FastAPI 0.111                |
| Database   | PostgreSQL 16+               |
| ORM        | SQLAlchemy 2.0               |
| Migrations | Alembic 1.13                 |
| Auth       | JWT (python-jose) + BCrypt   |
| Validation | Pydantic v2                  |
| Dev server | Uvicorn                      |

---

## 🗂️ Project Structure

```
/
├── app/
│   ├── configs/
│   │   ├── db_conn.py        # PostgresConnection — context manager + cache de engine
│   │   ├── security.py       # JWT + dependencias baseadas em role
│   │   └── __init__.py
│   │
│   ├── models/
│   │   ├── base_model.py     # SQLAlchemy declarative base
│   │   ├── user_model.py     # tabela users (admin | voluntario | financeiro)
│   │   ├── animal_model.py   # tabela animals
│   │   ├── vaccine_model.py  # tabela vaccines
│   │   ├── financial_model.py # tabela financial
│   │   ├── inventory_model.py # inventory items + movements
│   │   ├── donation_model.py  # donations + donation items
│   │   ├── log_model.py       # logs de requests
│   │   └── rbac_model.py      # roles + permissions
│   │
│   ├── daos/
│   │   ├── user_dao.py
│   │   ├── animal_dao.py
│   │   ├── vaccine_dao.py    # inclui get_overdue() e get_due_soon()
│   │   ├── financial_dao.py  # inclui get_by_month() para relatorios
│   │   ├── inventory_dao.py
│   │   ├── donation_dao.py
│   │   ├── role_dao.py
│   │   ├── permission_dao.py
│   │   └── log_dao.py
│   │
│   ├── schemas/
│   │   ├── user_schema.py
│   │   ├── animal_schema.py  # AnimalStatusUpdateRequest aplica regras de transicao
│   │   ├── vaccine_schema.py # valida next_dose > application_date
│   │   ├── financial_schema.py
│   │   ├── inventory_schema.py
│   │   ├── donation_schema.py
│   │   ├── role_schema.py
│   │   └── permission_schema.py
│   │
│   ├── services/
│   │   ├── auth_service.py   # inclui role no payload do JWT
│   │   ├── user_service.py
│   │   ├── animal_service.py # aplica regras de transicao de status
│   │   ├── vaccine_service.py
│   │   ├── financial_service.py  # relatorio mensal + somente desativacao
│   │   ├── inventory_service.py
│   │   ├── donation_service.py
│   │   ├── role_service.py
│   │   └── permission_service.py
│   │
│   ├── routes/
│   │   ├── auth_route.py
│   │   ├── users_route.py
│   │   ├── animals_route.py
│   │   ├── vaccines_route.py
│   │   ├── financial_route.py
│   │   ├── inventory_route.py
│   │   ├── donations_route.py
│   │   ├── roles_route.py
│   │   └── permissions_route.py
│   │
│   ├── dependencies/
│   │   └── auth_check.py     # validacao de permissoes
│   │
│   ├── middlewares/
│   │   └── trace_middleware.py
│   │
│   ├── utils/
│   │   └── hash.py           # BCrypt hash_password / verify_password
│   │
│   ├── migrations/
│   │   └── versions/
│   │       ├── 001_initial_shelter_tables.py
│   │       └── 002_seed_admin.py
│   │
│   └── main.py
│
├── seed.py                   # Dados de exemplo para desenvolvimento
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example
```

---

## 🔐 Role-Based Access Control

A role do usuario fica embutida no JWT no login — sem round-trip no banco por request.

| Role         | Animals | Vaccines | Financial | Users | Delete |
|--------------|:----:|:--------:|:---------:|:-----:|:------:|
| `admin`      | ✅   | ✅       | ✅        | ✅    | ✅     |
| `voluntario` | ✅   | ✅       | ❌        | ❌    | ❌     |
| `financeiro` | ❌   | ❌       | ✅        | ❌    | ❌     |

---

## 📋 Business Rules

**Animals:**
- Transicoes de status sao estritamente aplicadas:
  ```
  disponivel → em_processo → adotado
  em_processo → disponivel  (if adoption falls through)
  ```
  Um animal nao pode ser marcado como `adotado` sem passar por `em_processo`.

- `microchipped` indica se o animal possui microchip.

**Vaccines:**
- `next_dose` e obrigatorio — vacinas precisam sempre ter data de reforco.
- `next_dose` deve ser posterior a `application_date` (validado pelo Pydantic).

**Financial:**
- Registros **nao podem ser deletados** — apenas desativados (`is_active = False`).
- Somente admin e financeiro acessam dados financeiros.

**Donations + Inventory:**
- Doacoes podem incluir dinheiro, itens ou ambos.
- Doacoes de itens geram movimentos de estoque automaticamente.

---

## 🚀 Setup

### 1. Criar ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar .env

```bash
cp .env.example .env
```

```env
POSTGRES_USER=abrigo_user
POSTGRES_PASSWORD=your_password
POSTGRES_SERVER=db:5432          # Use 'localhost:5432' para dev local
POSTGRES_DB=abrigo_animais

JWT_SECRET_KEY=generate_with_python_secrets
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=480

FRONTEND_URL=http://localhost:5173
```

> Gerar uma chave segura:
> ```bash
> python -c "import secrets; print(secrets.token_hex(32))"
> ```

### 4. Rodar migrations

```bash
alembic upgrade head
```

Isso cria todas as tabelas e o usuario admin padrao.

### 5. (Opcional) Seed de dados de exemplo

```bash
python seed.py
```

### 6. Iniciar o servidor

```bash
uvicorn app.main:app --reload --port 8000
```

- **Swagger UI:** http://localhost:8000/docs
- **Health check:** http://localhost:8000/status

---

## 🐳 Docker

```bash
# Criar o volume externo (primeira vez)
docker volume create abrigo-animais-db-volume

# Build e start
docker compose up -d --build

# Rodar seed apos containers estarem saudaveis
docker compose exec api python seed.py
```

---

## 🧪 Tests

```bash
pip install -r requirements.txt -r requirements-dev.txt
```

Rodar todos os testes (precisa de Docker rodando para o Postgres do testcontainers):

```bash
pytest
```

Rodar apenas unit tests (sem Docker):

```bash
pytest tests/unit
```

---

## 🌐 API Endpoints

### Authentication
| Method | Route         | Auth | Request (campos) | Response (campos) | Description |
|--------|---------------|------|------------------|-------------------|-------------|
| POST   | `/auth/login` | ❌    | Form: `username` (email), `password` | `access_token`, `token_type`, `user_name`, `user_email`, `role` | Login — retorna JWT + role |
| GET    | `/status`     | ❌    | — | `status`, `system` | Health check |

### Users
| Method | Route                        | Auth | Request (campos) | Response (campos) | Description |
|--------|------------------------------|------|------------------|-------------------|-------------|
| GET    | `/users/me`                  | ✅ | — | `id`, `full_name`, `email`, `is_active`, `role`, `permissions[]` | Perfil do usuario atual (autenticado) |
| GET    | `/users`                     | ✅ (admin) | Query: `page`, `page_size` | `data[]` (user), `pagination` (`actual_page`, `page_size`, `total_pages`, `total_records`) | Listar todos os usuarios |
| GET    | `/users/{id}`                | ✅ (admin) | Path: `user_id` | `id`, `full_name`, `email`, `is_active`, `role`, `permissions[]` | Buscar usuario por ID |
| POST   | `/users`                     | ✅ (admin) | Body: `full_name`, `email`, `password`, `role`, `permissions[]` | `id`, `full_name`, `email`, `is_active`, `role`, `permissions[]` | Criar usuario |
| PATCH  | `/users/{id}`                | ✅ (admin) | Path: `user_id`, Body: `full_name?`, `role?`, `permissions?[]` | `id`, `full_name`, `email`, `is_active`, `role`, `permissions[]` | Atualizar usuario |
| PATCH  | `/users/{id}/deactivate`     | ✅ (admin) | Path: `user_id` | `message` | Desativar usuario |
| PATCH  | `/users/{id}/activate`       | ✅ (admin) | Path: `user_id` | `message` | Reativar usuario |

### Animals — admin + voluntario
| Method | Route                 | Auth | Request (campos) | Response (campos) | Description |
|--------|-----------------------|------|------------------|-------------------|-------------|
| GET    | `/animals`               | ✅ | Query: `include_inactive`, `page`, `page_size` | `data[]` (animal), `pagination` (`actual_page`, `page_size`, `total_pages`, `total_records`) | Listar animais ativos |
| GET    | `/animals/{id}`          | ✅ | Path: `animal_id` | `id`, `name`, `estimated_age`, `vaccines[]`, `size`, `species`, `adoption_status`, `entry_date`, `is_active`, `notes`, `neutered`, `dewormed`, `socializes_with_other_animals`, `color`, `microchipped`, `image_path`, `created_at`, `updated_at` | Buscar animal por ID |
| POST   | `/animals`               | ✅ | Form: `name`, `estimated_age`, `size`, `species`, `entry_date`, `notes?`, `neutered?`, `dewormed?`, `socializes_with_other_animals?`, `color?`, `microchipped?`, `vaccines?` (JSON lista), File: `image` | Animal completo (campos acima) | Cadastrar novo animal |
| PATCH  | `/animals/{id}`          | ✅ | Path: `animal_id`, Body: `name?`, `estimated_age?`, `size?`, `species?`, `notes?`, `neutered?`, `dewormed?`, `socializes_with_other_animals?`, `color?`, `microchipped?` | `message` | Atualizar dados do animal |
| PATCH  | `/animals/{id}/status`   | ✅ | Path: `animal_id`, Body: `adoption_status` | `message` | Atualizar status de adocao (regras) |
| DELETE | `/animals/{id}`          | ✅ | Path: `animal_id` | `message` | Desativar animal (admin apenas) |
| POST   | `/animals/{id}/image`    | ✅ | Path: `animal_id`, File: `image` | Animal completo (campos acima) | Enviar ou substituir imagem do animal |

### Vaccines — admin + voluntario
| Method | Route                          | Auth | Request (campos) | Response (campos) | Description |
|--------|--------------------------------|------|------------------|-------------------|-------------|
| GET    | `/vaccines/alerts/overdue`     | ✅ | — | `id`, `animal_id`, `animal_name`, `name`, `next_dose`, `status` | Listar vacinas em atraso |
| GET    | `/vaccines/alerts/due-soon`    | ✅ | Query: `days` | `id`, `animal_id`, `animal_name`, `name`, `next_dose`, `status` | Listar vacinas a vencer |
| GET    | `/vaccines/animal/{animal_id}` | ✅ | Path: `animal_id` | `id`, `animal_id`, `name`, `application_date`, `next_dose`, `notes`, `is_active`, `created_at` | Listar vacinas do animal |
| POST   | `/vaccines`                    | ✅ | Body: `animal_id`, `name`, `application_date`, `next_dose?`, `notes?` | `id`, `animal_id`, `name`, `application_date`, `next_dose`, `notes`, `is_active`, `created_at` | Registrar vacina |
| PATCH  | `/vaccines/{id}`               | ✅ | Path: `vaccine_id`, Body: `name?`, `application_date?`, `next_dose?`, `notes?` | `id`, `animal_id`, `name`, `application_date`, `next_dose`, `notes`, `is_active`, `created_at` | Atualizar registro da vacina |
| DELETE | `/vaccines/{id}`               | ✅ | Path: `vaccine_id` | `message` | Desativar registro da vacina |

### Financial — admin + financeiro
| Method | Route                             | Auth | Request (campos) | Response (campos) | Description |
|--------|-----------------------------------|------|------------------|-------------------|-------------|
| GET    | `/financial`                      | ✅ | — | `id`, `type`, `value`, `date`, `category`, `description`, `donor`, `is_active`, `created_at` | Listar registros ativos |
| GET    | `/financial/{id}`                 | ✅ | Path: `record_id` | `id`, `type`, `value`, `date`, `category`, `description`, `donor`, `is_active`, `created_at` | Buscar registro por ID |
| POST   | `/financial`                      | ✅ | Body: `type`, `value`, `date`, `category`, `description?`, `donor?` | `id`, `type`, `value`, `date`, `category`, `description`, `donor`, `is_active`, `created_at` | Registrar entrada ou saida |
| PATCH  | `/financial/{id}/deactivate`      | ✅ | Path: `record_id` | `message` | Desativar registro (sem delete) |
| GET    | `/financial/report/{year}/{month}`| ✅ | Path: `year`, `month` | `year`, `month`, `total_income`, `total_expenses`, `balance`, `records[]` | Relatorio mensal |

### Inventory — admin + financeiro
| Method | Route                            | Auth | Request (campos) | Response (campos) | Description |
|--------|----------------------------------|------|------------------|-------------------|-------------|
| GET    | `/inventory/items`               | ✅ | Query: `include_inactive`, `page`, `page_size` | `data[]` (item), `pagination` (`actual_page`, `page_size`, `total_pages`, `total_records`) | Listar itens do estoque |
| GET    | `/inventory/items/{item_id}`     | ✅ | Path: `item_id` | `id`, `name`, `description`, `unit`, `is_active`, `created_at`, `updated_at` | Buscar item do estoque |
| POST   | `/inventory/items`               | ✅ | Body: `name`, `description?`, `unit?` | `id`, `name`, `description`, `unit`, `is_active`, `created_at`, `updated_at` | Criar item no estoque |
| PATCH  | `/inventory/items/{item_id}`     | ✅ | Path: `item_id`, Body: `name?`, `description?`, `unit?` | `id`, `name`, `description`, `unit`, `is_active`, `created_at`, `updated_at` | Atualizar item do estoque |
| PATCH  | `/inventory/items/{item_id}/deactivate` | ✅ | Path: `item_id` | `message` | Desativar item |
| POST   | `/inventory/movements`           | ✅ | Body: `item_id`, `type` (`entrada`/`saida`), `quantity`, `date`, `unit?`, `note?`, `reference?` | `id`, `item_id`, `type`, `quantity`, `unit`, `date`, `note`, `reference`, `created_at` | Registrar movimento de estoque |
| GET    | `/inventory/movements`           | ✅ | Query: `item_id?` | `id`, `item_id`, `type`, `quantity`, `unit`, `date`, `note`, `reference`, `created_at` | Listar movimentos de estoque |
| GET    | `/inventory/stock`               | ✅ | — | `item_id`, `item_name`, `unit`, `is_active`, `balance` | Consultar saldo de estoque |

### Donations — admin + financeiro
| Method | Route                          | Auth | Request (campos) | Response (campos) | Description |
|--------|--------------------------------|------|------------------|-------------------|-------------|
| GET    | `/donations`                   | ✅ | — | `id`, `donor`, `date`, `monetary_value`, `description`, `is_active`, `created_at`, `items[]` | Listar doacoes |
| GET    | `/donations/{id}`              | ✅ | Path: `donation_id` | `id`, `donor`, `date`, `monetary_value`, `description`, `is_active`, `created_at`, `items[]` | Buscar doacao por ID |
| POST   | `/donations`                   | ✅ | Body: `donor?`, `date`, `monetary_value?`, `description?`, `items[]` (cada item: `item_id`, `quantity`, `unit?`) | `id`, `donor`, `date`, `monetary_value`, `description`, `is_active`, `created_at`, `items[]` | Registrar doacao (dinheiro ou itens) |
| PATCH  | `/donations/{id}/deactivate`   | ✅ | Path: `donation_id` | `message` | Desativar doacao |

### Roles and Permissions — admin only
| Method | Route           | Auth | Request (campos) | Response (campos) | Description |
|--------|-----------------|------|------------------|-------------------|-------------|
| GET    | `/roles`        | ✅ (admin) | — | `id`, `name`, `permissions[]` | Listar roles |
| POST   | `/roles`        | ✅ (admin) | Body: `name`, `permissions[]` | `id`, `name`, `permissions[]` | Criar role |
| PATCH  | `/roles/{id}`   | ✅ (admin) | Path: `role_id`, Body: `permissions?[]` | `id`, `name`, `permissions[]` | Atualizar permissoes da role |
| GET    | `/permissions`  | ✅ (admin) | — | `id`, `name`, `description` | Listar permissoes |
| POST   | `/permissions`  | ✅ (admin) | Body: `name`, `description?` | `id`, `name`, `description` | Criar permissao |

---

## ⚙️ Adding a New Feature

1. Criar o model em `app/models/` (import `BaseModel` de `base_model.py`)
2. Exportar em `app/models/__init__.py`
3. Importar em `app/migrations/env.py`
4. Criar o DAO em `app/daos/`
5. Criar o service em `app/services/`
6. Criar a route em `app/routes/` e registrar em `app/routes/__init__.py` e `app/main.py`
7. Gerar migration: `alembic revision --autogenerate -m "description"`

