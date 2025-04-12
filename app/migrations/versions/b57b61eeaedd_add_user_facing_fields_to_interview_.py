"""add_user_facing_fields_to_interview_template

Revision ID: b57b61eeaedd
Revises: c9bf0534012c
Create Date: 2025-04-12 18:19:26.148211

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b57b61eeaedd'
down_revision = 'c9bf0534012c'
branch_labels = None
depends_on = None


def upgrade():
    # Add the new user-facing fields to the interview_templates table
    op.add_column('interview_templates', sa.Column('title', sa.String(), nullable=True))
    op.add_column('interview_templates', sa.Column('description_short', sa.String(), nullable=True))
    op.add_column('interview_templates', sa.Column('description_long', sa.Text(), nullable=True))
    op.add_column('interview_templates', sa.Column('duration', sa.Integer(), nullable=True))


def downgrade():
    # Remove the columns if we need to roll back
    op.drop_column('interview_templates', 'title')
    op.drop_column('interview_templates', 'description_short')
    op.drop_column('interview_templates', 'description_long')
    op.drop_column('interview_templates', 'duration') 