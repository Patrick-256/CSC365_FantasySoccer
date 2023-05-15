from fastapi import APIRouter, HTTPException
from enum import Enum
from collections import Counter

from fastapi.params import Query
from src import database as db
import sqlalchemy
from sqlalchemy import func
from src.api import datatypes

router = APIRouter()


@router.post("/fantasy_leagues/", tags=["fantasy_leagues"])
def create_fantasy_league(new_fantasy_league_name: str):
    """
    Adds a new fantasy league with the
    specified name, adds user to league
    """

    insert_statement = """
    INSERT INTO fantasy_leagues (fantasy_league_name)
    VALUES ((:new_name))
    """

    params = {'new_name':new_fantasy_league_name}

    with db.engine.begin() as conn:
        new_league_id = conn.execute(sqlalchemy.text(insert_statement),params)

    return {"Added fantasy league {} to the database!".format(new_league_id.fantasy_league_id)}



@router.get("/fantasy_leagues/", tags=["fantasy_leagues"])
def list_fantasy_leagues():
    """
    lists the fantasy leagues from the table
    """

    sql = """select * from fantasy_leagues"""
    
    with db.engine.connect() as conn:
        result = conn.execute(sqlalchemy.text(sql))
        res_json = []
        for row in result:
            res_json.append({
                "fantasy_league_id":row.fantasy_league_id,
                "fantasy_league_name":row.fantasy_league_name,
                "created_at":row.created_at,
            })
    
    return res_json


@router.get("/fantasy_leagues/{fantasy_league_id}", tags=["fantasy_leagues"])
def get_top_teams_in_fantasy_league(id: int):
    """
    Lists teams in the specified league in order of total points.
    Total points is calculated based on the following formula:
    total_points = num_goals*5 + num_assists*3 + num_passes*0.05 + num_shots_on_goal*0.2 - num_turnovers*0.2
    """
    sql = """SELECT 
                fantasy_teams.fantasy_team_id,
                SUM(games.num_goals * 5 + games.num_assists * 3 + games.num_passes * 0.05 + games.num_shots_on_goal * 0.2 - games.num_turnovers * 0.2) AS total_points
            FROM fantasy_teams
            JOIN player_fantasy_team ON fantasy_teams.fantasy_team_id = player_fantasy_team.fantasy_team_id
            JOIN games ON player_fantasy_team.player_id = games.player_id
            WHERE fantasy_teams.fantasy_league_id = :id
            GROUP BY fantasy_teams.fantasy_team_id
            ORDER BY total_points DESC
            """
    params = {'id': id}

    with db.engine.connect() as conn:
        result = conn.execute(sqlalchemy.text(sql), params)
        res_json = []
        for row in result:
            res_json.append({
                "fantasy_team_id": row.fantasy_team_id,
                "total_points": row.total_points,
            })
    
    return res_json


    
#this one doesnt work yet
@router.get("/fantasy_leagues/leaderboard", tags=["fantasy_leagues"])
def get_top_fantasy_leagues():
    """
    lists fantasy leagues by score of the highest scoring team in the league.
    """

    sql = """SELECT fantasy_teams.fantasy_league_id, 
                    fantasy_teams.fantasy_team_id, 
                    SUM(games.num_goals*5 + games.num_assists*3 + games.num_passes*0.05 + games.num_shots_on_goal*0.2 - games.num_turnovers*0.2) AS total_points
            FROM fantasy_teams
            JOIN player_fantasy_team ON fantasy_teams.fantasy_team_id = player_fantasy_team.fantasy_team_id
            JOIN games ON player_fantasy_team.player_id = games.player_id
            GROUP BY fantasy_teams.fantasy_league_id, fantasy_teams.fantasy_team_id
            ORDER BY total_points DESC"""
    
    with db.engine.connect() as conn:
        result = conn.execute(sqlalchemy.text(sql))
        res_json = []
        for row in result:
            res_json.append({
                "fantasy_league_id": row.fantasy_league_id,
                "fantasy_team_id": row.fantasy_team_id,
                "total_points": row.total_points,
            })
        return res_json


