# coding=utf8
import glob
import os
import random
import openai
import pandas as pd

openai.api_key = os.getenv("OPENAI_API_KEY")

start_sequence = "The answer is:"
hoax = "apple"
choices_default = ["1) squishy fruit",
                   "2) square vegetable",
                   "3) purple integrated circuit"]
prompt_default = "apple"
engine_to_use = 'curie'


class WordHoaxAI:
    """
    Class which manages the word hoax AI environment and provides access to AI
    """

    class WordHoaxBot:
        """
        temperature_coeff:

        max_tokens_coeff:

        top_p_coeff:

        frequency_penalty_coeff:

        presence_penalty_coeff:

        """
        listed_keys = ['temperature_coeff', 'max_tokens_coeff', 'top_p_coeff', 'frequency_penalty_coeff',
                       'presence_penalty_coeff']

        def __init__(self, context_dir: str = "data", engine='curie', **kwargs):
            self.context_dir = context_dir
            self.context_movie = open(os.path.join(self.context_dir, "movie.context.txt"), encoding="utf-8").read()
            self.context_person = open(os.path.join(self.context_dir, "person.context.txt"), encoding="utf-8").read()
            self.context_thing = open(os.path.join(self.context_dir, "thing.context.txt"), encoding="utf-8").read()
            self.engine_to_use = engine

            _dict = {}
            # Set default values for listed keys
            for item in self.listed_keys:
                _dict[item] = 1
            # Update the dictionary with all kwargs
            _dict.update(kwargs)

            # Have the keys of kwargs as instance attributes
            self.__dict__.update(_dict)

        def person(self, person: str):
            response = openai.Completion.create(
                engine=self.engine_to_use,
                prompt=f"{self.context_person}C: Who is/was {person}?\n",
                temperature=0.26,
                max_tokens=155,
                top_p=0.5,
                frequency_penalty=1.04,
                presence_penalty=0.99,
                stop=["C: Who"]
            )
            possible_response = response["choices"][0]["text"]
            return possible_response

        def guess(self, prompt: str, choices: list):
            response = openai.Engine(self.engine_to_use).search(
                documents=choices,
                query=prompt
            )

            df = pd.DataFrame(response["data"])
            df.sort_values(by="score", inplace=True)
            pick = choices[df.iloc[-1].document]
            context = ".".join(choices)
            prompt = f"I'm going to go with {pick} because"
            response = openai.Completion.create(
                engine=self.engine_to_use,
                prompt=context + prompt,
                temperature=1,
                max_tokens=50,
                top_p=.7,
                best_of=1,
                frequency_penalty=.2,
                presence_penalty=0,
                stop="."
            )
            return f'{prompt} :: {response["choices"][0]["text"]}.'

        def thing(self, prompt: str):

            possible_response = ""

            for _ in range(30):

                response = openai.Completion.create(
                    engine=self.engine_to_use,
                    prompt=f'{self.context_thing}C: what is {prompt}?\n',
                    temperature=.51,
                    max_tokens=150,
                    top_p=1,
                    best_of=1,
                    frequency_penalty=.0,
                    stop="\n\n"
                )
                possible_response = response["choices"][0]["text"]

                if possible_response.__len__() >= 30:
                    return possible_response

        def movie(self, movie: str):
            response = openai.Completion.create(
                engine=self.engine_to_use,
                prompt=f"{self.context_movie}C: Movie:{movie}?\n",
                temperature=.98,
                max_tokens=155,
                top_p=1,
                frequency_penalty=2,
                presence_penalty=0,
                stop=["C: Movie:"]
            )
            possible_response = response["choices"][0]["text"]
            return possible_response

    def init_error(self, e):
        raise Exception(e)

    def __init__(self, data_dir=f"./data", **kwargs):
        self.data_dir = os.path.realpath(data_dir)
        self.data_dir_glob_str = os.path.join(self.data_dir, "*")
        self.data_dir_glob = glob.glob(self.data_dir_glob_str)

        self.personalities_dir = os.path.realpath(os.path.join(data_dir, "personalities"))
        self.personalities_dir_str = os.path.join(self.personalities_dir, "*")
        self.personalities_dir_glob = glob.glob(self.personalities_dir_str)

        self.data_dir_glob = glob.glob(self.data_dir_glob_str)
        self.personalities = self.list_personalities()

        True if self.personalities_dir in self.data_dir_glob else self.init_error(f"invalid data dir {self.personalities_dir} does not exist in ({os.path.realpath(self.data_dir)})")

    def list_personalities(self):
        return [os.path.basename(personality) for personality in self.personalities_dir_glob]

    def create_bot_with_personality(self, personality: str) -> WordHoaxBot:
        if personality in self.personalities:
            ctx_dir = os.path.join(self.personalities_dir, personality)
            return WordHoaxAI.WordHoaxBot(context_dir=ctx_dir)


if __name__ == "__main__":
    HoaxAI = WordHoaxAI()
    print(HoaxAI.list_personalities())

    bubble_testbot = HoaxAI.create_bot_with_personality("bubblebot")
    buzzkill_testbot = HoaxAI.create_bot_with_personality("buzzkillbot")
    print("what is a Clatau Noctu?")
    print("Bubble bot:")
    a = bubble_testbot.thing("Clatau Noctu")
    print(a)

    print("\nBuzzkill bot:")
    b = buzzkill_testbot.thing("Clatau Noctu")
    print(b)

    ########
    print("\n\nWho is/was Jennie Sky Kent ")
    print("Bubble bot:")
    a = bubble_testbot.person("Jennie Sky Kent")
    print(a)

    print("\nBuzzkill bot:")
    b = buzzkill_testbot.person("Jennie Sky Kent")
    print(b)


    print("\n\nwhat is the movie 'A thing called Wanda' about?")
    print("Bubble bot:")
    a = bubble_testbot.movie("A thing called Wanda")
    print(a)

    print("\nBuzzkill bot:")
    b = buzzkill_testbot.movie("A thing called Wanda")
    print(b)
    # menu = [f'exit',
    #         f'guess',
    #         f'thing',
    #         f'person',
    #         f'movie',
    #         ]
    # menu = '\n\t' + '\n\t'.join(menu)
    # contestant_bot = WordHoaxBot()
    # while (a := input(f"what to do? {menu}\n\n>")) != "exit":
    #     print(a)
    #     if a.lower() == "guess":
    #         paste = input("paste the choices here seperated by * :")
    #         if paste == "":
    #             choices = choices_default
    #             prompt = prompt_default
    #         else:
    #             choices = paste.split("*")
    #             prompt = input("what was the prompt?")
    #
    #         contestant_bot.guess(prompt, choices)
    #
    #     elif a.lower() == "thing":
    #         prompt = input("Name of the thing?\n")
    #         definition = contestant_bot.thing(prompt)
    #         print(definition)
    #
    #     elif a.lower() == "person":
    #         prompt = input("Persons name?\n")
    #         definition = contestant_bot.person(prompt)
    #         print(definition)
    #
    #     elif a.lower() == "movie":
    #         prompt = input("prompt?\n")
    #         definition = contestant_bot.movie(prompt)
    #         print(definition)
