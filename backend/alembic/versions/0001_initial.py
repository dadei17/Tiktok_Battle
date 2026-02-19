"""Initial migration: battles, battle_results, country_statistics

Revision ID: 0001_initial
Revises: 
Create Date: 2026-02-19 20:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # battles table
    op.create_table(
        'battles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('creator_username', sa.String(255), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('winner_country', sa.String(255), nullable=True),
    )

    # battle_results table
    op.create_table(
        'battle_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('battle_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('battles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('country_name', sa.String(255), nullable=False),
        sa.Column('final_score', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.UniqueConstraint('battle_id', 'country_name', name='uq_battle_country'),
    )
    op.create_index('ix_battle_results_battle_id', 'battle_results', ['battle_id'])

    # country_statistics table
    op.create_table(
        'country_statistics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('country_name', sa.String(255), unique=True, nullable=False),
        sa.Column('total_wins', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_second_place', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_third_place', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_battles', sa.Integer(), nullable=False, server_default='0'),
    )
    op.create_index('ix_country_statistics_country_name', 'country_statistics', ['country_name'])


def downgrade() -> None:
    op.drop_table('country_statistics')
    op.drop_table('battle_results')
    op.drop_table('battles')
