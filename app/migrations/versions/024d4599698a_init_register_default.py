"""Init register default

Revision ID: 024d4599698a
Revises: 002_seed_admin
Create Date: 2026-04-05 19:15:05.708982

"""
from typing import Sequence, Union
from datetime import date, datetime

from alembic import op
import sqlalchemy as sa
from utils import hash_password

# revision identifiers, used by Alembic.
revision: str = '024d4599698a'
down_revision: Union[str, None] = '002_seed_admin'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


SEED_USERS = [
    {
        "full_name": "Maria Voluntária",
        "email": "voluntaria@abrigo.com",
        "password": "Voluntario@2025",
        "role": "voluntario",
    },
    {
        "full_name": "João Financeiro",
        "email": "financeiro@abrigo.com",
        "password": "Financeiro@2025",
        "role": "financeiro",
    },
]

SEED_DOGS = [
    {"name": "Rex", "estimated_age_months": 24, "size": "G", "entry_date": date(2026, 3, 6), "notes": "Dócil, bom com crianças."},
    {"name": "Mel", "estimated_age_months": 6,  "size": "P", "entry_date": date(2026, 3, 21), "notes": "Filhote energético."},
    {"name": "Thor", "estimated_age_months": 48, "size": "G", "entry_date": date(2026, 2, 4), "notes": "Precisa de tutor experiente."},
    {"name": "Belinha", "estimated_age_months": 18, "size": "M", "entry_date": date(2026, 3, 26), "notes": None},
]

SEED_VACCINES = [
    {"dog_name": "Rex", "name": "V10", "application_date": date(2025, 10, 7), "next_dose": date(2026, 10, 7)},
    {"dog_name": "Mel", "name": "V8", "application_date": date(2025, 4, 10), "next_dose": date(2026, 4, 10)},
    {"dog_name": "Thor", "name": "Antirrábica", "application_date": date(2025, 3, 1), "next_dose": date(2026, 3, 1)},
    {"dog_name": "Belinha", "name": "V10", "application_date": date(2026, 3, 31), "next_dose": date(2027, 3, 31)},
]

SEED_FINANCIAL = [
    {"type": "entrada", "value": 500.00, "date": date(2026, 4, 1), "category": "doacao", "description": "Monthly donation", "donor": "Ana Silva"},
    {"type": "entrada", "value": 200.00, "date": date(2026, 4, 5), "category": "doacao", "description": "Online campaign", "donor": None},
    {"type": "saida", "value": 350.00, "date": date(2026, 4, 3), "category": "veterinario", "description": "Consulta e vacinas — Rex e Mel", "donor": None},
    {"type": "saida", "value": 180.00, "date": date(2026, 4, 7), "category": "suprimentos", "description": "Ração mensal", "donor": None},
    {"type": "saida", "value": 120.00, "date": date(2026, 4, 1), "category": "custos_fixos", "description": "Conta de água e luz", "donor": None},
]


def _resolve_financial_table(bind) -> str:
    inspector = sa.inspect(bind)
    for candidate in ("financial_records", "financial", "finances"):
        if inspector.has_table(candidate):
            return candidate
    raise RuntimeError("Tabela financeira não encontrada (tentou: financial_records, financial, finances).")


