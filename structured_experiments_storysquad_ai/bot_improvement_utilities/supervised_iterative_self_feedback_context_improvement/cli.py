import os.path

import openai
import json

import pandas as pd
from matplotlib.pyplot import xlabel

from StorySquadAI.contestant import StorySquadAI
import bot_personalities
import matplotlib.pyplot as plt
from bot_personalities import BotName as bot_names
from structured_experiments_storysquad_ai.bot_improvement_utilities.generate_responses_to_grade import \
    get_extended_query_list
import pandas
import numpy as np
import random


class SupervisedIterative:

    def __init__(self):
        self.query_dict = self.setup()

        self.hoax_ai = StorySquadAI(data_dir="../../../data//")
        self.results = {}

    def setup(self):
        _query_list = get_extended_query_list()
        _query_dict = {"thing": {item[0] for item in _query_list}, "person": {item[1] for item in _query_list},
                       "movie": {item[2] for item in _query_list}}

        return _query_dict

    def supervise(self, response_type: str):
        if not self.results[response_type]:
            self.results[response_type] = {}

        set_as_list = list(self.query_dict[response_type])
        random.shuffle(set_as_list)
        prompt = set_as_list[0]
        self.query_dict[response_type] = set(set_as_list[1:])

        eval_str = f"self.bot.{response_type}('{prompt}')"
        response = eval(eval_str)

        print(f"Prompt: {prompt}")
        print(f"Response: {response}")
        good = input(f"Include in new context doc for {response_type} ?")

        if "y" in good.lower():
            self.results[response_type][prompt] = response

    def go(self, number_per_category):
        print(bot_names._member_names_)
        base_bot_name = input("use which bot as base?")
        self.bot = self.hoax_ai.create_bot_with_personality(base_bot_name)
        self.bot.engine_to_use = "curie"
        filename = f"{self.bot.engine_to_use}_{base_bot_name}_iterative.json"
        pathname = os.path.dirname(__file__)
        try:
            with open(os.path.join(pathname, filename), "r") as f:
                self.results = json.loads(f.read())
        except FileNotFoundError as e:
            print("new results file created.")

        for i, _list in enumerate(["thing", "person", "movie"]):
            if _list not in self.results.keys(): self.results[_list] = {}
            while len(self.results[_list]) < number_per_category:
                self.supervise(_list)
                print(f'{number_per_category - len(self.results[_list])} more to go!\n')
                json_out = json.dumps(self.results)
                with open(os.path.join(pathname, filename), "w") as f:
                    f.write(json_out)
            print(f'{_list} done.')


if __name__ == "__main__":
    process = SupervisedIterative()
    process.go(20)
