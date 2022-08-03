import os.path

import openai
import json
from src.StorySquadAI.Alphabots.story_squad_bot import StorySquadBot
from src.StorySquadAI.story_squad_ai import StorySquadAI


def get_embedding(bot: StorySquadBot, s: str = "test string"):
    embedding = openai.Engine(id=f"{bot.engine_to_use}-similarity").embeddings(input=s)['data'][0]['embedding']
    return embedding


def get_responses_for_bot_for_query_list(bot, query_list):
    out_queries = []
    out_results = []
    out_result_embeddings = []
    for query_tuple in query_list:
        thing_res = bot.thing(prompt=query_tuple[0])
        out_result_embeddings.append(get_embedding(bot, thing_res))
        out_results.append(thing_res)
        out_queries.append(query_tuple[0])

        person_res = bot.person(person=query_tuple[1])
        out_result_embeddings.append(get_embedding(bot, person_res))
        out_results.append(person_res)
        out_queries.append(query_tuple[1])

        movie_res = bot.movie(movie=query_tuple[2])
        out_result_embeddings.append(get_embedding(bot, movie_res))
        out_results.append(movie_res)
        out_queries.append(query_tuple[2])

    return out_results, out_result_embeddings, out_queries


def create_save_bot_results_for_bot(query_list: [(str, str, str)], bot: str, number: int = 1, engine: str = "ada"):
    _hoax_ai = StorySquadAI(data_dir="../../data//")
    _bot = _hoax_ai.create_bot_with_personality(bot)
    _bot.engine_to_use = engine
    _bot_results, _bot_embeddings, _ = \
        get_responses_for_bot_for_query_list(_bot, query_list[0:number])
    all_out_results = {}
    for i, _list in enumerate(["thing", "person", "movie"]):
        out_results = json.dumps(_bot_results[i::3])
        out_embeddings = json.dumps(_bot_embeddings[i::3])

        with open(f"{_bot.engine_to_use}_{bot}_{_list}_result.txt", "w") as f:
            f.write(out_results)
        with open(f"{_bot.engine_to_use}_{bot}_{_list}_embeddings.txt", "w") as f:
            f.write(out_embeddings)
        print(f'{_list} done.')
        all_out_results[_list] = out_results
    return all_out_results


def get_extended_query_list():
    base_dir = os.path.dirname(__file__)
    files = [f"things_100.txt", f"names_100.txt", f"movies_100.txt"]
    files = map(lambda x: os.path.join(base_dir, x), files)
    extended_query_list = []
    for file_name in files:
        with open(file_name) as f:
            extended_query_list.append(f.read().splitlines())
    extended_query_list = zip(*extended_query_list)
    extended_query_list = [(a, b, c) for a, b, c in extended_query_list]
    return extended_query_list


if __name__ == "__main__":
    HoaxAI = StorySquadAI(data_dir="../../data//")

    which_bot = input("Which bot? ")
    query_list = get_extended_query_list()

    results = create_save_bot_results_for_bot(query_list, which_bot, number=50, engine="curie")