def upgrade() -> None:
    bind = op.get_bind()
    financial_table = _resolve_financial_table(bind)
    now = datetime.utcnow()

    # Users
    for u in SEED_USERS:
        exists = bind.execute(
            sa.text("SELECT 1 FROM users WHERE email = :email LIMIT 1"),
            {"email": u["email"]},
        ).scalar()
        if not exists:
            bind.execute(
                sa.text("""
                    INSERT INTO users (full_name, email, hashed_password, role, created_at)
                    VALUES (:full_name, :email, :hashed_password, :role, :created_at)
                """),
                {
                    "full_name": u["full_name"],
                    "email": u["email"],
                    "hashed_password": hash_password(u["password"]),
                    "role": u["role"],
                    "created_at": now,
                },
            )

    # Dogs
    for d in SEED_DOGS:
        exists = bind.execute(
            sa.text("SELECT 1 FROM dogs WHERE name = :name LIMIT 1"),
            {"name": d["name"]},
        ).scalar()
        if not exists:
            bind.execute(
                sa.text("""
                    INSERT INTO dogs (name, estimated_age_months, size, entry_date, notes, created_at)
                    VALUES (:name, :estimated_age_months, :size, :entry_date, :notes, :created_at)
                """),
                {
                    **d,
                    "created_at": now,
                },
            )

    # Dog name -> id
    dog_name_to_id = {
        row[1]: row[0]
        for row in bind.execute(sa.text("SELECT id, name FROM dogs WHERE name IN ('Rex','Mel','Thor','Belinha')")).fetchall()
    }

    # Vaccines
    for v in SEED_VACCINES:
        dog_id = dog_name_to_id.get(v["dog_name"])
        if not dog_id:
            continue
        exists = bind.execute(
            sa.text("""
                SELECT 1
                FROM vaccines
                WHERE dog_id = :dog_id
                  AND name = :name
                  AND application_date = :application_date
                LIMIT 1
            """),
            {"dog_id": dog_id, "name": v["name"], "application_date": v["application_date"]},
        ).scalar()
        if not exists:
            bind.execute(
                sa.text("""
                    INSERT INTO vaccines (dog_id, name, application_date, next_dose, created_at)
                    VALUES (:dog_id, :name, :application_date, :next_dose, :created_at)
                """),
                {
                    "dog_id": dog_id,
                    "name": v["name"],
                    "application_date": v["application_date"],
                    "next_dose": v["next_dose"],
                    "created_at": now,
                },
            )

    # Financial
    for f in SEED_FINANCIAL:
        exists = bind.execute(
            sa.text(f"""
                SELECT 1
                FROM {financial_table}
                WHERE type = :type
                  AND value = :value
                  AND date = :date
                  AND category = :category
                  AND description = :description
                LIMIT 1
            """),
            f,
        ).scalar()
        if not exists:
            bind.execute(
                sa.text(f"""
                    INSERT INTO {financial_table} (type, value, date, category, description, donor, created_at)
                    VALUES (:type, :value, :date, :category, :description, :donor, :created_at)
                """),
                {
                    **f,
                    "created_at": now,
                },
            )


def downgrade() -> None:
    bind = op.get_bind()
    financial_table = _resolve_financial_table(bind)

    # Vaccines first (FK with dogs)
    bind.execute(sa.text("""
        DELETE v
        FROM vaccines v
        JOIN dogs d ON d.id = v.dog_id
        WHERE
            (d.name = 'Rex' AND v.name = 'V10' AND v.application_date = '2025-10-07')
            OR (d.name = 'Mel' AND v.name = 'V8' AND v.application_date = '2025-04-10')
            OR (d.name = 'Thor' AND v.name = 'Antirrábica' AND v.application_date = '2025-03-01')
            OR (d.name = 'Belinha' AND v.name = 'V10' AND v.application_date = '2026-03-31')
    """))

    # Financial
    bind.execute(sa.text(f"""
        DELETE FROM {financial_table}
        WHERE
            (type='entrada' AND value=500.00 AND date='2026-04-01' AND category='doacao' AND description='Monthly donation')
            OR (type='entrada' AND value=200.00 AND date='2026-04-05' AND category='doacao' AND description='Online campaign')
            OR (type='saida' AND value=350.00 AND date='2026-04-03' AND category='veterinario' AND description='Consulta e vacinas — Rex e Mel')
            OR (type='saida' AND value=180.00 AND date='2026-04-07' AND category='suprimentos' AND description='Ração mensal')
            OR (type='saida' AND value=120.00 AND date='2026-04-01' AND category='custos_fixos' AND description='Conta de água e luz')
    """))

    # Dogs
    bind.execute(sa.text("DELETE FROM dogs WHERE name IN ('Rex', 'Mel', 'Thor', 'Belinha')"))

    # Users (não remove admin)
    bind.execute(sa.text("DELETE FROM users WHERE email IN ('voluntaria@abrigo.com', 'financeiro@abrigo.com')"))