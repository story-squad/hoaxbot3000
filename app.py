import datetime
import os.path

import bot_personalities
from StorySquadAI.contestant import StorySquadAI
from fastapi import FastAPI, HTTPException, Query
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
# from fastapi.middleware.cors import CORSMiddleware

from starlette.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware

alias = {
    "bubblebot": "Alphabot"
}


def setup():
    this_dir = os.path.dirname(__file__)
    this_data_dir = os.path.join(this_dir, "data")
    hoax_api = StorySquadAI(data_dir=this_data_dir)

    app = FastAPI()

    origins = [
        "*",
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

    if "Enclosure to handle personality enumeration":
        file_needs_replaced = False
        bot_personalities_enum_file_py = os.path.join(this_dir, "bot_personalities.py")
        file_out = f"# Do not edit this file, it is automatically generated when {os.path.basename(__file__)}; is " \
                   f"executed last run {datetime.datetime.now()}\n "
        personalities = hoax_api.list_personalities()

        file_out = file_out + "\nfrom enum import Enum\n\n\nclass BotName(str,Enum):\n"
        personality_roots = set()
        for personality in personalities:
            version_idx = personality.find("_v")
            if version_idx >= 0:
                personality_roots.add(personality[:version_idx])

        personality_roots = sorted(personality_roots)
        for root in personality_roots:
            personalities.append(root)
        for a in alias.values():
            personalities.append(a)

        for personality in personalities:
            file_out = file_out + f"\t{personality} = '{personality}',\n"
        try:
            current_file = open(bot_personalities_enum_file_py, "r+").read()
            file_without_header = current_file.splitlines()[1:]
            current_file = ''.join(file_without_header)
            compare_file_out = ''.join(file_out.splitlines()[1:])
            if current_file != compare_file_out:
                file_needs_replaced = True
        except FileNotFoundError as e:
            file_needs_replaced = True

        if file_needs_replaced:
            print("file needs update")
            with open(bot_personalities_enum_file_py, "w+") as f:
                f.write(file_out)
            print("Server updated please restart.")
            exit()
    for i in bot_personalities.BotName:
        bots[i] = hoax_api.create_bot_with_personality(str(i).split(".")[1])
    return app


base_path = "/{api_key}"
bots = {}
setup()
from bot_personalities import BotName

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


@app.get("/", response_class=HTMLResponse)
def root_path():
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
def guess_result(api_key, prompt: str, choices: str, bot_name: BotName):
    bot_name = handle_bot_name(bot_name)

    if api_key == "zetabot":
        output = bots[bot_name].guess(prompt, choices.split("*"))
        return output
    else:
        return "not authorized"


if __name__ == "__main__":
    uvicorn.run(app)
