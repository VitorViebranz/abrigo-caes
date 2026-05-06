# 🐾 Abrigo de Animais — API

Internal management system for an animal shelter, built with **FastAPI + PostgreSQL + SQLAlchemy**.
Access is restricted to authenticated internal users only — no public-facing endpoints.

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
│   │   ├── db_conn.py        # PostgresConnection — context manager + engine cache
│   │   ├── security.py       # JWT + role-based dependencies
│   │   └── __init__.py
│   │
│   ├── models/
│   │   ├── base_model.py     # SQLAlchemy declarative base
│   │   ├── user_model.py     # users table (admin | voluntario | financeiro)
│   │   ├── animal_model.py   # animals table
│   │   ├── vaccine_model.py  # vaccines table
│   │   └── financial_model.py # financial table
│   │
│   ├── daos/
│   │   ├── user_dao.py
│   │   ├── animal_dao.py
│   │   ├── vaccine_dao.py    # includes get_overdue() and get_due_soon()
│   │   └── financial_dao.py  # includes get_by_month() for reports
│   │
│   ├── schemas/
│   │   ├── user_schema.py
│   │   ├── animal_schema.py  # AnimalStatusUpdateRequest enforces transition rules
│   │   ├── vaccine_schema.py # validates next_dose > application_date
│   │   └── financial_schema.py
│   │
│   ├── services/
│   │   ├── auth_service.py   # embeds role in JWT payload
│   │   ├── user_service.py
│   │   ├── animal_service.py # enforces adoption status transition rules
│   │   ├── vaccine_service.py
│   │   └── financial_service.py  # monthly report + deactivation only
│   │
│   ├── routes/
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── animals_route.py
│   │   ├── vaccines.py
│   │   └── financial.py
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
├── seed.py                   # Sample data for development
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example
```

---

## 🔐 Role-Based Access Control

The user's role is embedded in the JWT at login — no database round-trip needed per request.

| Role         | Animals | Vaccines | Financial | Users | Delete |
|--------------|:----:|:--------:|:---------:|:-----:|:------:|
| `admin`      | ✅   | ✅       | ✅        | ✅    | ✅     |
| `voluntario` | ✅   | ✅       | ❌        | ❌    | ❌     |
| `financeiro` | ❌   | ❌       | ✅        | ❌    | ❌     |

---

## 📋 Business Rules

**Animals:**
- Status transitions are strictly enforced:
  ```
  disponivel → em_processo → adotado
  em_processo → disponivel  (if adoption falls through)
  ```
  An animal cannot be marked as `adotado` without going through `em_processo` first.

- `microchipped` indicates whether the animal has a microchip.

**Vaccines:**
- `next_dose` is mandatory — vaccines must always have a due date.
- `next_dose` must be after `application_date` (validated by Pydantic).

**Financial:**
- Records **cannot be deleted** — only deactivated (`is_active = False`).
- Only admins and the financial role can access financial data.

---

## 🚀 Setup

### 1. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure .env

```bash
cp .env.example .env
```

```env
POSTGRES_USER=abrigo_user
POSTGRES_PASSWORD=your_password
POSTGRES_SERVER=db:5432          # Use 'localhost:5432' for local dev
POSTGRES_DB=abrigo_animais

JWT_SECRET_KEY=generate_with_python_secrets
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=480

FRONTEND_URL=http://localhost:5173
```

> Generate a secure key:
> ```bash
> python -c "import secrets; print(secrets.token_hex(32))"
> ```

### 4. Run migrations

```bash
alembic upgrade head
```

This creates all tables and the default admin user.

### 5. (Optional) Seed sample data

```bash
python seed.py
```

### 6. Start the server

```bash
uvicorn app.main:app --reload --port 8000
```

- **Swagger UI:** http://localhost:8000/docs
- **Health check:** http://localhost:8000/status

---

## 🐳 Docker

```bash
# Create the external volume (first time only)
docker volume create abrigo-animais-db-volume

# Build and start
docker compose up -d --build

# Run seed after containers are healthy
docker compose exec api python seed.py
```

---

## 🌐 API Endpoints

### Authentication
| Method | Route         | Auth | Description                  |
|--------|---------------|------|------------------------------|
| POST   | `/auth/login` | ❌    | Login — returns JWT + role   |
| POST   | `/auth/token` | ❌    | OAuth2 login (Swagger UI)    |

### Users — admin only
| Method | Route                        | Description          |
|--------|------------------------------|----------------------|
| GET    | `/users`                     | List all users       |
| POST   | `/users`                     | Create user          |
| PATCH  | `/users/{id}/deactivate`     | Deactivate user      |
| PATCH  | `/users/{id}/activate`       | Reactivate user      |

### Animals — admin + voluntario
| Method | Route                 | Description                              |
|--------|-----------------------|------------------------------------------|
| GET    | `/animals`               | List all active animals                     |
| GET    | `/animals/{id}`          | Get animal by ID                            |
| POST   | `/animals`               | Register new animal                         |
| PATCH  | `/animals/{id}`          | Update animal details                       |
| PATCH  | `/animals/{id}/status`   | Update adoption status (rules enforced)     |
| DELETE | `/animals/{id}`          | Deactivate animal (admin only)              |

### Vaccines — admin + voluntario
| Method | Route                          | Description                  |
|--------|--------------------------------|------------------------------|
| GET    | `/vaccines/alerts/overdue`     | List overdue vaccines        |
| GET    | `/vaccines/alerts/due-soon`    | List vaccines due soon       |
| GET    | `/vaccines/animal/{animal_id}` | List vaccines for an animal  |
| POST   | `/vaccines`                    | Register vaccine             |
| PATCH  | `/vaccines/{id}`               | Update vaccine record        |

### Financial — admin + financeiro
| Method | Route                             | Description                  |
|--------|-----------------------------------|------------------------------|
| GET    | `/financial`                      | List all active records      |
| POST   | `/financial`                      | Register income or expense   |
| PATCH  | `/financial/{id}/deactivate`      | Deactivate record (no delete)|
| GET    | `/financial/report/{year}/{month}`| Monthly report               |

---

## ⚙️ Adding a New Feature

1. Create the model in `app/models/` (import `BaseModel` from `base_model.py`)
2. Export it from `app/models/__init__.py`
3. Import it in `app/migrations/env.py`
4. Create the DAO in `app/daos/`
5. Create the service in `app/services/`
6. Create the route in `app/routes/` and register it in `app/routes/__init__.py` and `app/main.py`
7. Generate migration: `alembic revision --autogenerate -m "description"`

---

## 📌 Roadmap

- [ ] Automatic vaccine notifications (email/push)
- [ ] Dashboard with charts (adoptions, financial balance)
- [ ] Adopter registration linked to adoption history
- [ ] Animal photo upload (S3 or local storage)
- [ ] Production deploy — Gunicorn + Nginx + HTTPS
