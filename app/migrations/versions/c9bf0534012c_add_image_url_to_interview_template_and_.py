"""Add image_url to interview_template and is_admin to user

Revision ID: c9bf0534012c
Revises: bd3d2471527c
Create Date: 2025-04-12 13:46:08.724030

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c9bf0534012c'
down_revision = 'bd3d2471527c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # First add the column as nullable
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=True))
    
    # Set default value for existing rows
    op.execute("UPDATE users SET is_admin = FALSE")
    
    # Make the column not nullable
    op.alter_column('users', 'is_admin', nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'is_admin')
    # ### end Alembic commands ### 