import os.path

import openai
import json

import pandas as pd
from matplotlib.pyplot import xlabel
from setuptools import glob

from StorySquadAI.contestant import StorySquadAI
import bot_personalities
import matplotlib.pyplot as plt
from bot_personalities import BotName as bot_names
from structured_experiments_storysquad_ai.bot_improvement_utilities.generate_responses_to_grade import \
    get_extended_query_list
import pandas
import numpy as np
import random
import yaml
from yaml import CLoader as Loader, CDumper as Dumper


class ConvertJsonToNewBot:
    def __init__(self, bot_name: str = "", json_name: str = ""):
        self.bot_name = bot_name
        self.json_name = json_name

    def go(self):
        if not self.bot_name:
            self.bot_name = input("name_version of the bot? (ie 'bubblebot_v5') : ")

        if not self.json_name:
            a = glob.glob("*.json")
            print(f"json files found in {os.path.dirname(__file__)}")
            for f in a:
                print(f'\t{f}')

            self.json_name = input("filename of the json file? ")

            if self.json_name[-4:] != "json":
                self.json_name = self.json_name + ".json"

        print(f"using {self.bot_name} as the bot name")
        print(f"using {self.json_name} as the json file to import from")
        self.json_file_data = open(self.json_name, "r").read()
        self.json_data_object = json.loads(self.json_file_data);

        q_token = "6312641351"
        r_token = "9384987534"

        self.formatter = {
            "thing": f"C: What is {q_token}?\n{r_token}\n\n",
            "movie": f"C: Movie: {q_token}?\n{r_token}\n\n",
            "person": f"C: Who is/was {q_token}?\n{r_token}\n\n",
        }
        self.SSAI = StorySquadAI(data_dir="../../../data//")
        self.default_response_params = yaml.load(self.SSAI.default_yaml, Loader)

        self.personality = StorySquadAI.Personality(responses=
        {k: StorySquadAI.PersonalityRequestData(
            logit_bias=self.default_response_params[k]["logit_bias"],
            max_tokens=self.default_response_params[k]["max_tokens"],
            temperature=self.default_response_params[k]["temperature"],
            top_p=self.default_response_params[k]["top_p"],
            context_doc=''.join(
                [self.formatter[k].replace(q_token, q.replace("\n", "")).replace(r_token, r.replace("\n", "")) for q, r
                 in v.items()])

        )

            for k, v in self.json_data_object.items()}
        )
        self.new_bot = self.SSAI.create_bot_with_personality(personality=self.bot_name,
                                                             personality_data=self.personality)
        print(self.personality)
        self.SSAI.save_bot(self.new_bot)


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
    process = ConvertJsonToNewBot(bot_name="bubblebot_v6", json_name="curie_bubblebot_v5_iterative.json")
    process.go()
