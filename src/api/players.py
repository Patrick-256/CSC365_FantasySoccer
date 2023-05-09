from fastapi import APIRouter, HTTPException
from enum import Enum
from collections import Counter

from fastapi.params import Query
from src import database as db
import sqlalchemy
from sqlalchemy import func
import pydantic.dataclasses

router = APIRouter()

@pydantic.dataclasses.dataclass
class User:
    # user_id: int
    user_name: str
    is_admin: bool
    # fantasy_team_id: int
    # fantast_league_id: int
    
@pydantic.dataclasses.dataclass
class Player:
    player_id: int
    player_name: str
    player_position: str
    irl_team_name: str

@pydantic.dataclasses.dataclass
class Fantasy_Team:
    fantasy_team_id: int
    fantasy_team_name: str
    user_id: int

@pydantic.dataclasses.dataclass
class Friend:
    user1_id: int
    user2_id: int

@pydantic.dataclasses.dataclass
class PlayerTeam:
    player_id: int
    fantasy_team_id: int

@router.post("/players/", tags=["players"])
def add_player(name: str, irl_team_name: str, position: str):
    """
    This endpoint adds a player to the database
    * `player_id`: the internal id of the player. 
    * `player_name`:
    * `player_position`:
    """

    with db.engine.begin() as conn:


      sql = """
            INSERT INTO players (player_name, player_position, irl_team_name)
            VALUES ((:name), (:position), (:irl_team_name))
      """

      params = {
            'name':name,
            'position': position,
            'irl_team_name': irl_team_name
      }

      conn.execute(sqlalchemy.text(sql),params)

    return {"New player added."}

    
@router.put("/players/{id}/info", tags=["players"])
def edit_player(id: int, position: str, irl_team_name: str):
    """
    This endpoint edits player statistics in the database
    * `player_id`: the internal id of the player. 
    * `irl_team_name`:
    * `player_position`:
    """

    with db.engine.begin() as conn:

      sql = """
            update players
            set irl_team_name = (:irl_team_name),
                player_position = (:position)
            where player_id = (:id)
      """

      params = {
          'irl_team_name': irl_team_name,
          'position': position,
          'id': id
      }

      conn.execute(sqlalchemy.text(sql),params)

    return {"Edited player info."}


@router.get("/players/{id}", tags=["players"])
def get_player(id: int):
    """
    This endpoint returns a single player by its identifier. For each player
    it returns:
    * `player_id`: the internal id of the character. Can be used to query the
      `/characters/{character_id}` endpoint.
    * `player_name`:
    * `player_position`
    * game stats
    """

    with db.engine.connect() as conn:

      sql = """
            select players.player_id, 
            players.player_name, 
            players.player_position,
            players.irl_team_name,
            games.num_goals,
            games.num_assists,
            games.num_passes,
            games.num_shots_on_goal,
            games.num_turnovers
            from players
            join games on games.player_id = players.player_id
            where players.player_id = (:id)
      """

      result = conn.execute(sqlalchemy.text(sql), {'id':id}).fetchone()

    return {
        "player_id": result.player_id,
        "player_name": result.player_name,
        "player_position": result.player_position,
        "irl_team_name": result.irl_team_name,
        "num_goals": result.num_goals,
        "num_assists": result.num_assists,
        "num_passes": result.num_passes,
        "num_shots_on_goal": result.num_shots_on_goal,
        "num_turnovers": result.num_turnovers   
    }
        


class player_sort_options(str, Enum):
    goals = "num_goals"
    assists = "num_assists"
    shots = "num_shots"
    shots_on_goal = "num_shots_on_goal"
    games_played = "num_games_played"


@router.get("/players/", tags=["players"])
def get_players(sort: player_sort_options = player_sort_options.goals,
                limit: int = Query(50, ge=1, le=250)):
    """
    """

    with db.engine.connect() as conn:

      sql = """
            select players.player_id, 
            players.player_name, 
            players.player_position,
            players.irl_team_name,
            games.num_goals,
            games.num_assists,
            games.num_passes,
            games.num_shots_on_goal,
            games.num_turnovers
            from players
            join games on games.player_id = players.player_id
            order by {} desc
            limit (:limit)
            """.format(sort.value)
      
      params = {
          'limit': limit
      }
      
      result = conn.execute(sqlalchemy.text(sql), params)

    players = []

    for row in result:
      player = {
        "player_id": row.player_id,
        "player_name": row.player_name,
        "player_position": row.player_position,
        "irl_team_name": row.irl_team_name,
        "num_goals": row.num_goals,
        "num_assists": row.num_assists,
        "num_passes": row.num_passes,
        "num_shots_on_goal": row.num_shots_on_goal,
        "num_turnovers": row.num_turnovers   
      }
      players.append(player)

    return players



