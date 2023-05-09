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
class PlayerTeam:
    player_id: int
    fantasy_team_id: int

@router.post("/fantasy_teams/", tags=["fantasy_teams"])
def create_fantasy_team(user_id: int, name: str):
    """Adds a new fantasy team with the
       specified user id
       """
    
    conn = db.engine.connect()

    max_id = conn.execute(sqlalchemy.select(func.max(db.fantasy_teams.c.fantasy_team_id))).scalar()
    new_id = (max_id or 0) + 1

    sql = """
          INSERT INTO fantasy_teams (fantasy_team_id, fantasy_team_name, user_id)
          VALUES ("""+new_id+", "+name+", "+user_id+""")
    """

    conn.execute(sqlalchemy.text(sql))

    return new_id
    

@router.post("/fantasy_teams/{fantasy_team_id}/players", tags=["fantasy_teams"])
def add_player_to_fantasy_team(player_team: PlayerTeam):
    """adds a player to the specified fantasy team
    """

    conn = db.engine.connect()


    sql = """
          INSERT INTO player_fantasy_team (player_id, fantasy_team_id)
          VALUES ({},{})""".format(player_team.player_id, player_team.fantasy_team_id)

    conn.execute(sqlalchemy.text(sql))

    return {"Added player to team"}


@router.delete("/fantasy_teams/{fantasy_team_id}/players", tags=["fantasy_teams"])
def remove_player_from_fantasy_team(player_id: int, fantasy_team_id: str):
    """removes a player from the specified fantasy team
    """


@router.get("/fantasy_teams/{fantasy_team_id}/score", tags=["fantasy_teams"])
def get_fantasy_team_score(fantasy_team_id: int):
    """return the score of the specified fantasy team,
       which is a sum of the team's player scores"""
    

@router.put("/users/{fantasy_league_id}/join", tags=["users"])
def add_team_to_fantasy_league(team_id: int, league_id: int):
    """
    This endpoint adds a user to a fantasy league
    It sets the league_id column of a team
    """

    conn = db.engine.connect()

    sql = """
          update fantasy_teams
          set fantasy_league_id = """+league_id+"""
          where team_id = """+team_id
        

    conn.execute(sqlalchemy.text(sql))

    return (team_id, league_id)
    

    




