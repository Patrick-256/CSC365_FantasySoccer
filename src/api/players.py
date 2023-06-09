from fastapi import APIRouter, HTTPException
from enum import Enum
from collections import Counter

from fastapi.params import Query
from src import database as db
import sqlalchemy
from sqlalchemy import func
from src.api import datatypes

from sqlalchemy.exc import IntegrityError
from psycopg2.errors import ForeignKeyViolation

router = APIRouter()


@router.post("/players/", tags=["players"])
def add_player(newPlayer: datatypes.Player):
    """
    This endpoint adds a player to the database
    * `player_name`: the name of the player
    * `player_position`: the position of the player Can be any of the following:
        GK, LB, CB, RB, CDM, CM, CAM, CF, ST, LM, RM, LW, RW, LWB, RWB
    * `irl_team_name`: the real life team of the player
    * 'player_value': the value of the player
    """

    if(newPlayer.player_value <= 0):
        raise HTTPException(422, "Value must be greater than $0")
    
    if(newPlayer.player_value > 10000000):
        raise HTTPException(422, "Value must be less than $10,000,000")
    
    with db.engine.begin() as conn:

        
        sql = """
            INSERT INTO players (player_name, player_position, irl_team_name, player_value)
            VALUES ((:name), (:position), (:irl_team_name), (:value))
            returning player_id
        """

        params = {
            'name':newPlayer.player_name,
            'position': newPlayer.player_position,
            'irl_team_name': newPlayer.irl_team_name,
            'value': newPlayer.player_value
        }
        try:
            new_player_id = conn.execute(sqlalchemy.text(sql),params).scalar_one()
        except sqlalchemy.exc.IntegrityError as e:
            error_msg = e.orig.diag.message_detail
            raise HTTPException(422, error_msg)


    return {"Player {} added.".format(new_player_id)}

    
@router.put("/players/{id}/info", tags=["players"])
def edit_player(id: int, position: str, irl_team_name: str, value: int):
    """
    This endpoint edits the follwoing player information of the specified player
    * `irl_team_name`: the real life team of the player
    * `player_position`: the position of the player
    * 'player_value': the value of the player

    """
    if(value <= 0):
        raise HTTPException(422, "Value must be greater than $0")

    with db.engine.begin() as conn:

        player_subq = """
            select player_id from players
            where player_id = (:player_id)
            """
        
        player_result = conn.execute(sqlalchemy.text(player_subq),{"player_id":id}).fetchone()

        if player_result is None:
            raise HTTPException(422, "Player not found.")
      
        current_player = """
            select * from players
            where players.player_id = (:id)
        """
        cur = conn.execute(sqlalchemy.text(current_player),{"id": id}).fetchone()
        if(position == ""):
            position = cur.player_position

        if(irl_team_name == ""):
            irl_team_name = cur.irs_team_name

        sql = """
            update players
            set irl_team_name = (:irl_team_name),
                player_position = (:position),
                player_value = (:value)
            where player_id = (:id)
        """

        params = {
          'irl_team_name': irl_team_name,
          'position': position,
          'id': id,
          'value': value
         }
        try:
            conn.execute(sqlalchemy.text(sql),params)
        except sqlalchemy.exc.IntegrityError as e:
            error_msg = e.orig.diag.message_detail
            raise HTTPException(422, error_msg)

    return {"Edited player {} info.".format(id)}


