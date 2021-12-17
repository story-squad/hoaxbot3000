# coding=utf8
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

class WordHoaxBot:
    def __init__(self, context_dir: str = "data", engine='curie'):
        self.context_dir = context_dir
        self.context_movie = open(os.path.join(self.context_dir, "movie.context.txt")).read()
        self.context_person = open(os.path.join(self.context_dir, "person.context.txt")).read()
        self.context_thing = open(os.path.join(self.context_dir, "thing.context.txt")).read()
        self.engine_to_use=engine

    def person(self, person: str):
        response = openai.Completion.create(
            engine=self.engine_to_use,
            prompt=f"{self.context_person}\n\n Who is {person}?\n",
            temperature=0.26,
            max_tokens=155,
            top_p=0.5,
            frequency_penalty=1.04,
            presence_penalty=0.99,
            stop=["Who"]
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
                prompt=self.context_thing+prompt+"?\n",
                temperature=.51,
                max_tokens=150,
                top_p=1,
                best_of=1,
                frequency_penalty=.0,
                stop="Q:"
            )
            possible_response = response["choices"][0]["text"]

            if possible_response.__len__() >= 30:
                return possible_response

    def movie(self, movie: str):
        response = openai.Completion.create(
            engine=self.engine_to_use,
            prompt=f"{self.context_movie}{movie}?\n",
            temperature=.98,
            max_tokens=155,
            top_p=1,
            frequency_penalty=2,
            presence_penalty=0,
            stop=["Movie:"]
        )
        possible_response = response["choices"][0]["text"]
        return possible_response

if __name__ =="__main__":
    menu = [f'exit',
            f'guess',
            f'thing',
            f'person',
            f'movie',
            ]
    menu = '\n\t' + '\n\t'.join(menu)
    contestant_bot = WordHoaxBot()
    while (a := input(f"what to do? {menu}\n\n>")) != "exit":
        print(a)
        if a.lower() == "guess":
            paste = input("paste the choices here seperated by * :")
            if paste == "":
                choices = choices_default
                prompt = prompt_default
            else:
                choices = paste.split("*")
                prompt = input("what was the prompt?")

            contestant_bot.guess(prompt, choices)

        elif a.lower() == "thing":
            prompt = input("Name of the thing?\n")
            definition = contestant_bot.thing(prompt)
            print(definition)

        elif a.lower() == "person":
            prompt = input("Persons name?\n")
            definition = contestant_bot.person(prompt)
            print(definition)

        elif a.lower() == "movie":
            prompt = input("prompt?\n")
            definition = contestant_bot.movie(prompt)
            print(definition)
