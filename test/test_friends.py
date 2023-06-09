from fastapi.testclient import TestClient

from src.api.server import app

import json
import src.database as db
import sqlalchemy


client = TestClient(app)

def test_get_friends():
    response = client.get("/friends/")
    assert response.status_code == 200

    assert response.json()[0] ==  {
    "user1_id": 0,
    "user2_id": 1,
    "created_at": "2023-05-08T21:49:21.359839+00:00"
  }
    
def test_add_friend():
    test_friendship = { #this wont work in future versions when we verify the users exist
        "user1_id": 44,
        "user2_id": 45
    }
    response = client.post("/friends/", json=test_friendship)
    assert response.status_code == 200

    #clean up
    with db.engine.begin() as conn:

        sql = """
            DELETE FROM friends
            WHERE user1_id = 44 and user2_id = 45
            """
        conn.execute(sqlalchemy.text(sql))

    