@router.get("/players/{id}", tags=["players"])
def get_player(id: int):
    """
    This endpoint returns a single player by its identifier. For each player
    it returns:
    * `player_id`: the internal id of the character. Can be used to query the
      `/characters/{character_id}` endpoint.
    * `player_name`: the name of the player
    * `player_position`: the position of the player
    * 'player_value': the value of the player
    * the following game stats (if the player has played in at least one game):
        number of total goals
        number of total assists
        number of total shots on goal
        number of total passes
        number of total turnovers

    """

    with db.engine.connect() as conn:

        player_subq = """
            select player_id from players
            where player_id = (:player_id)
            """
        
        player_subq_result = conn.execute(sqlalchemy.text(player_subq),{"player_id":id}).fetchone()

        if player_subq_result is None:
            raise HTTPException(422, "Player not found.")

        game_subq = """
            select player_id from games
            where player_id = (:player_id)
            """
        
        player_in_game_result = conn.execute(sqlalchemy.text(game_subq),{"player_id":id}).fetchone()

        if player_in_game_result is not None:

            sql = """
                SELECT
                players.player_id, 
                players.player_name, 
                players.player_position,
                players.irl_team_name,
                CONCAT('$', COALESCE(TO_CHAR(players.player_value, 'FM999,999,999,999'), 'NULL')) AS player_value,
                SUM(games.num_goals) AS total_num_goals,
                SUM(games.num_assists) AS total_num_assists,
                SUM(games.num_passes) AS total_num_passes,
                SUM(games.num_shots_on_goal) AS total_num_shots_on_goal,
                SUM(games.num_turnovers) AS total_num_turnovers
                FROM
                    players
                JOIN games ON games.player_id = players.player_id
                WHERE
                    players.player_id = (:id)
                GROUP BY
                    players.player_id, 
                    players.player_name, 
                    players.player_position,
                    players.irl_team_name,
                    players.player_value

            """
            result = conn.execute(sqlalchemy.text(sql), {'id':id}).fetchone()

            if result is None:
                raise HTTPException(422, "Player not found.")
        
        else: 

            p = """
                SELECT
                players.player_id, 
                players.player_name, 
                players.player_position,
                players.irl_team_name,
                CONCAT('$', COALESCE(TO_CHAR(players.player_value, 'FM999,999,999,999'), 'NULL')) AS player_value
                from players
                where player_id = (:player_id)
                """
            p_result = conn.execute(sqlalchemy.text(p),{"player_id":id}).fetchone()

            return {
                "player_id": p_result.player_id,
                "player_name": p_result.player_name,
                "player_position": p_result.player_position,
                "irl_team_name": p_result.irl_team_name,
                "player_value": p_result.player_value
            }


    return {
        "player_id": result.player_id,
        "player_name": result.player_name,
        "player_position": result.player_position,
        "irl_team_name": result.irl_team_name,
        "player_value": result.player_value,
        "total_num_goals": result.total_num_goals,
        "total_num_assists": result.total_num_assists,
        "total_num_passes": result.total_num_passes,
        "total_num_shots_on_goal": result.total_num_shots_on_goal,
        "total_num_turnovers": result.total_num_turnovers   
    }
        


class player_sort_options(str, Enum):
    goals = "num_goals"
    assists = "num_assists"
    shots_on_goal = "num_shots_on_goal"
    passes = "num_passes"
    turnovers = "num_turnovers"
    value = "player_value"


@router.get("/players/", tags=["players"])
def get_players(sort: player_sort_options = player_sort_options.goals,
                limit: int = Query(50, ge=1, le=250)):
    """
    list players in order of the specified sort up to the limit
    can sort by: number of goals, number of assists, number of shots on goal,
    number of turnovers or player value.

    returns a sorted list of players
    """

    with db.engine.connect() as conn:

        sql = """
              SELECT
            players.player_id, 
            players.player_name, 
            players.player_position,
            players.irl_team_name,
            CONCAT('$', TO_CHAR(players.player_value, 'FM999,999,999,999')) AS value,
            SUM(games.num_goals) AS num_goals,
            SUM(games.num_assists) AS num_assists,
            SUM(games.num_passes) AS num_passes,
            SUM(games.num_shots_on_goal) AS num_shots_on_goal,
            SUM(games.num_turnovers) AS num_turnovers
            FROM
            players
            JOIN games ON games.player_id = players.player_id
            GROUP BY
                players.player_id, 
                players.player_name, 
                players.player_position,
                players.irl_team_name,
                players.player_value
            ORDER BY {} desc, players.player_value desc
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
        "player_value": row.value,
        "total_num_goals": row.num_goals,
        "total_num_assists": row.num_assists,
        "total_num_passes": row.num_passes,
        "total_num_shots_on_goal": row.num_shots_on_goal,
        "total_num_turnovers": row.num_turnovers   
      }
        players.append(player)

    return players