import os.path

from enum import Enum
from src.StorySquadAI.story_squad_ai import StorySquadAI
from fastapi import FastAPI, Query, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
# from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import src.StorySquadAI.WebApi.models as models
import src.StorySquadAI.WebApi.crud as crud
import src.StorySquadAI.WebApi.schemas as schemas

from src.StorySquadAI.WebApi.database import SessionLocal
from starlette.middleware.cors import CORSMiddleware


class BotName(str, Enum):
    bubblebot_v1 = 'bubblebot_v1',
    bubblebot_v2 = 'bubblebot_v2',
    bubblebot_v3 = 'bubblebot_v3',
    bubblebot_v4 = 'bubblebot_v4',
    bubblebot_v5 = 'bubblebot_v5',
    bubblebot_v6 = 'bubblebot_v6',
    bubblebot_v7 = 'bubblebot_v7',
    buzzkillbot_v1 = 'buzzkillbot_v1',
    buzzkillbot_v2 = 'buzzkillbot_v2',
    originaltestbot_v1 = 'originaltestbot_v1',
    bubblebot = 'bubblebot',
    buzzkillbot = 'buzzkillbot',
    originaltestbot = 'originaltestbot',
    Alphabot = 'Alphabot'


alias = {
    "bubblebot": "Alphabot"
}


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def setup():
    stsq_path = os.getenv("STORYSQUADAI_PATH")
    personality_data_dir = os.path.join(stsq_path, "data")
    web_api_path = os.path.join(stsq_path, "WebApi")

    hoax_api = StorySquadAI(data_dir=personality_data_dir, llm_provider_str="openai")

    app = FastAPI()

    origins = [
        "*",
        "172.125.186.85",
        "http://127.0.0.1:*",
        "http://localhost:*",
        "http://localhost",
        "http://localhost:3000",
        "https://new-wordhoax.herokuapp.com/",
        "https://new-wordhoax.herokuapp.com:*",
        "https://dev-wordhoax.netlify.app:*",

    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    for i in BotName:
        bots[i] = hoax_api.create_bot_with_personality(str(i).split(".")[1])
    return app


base_path = "/{api_key}"
bots = {}
#setup()


app = setup()
templates = Jinja2Templates(directory="templates")


def get_most_recent_bot_name_from_root(root_name):
    max_version_found = 0
    max_version_bot_name = ""
    for key in bots.keys():
        if root_name in key:
            v_idx = key.find("_v")
            if v_idx >= 0:
                version = int(key[v_idx + 2:])
                if version > max_version_found:
                    max_version_found = version
                    max_version_bot_name = key

    return de_alias_bot_name(max_version_bot_name)


def get_aliased_bot_roots_for_list(bot_list: list):
    out = []
    for in_name in bot_list:
        if "test" in in_name:
            pass
        elif "bubblebot" in in_name:
            out.append("Alphabot")
        else:
            out.append(in_name)
    return list(set(out))


def de_alias_bot_name(bot_name):
    if bot_name == "Alphabot":
        return "bubblebot"
    return bot_name


@app.post("/responses/", response_model=schemas.ResponseRecord)
def record_response(response: schemas.ResponseRecord, db: Session = Depends(get_db)):
    crud.create_response(db=db, record=response)


@app.get("/", response_class=HTMLResponse)
async def root_path():
    html = """
    
    """
    return "<a href='/docs/'>docs</a>"


@app.get(base_path + "/botlist/")
def bot_list_result(api_key: str = Query("default")):
    if api_key == "zetabot":
        return get_aliased_bot_roots_for_list([name for name in BotName.__members__.keys() if name.find("_v") == -1])
    else:
        return "not authorized"


def handle_bot_name(bot_name):
    if bot_name in alias.values():
        bot_name = de_alias_bot_name(bot_name)

    if bot_name[-2:-1] == "v":
        bot_name = bot_name
    else:
        bot_name = get_most_recent_bot_name_from_root(bot_name)
    return bot_name


@app.get(base_path + "/thing/{thing_name}/{bot_name}")
def thing_result(api_key, thing_name: str, bot_name: BotName):
    bot_name = handle_bot_name(bot_name)

    if api_key == "zetabot":
        output = bots[bot_name].thing(thing_name)
        return output
    else:
        return "not authorized"


@app.get(base_path + "/movie/{movie_title}/{bot_name}")
def movie_result(api_key, movie_title: str, bot_name: BotName):
    bot_name = handle_bot_name(bot_name)

    if api_key == "zetabot":
        output = bots[bot_name].movie(movie_title)
        return output
    else:
        return "not authorized"


@app.get(base_path + "/person/{person_name}/{bot_name}")
def person_result(api_key, person_name: str, bot_name: BotName):
    bot_name = handle_bot_name(bot_name)

    if api_key == "zetabot":
        output = bots[bot_name].person(person_name)
        return output
    else:
        return "not authorized"


@app.get(base_path + "/guess/{prompt}/{choices}/{bot_name}")
def guess_result(api_key, prompt: str, choices: str, bot_name: BotName, db: Session = Depends(get_db)):
    bot_name = handle_bot_name(bot_name)

    if api_key == "zetabot":
        output = bots[bot_name].guess(prompt, choices.split("*"))
        for response in choices.split("*"):
            if response != "":
                record = models.ResponseRecord()
                record.response = response
                record.is_bot = False
                crud.create_response(db=db, record=record)
        return output
    else:
        return "not authorized"


if __name__ == "__main__":
    uvicorn.run(app, port=80)

if __name__ == 'src.StorySquadAI.WebApi.app':
    print(__name__)
