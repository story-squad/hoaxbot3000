

# HoaxBot3000 Web API

## Overview
The Web API serves as an interface to interact with the `StorySquadAI` through HTTP requests. It is built with FastAPI and allows for managing and querying AI-generated content.

## Features
- Multiple endpoints to interact with different AI personalities.
- Record and retrieve responses.
- CORS support for cross-origin requests.

## Installation
Ensure you have `fastapi`, `uvicorn`, `sqlalchemy`, and other dependencies installed. You can install them using pip:
```bash
pip install fastapi uvicorn sqlalchemy
```

## Usage
Set the `STORYSQUADAI_PATH` environment variable to the path where your `data` and `WebApi` directories are located. Run the API server with Uvicorn:
```bash
uvicorn src.StorySquadAI.WebApi.app:app --port 80
```

## API Endpoints
- `POST /responses/`: Record a response to the database.
- `POST /wordhoax/`: Generate a word hoax based on the given prompt and definition type.
- `GET /botlist/`: Get a list of available AI bots.
- `GET /thing/{thing_name}/{bot_name}`: Get a response from a specific bot about a thing.
- `GET /movie/{movie_title}/{bot_name}`: Get a movie response from a specific bot.
- `GET /person/{person_name}/{bot_name}`: Get a person response from a specific bot.
- `GET /guess/{prompt}/{choices}/{bot_name}`: Get a guess response from a specific bot.

The API uses API keys for authorization, and the endpoints are designed to respond only to authorized requests.

## Environment Variables
- `STORYSQUADAI_PATH`: The path to the `StorySquadAI` data directory.

