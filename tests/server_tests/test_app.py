from fastapi import FastAPI
from fastapi.testclient import TestClient
from StorySquadAI_web_api.app import app

test_client = TestClient(app)

def test_setup():
    response = test_client.get("/")
    assert response.status_code == 200


