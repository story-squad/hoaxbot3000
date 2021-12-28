import os.path
from flask import request, redirect
from flask import Flask
from enum import Enum
from WordHoaxAI.contestant import WordHoaxAI
from fastapi import FastAPI, Path, Depends
from fastapi.responses import HTMLResponse
import hashlib
from fastapi import HTTPException

import uvicorn

base_path = "/{api_key}"

app = FastAPI()

bots = {}
this_dir = os.path.dirname( __file__)
hoax_api = WordHoaxAI(data_dir=os.path.join(this_dir, "data"))
bots["bot_zero"] = hoax_api.create_bot_with_personality("originaltestbot")
bots["bubblebot"] = hoax_api.create_bot_with_personality("bubblebot")
bots["buzzkillbot"] = hoax_api.create_bot_with_personality("buzzkillbot")



# app = Flask(__name__)
class BotName(str, Enum):
    BotZero = "bot_zero",
    BubbleBot = "bubblebot",
    BuzzKillBot = "buzzkillbot"


@app.get("/", response_class=HTMLResponse)
def root_path():
    return "<a href='/docs/'>docs</a>"


@app.get(base_path + "/thing/{thing_name}/{bot_name}")
def thing_result(api_key, thing_name: str, bot_name: BotName):
    if api_key == "zetabot":
        output = bots[bot_name].thing(thing_name)
        return output
    else:
        return "not authorized"


@app.get(base_path + "/movie/{movie_title}/{bot_name}")
def movie_result(api_key, movie_title: str, bot_name: BotName):
    if api_key == "zetabot":
        output = bots[bot_name].movie(movie_title)
        return output
    else:
        return "not authorized"


@app.get(base_path + "/person/{person_name}/{bot_name}")
def person_result(api_key, person_name: str, bot_name: BotName):
    if api_key == "zetabot":
        output = bots[bot_name].person(person_name)
        return output
    else:
        return "not authorized"


@app.get(base_path + "/guess/{prompt}/{choices}/{bot_name}")
def guess_result(api_key, prompt: str, choices: str, bot_name: BotName):
    if api_key == "zetabot":
        output = bots[bot_name].guess(prompt, choices.split("*"))
        return output
    else:
        return "not authorized"


if __name__ == "__main__":
    uvicorn.run(app)
