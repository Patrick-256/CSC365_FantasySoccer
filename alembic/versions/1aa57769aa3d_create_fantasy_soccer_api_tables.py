"""create fantasy_soccer_api tables

Revision ID: 1aa57769aa3d
Revises: 
Create Date: 2023-05-19 14:43:29.761214

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1aa57769aa3d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'positions',
        sa.Column('player_position', sa.String(5), primary_key=True),
    )

    connection = op.get_bind()
    positions= sa.table('positions',sa.column('player_position'))
    connection.execute(positions.insert().values(player_position='GK'))
    connection.execute(positions.insert().values(player_position='LB'))
    connection.execute(positions.insert().values(player_position='CB'))
    connection.execute(positions.insert().values(player_position='RB'))
    connection.execute(positions.insert().values(player_position='CDM'))
    connection.execute(positions.insert().values(player_position='CM'))
    connection.execute(positions.insert().values(player_position='CAM'))
    connection.execute(positions.insert().values(player_position='LM'))
    connection.execute(positions.insert().values(player_position='RM'))
    connection.execute(positions.insert().values(player_position='CF'))
    connection.execute(positions.insert().values(player_position='ST'))
    connection.execute(positions.insert().values(player_position='LW'))
    connection.execute(positions.insert().values(player_position='RW'))
    connection.execute(positions.insert().values(player_position='LWB'))
    connection.execute(positions.insert().values(player_position='RWB'))



    op.create_table(
        'users',
        sa.Column('user_id', sa.Integer, primary_key=True),
        sa.Column('user_name', sa.String(50), nullable=False),
        sa.Column('is_admin', sa.Boolean,nullable=False),
        sa.Column('password', sa.String(100), nullable=True)
    )

    op.create_table(
        'fantasy_leagues',
        sa.Column('fantasy_league_id', sa.Integer, primary_key=True),
        sa.Column('fantasy_league_name', sa.String(50), nullable=False),
    )

    op.create_table(
        'players',
        sa.Column('player_id', sa.Integer, primary_key=True),
        sa.Column('player_name', sa.String(50), nullable=False),
        sa.Column('irl_team_name', sa.String(50),nullable=False),
        sa.Column('player_position', sa.String(50), nullable=False),
        sa.ForeignKeyConstraint(['player_position'], ['positions.player_position'])

    )

    op.create_table(
        'fantasy_teams',
        sa.Column('fantasy_team_id', sa.Integer, primary_key=True),
        sa.Column('fantasy_team_name', sa.String(50), nullable=False),
        sa.Column('user_id', sa.Integer,nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id']),
        sa.Column('fantasy_league_id', sa.Integer, nullable=True),
        sa.ForeignKeyConstraint(['fantasy_league_id'], ['fantasy_leagues.fantasy_league_id'])
    )

    op.create_table(
        'friends',
        sa.Column('user1_id', sa.Integer, primary_key=True),
        sa.ForeignKeyConstraint(['user1_id'], ['users.user_id']),
        sa.Column('user2_id', sa.Integer, primary_key=True),
        sa.ForeignKeyConstraint(['user2_id'], ['users.user_id']),
    )

    op.create_table(
        'games',
        sa.Column('game_id', sa.Integer, primary_key=True),
        sa.Column('player_id', sa.Integer, primary_key=True),
        sa.ForeignKeyConstraint(['player_id'], ['players.player_id']),
        sa.Column('num_goals', sa.Integer,nullable=False),
        sa.Column('num_assists', sa.Integer, nullable=False),
        sa.Column('num_passes', sa.Integer, nullable=False),
        sa.Column('num_shots_on_goal', sa.Integer, nullable=False),
        sa.Column('num_turnovers', sa.Integer, nullable=False),
    )

    op.create_table(
        'player_fantasy_team',
        sa.Column('player_id', sa.Integer, primary_key=True),
        sa.ForeignKeyConstraint(['player_id'], ['players.player_id']),
        sa.Column('fantasy_team_id', sa.Integer, primary_key=True),
        sa.ForeignKeyConstraint(['fantasy_team_id'], ['fantasy_teams.fantasy_team_id']),
    )

    


def downgrade() -> None:
    
    pass
