import os.path
from flask import request, redirect
from flask import Flask
from enum import Enum
from contestant import WordHoxBot
from fastapi import FastAPI, Path

import uvicorn

app = FastAPI()
bots = {}
bots["bot_zero"] = WordHoxBot()


# app = Flask(__name__)
class BotName(str, Enum):
    BotZero = "bot_zero"


@app.get("/")
def hello_world():
    return "<HTML><a href = '/thing'>thing</a></HTML>"


@app.get("/thing/{thing_name}/{bot_name}")
def thing_result(thing_name: str, bot_name: BotName):
    output = bots[bot_name].thing(thing_name)
    return output


@app.get("/movie/{movie_title}/{bot_name}")
def movie_result(movie_title: str, bot_name: BotName):
    output = bots[bot_name].movie(movie_title)
    return output


@app.get("/person/{person_name}/{bot_name}")
def person_result(person_name: str, bot_name: BotName):
    output = bots[bot_name].person(person_name)
    return output


@app.get("/guess/{prompt}/{choices}/{bot_name}")
def guess_result(prompt: str, choices: str, bot_name: BotName):
    output = bots[bot_name].guess(prompt, choices.split("*"))
    return output


if __name__ == "__main__":
    uvicorn.run(app)
