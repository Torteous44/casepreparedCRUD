"""Initial migration

Revision ID: 3b7641878a71
Revises: 
Create Date: 2025-04-11 19:30:50.066198

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '3b7641878a71'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('interview_templates',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('case_type', sa.String(), nullable=False),
    sa.Column('lead_type', sa.String(), nullable=False),
    sa.Column('difficulty', sa.String(), nullable=False),
    sa.Column('company', sa.String(), nullable=True),
    sa.Column('industry', sa.String(), nullable=True),
    sa.Column('prompt', sa.Text(), nullable=False),
    sa.Column('structure', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('version', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('full_name', sa.String(), nullable=False),
    sa.Column('password_hash', sa.String(), nullable=True),
    sa.Column('google_oauth_id', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_table('interviews',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('template_id', sa.UUID(), nullable=False),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('started_at', sa.DateTime(), nullable=True),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.Column('progress_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.ForeignKeyConstraint(['template_id'], ['interview_templates.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('subscriptions',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('stripe_customer_id', sa.String(), nullable=True),
    sa.Column('stripe_subscription_id', sa.String(), nullable=True),
    sa.Column('plan', sa.String(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('subscriptions')
    op.drop_table('interviews')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_table('interview_templates')
    # ### end Alembic commands ### 