"""seed_roles_permissions_and_update_users

Revision ID: ef68ca87db7e
Revises: 4c6de7d97dd3
Create Date: 2026-05-01 14:46:48.837444

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ef68ca87db7e'
down_revision: Union[str, None] = '4c6de7d97dd3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()

    # 1. Inserir Roles (Cargos)
    bind.execute(sa.text("""
        INSERT INTO roles (id, name) VALUES
        (1, 'admin'),
        (2, 'voluntario'),
        (3, 'financeiro')
    """))

    # 2. Inserir Permissions (Permissões básicas como exemplo)
    bind.execute(sa.text("""
        INSERT INTO permissions (id, name, description) VALUES
        (1, 'manage_all', 'Acesso total e irrestrito ao sistema'),
        (2, 'manage_dogs', 'Gerenciamento de cães e rotinas do abrigo'),
        (3, 'manage_finances', 'Gerenciamento do painel financeiro e doações')
    """))

    # 3. Associar Permissions às Roles (Role_Permissions)
    bind.execute(sa.text("""
        INSERT INTO role_permissions (role_id, permission_id) VALUES
        (1, 1), -- Admin recebe 'manage_all'
        (2, 2), -- Voluntário recebe 'manage_dogs'
        (3, 3)  -- Financeiro recebe 'manage_finances'
    """))

    # 4. Atualizar os Usuários Existentes com seus respectivos role_id
    # Utilizando o email como chave para garantir precisão caso os IDs mudem entre bancos
    bind.execute(sa.text("UPDATE users SET role_id = 1 WHERE email = 'admin@abrigo.com'"))
    bind.execute(sa.text("UPDATE users SET role_id = 2 WHERE email = 'voluntaria@abrigo.com'"))
    bind.execute(sa.text("UPDATE users SET role_id = 3 WHERE email = 'financeiro@abrigo.com'"))


def downgrade() -> None:
    bind = op.get_bind()

    # 1. Desvincular os usuários (reverter para NULL)
    bind.execute(sa.text("UPDATE users SET role_id = NULL WHERE email IN ('admin@abrigo.com', 'voluntaria@abrigo.com', 'financeiro@abrigo.com')"))

    # 2. Remover as associações
    bind.execute(sa.text("DELETE FROM role_permissions WHERE role_id IN (1, 2, 3)"))

    # 3. Remover Permissões e Cargos
    bind.execute(sa.text("DELETE FROM permissions WHERE id IN (1, 2, 3)"))
    bind.execute(sa.text("DELETE FROM roles WHERE id IN (1, 2, 3)"))