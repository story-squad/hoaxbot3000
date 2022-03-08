from turtle import pd

import openai


class StorySquadBot:
    def __init__(self, personality: 'StorySquadAI.Personality', data_dir: str = "data",
                 engine='curie', name: str = None, **kwargs):
        self.personality = personality

        if name:
            self.name = name
        elif type(personality) is str:
            self.name = personality
        else:
            raise ValueError("No name given for this bot!")

        self.context_dir = data_dir
        self.engine_to_use = engine

    def person(self, person: str):
        response_name = "person"
        kwargs = {
            "engine": self.engine_to_use,
            "prompt": f'{self.personality.responses[response_name].context_doc}C: Who is/was {person}?\n',
            "temperature": self.personality.responses[response_name].temperature,
            "max_tokens": self.personality.responses[response_name].max_tokens,
            "top_p": self.personality.responses[response_name].top_p,
            "stop": ["C: ", "\n\n"]
        }
        kwargs = {k: v for k, v in kwargs.items() if v != 'None'}
        response = openai.Completion.create(**kwargs)
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
            max_tokens=40,
            top_p=.7,
            best_of=1,
            frequency_penalty=.2,
            presence_penalty=0,
            stop="."
        )
        return f'{prompt} :: {response["choices"][0]["text"]}.'

    def thing(self, prompt: str):
        response_name = "thing"
        kwargs = {
            "engine": self.engine_to_use,
            "prompt": f'{self.personality.responses[response_name].context_doc}C: what is {prompt}?\n',
            "temperature": self.personality.responses[response_name].temperature,
            "max_tokens": self.personality.responses[response_name].max_tokens,
            "top_p": self.personality.responses[response_name].top_p,
            "stop": ["C: ", "\n\n"]
        }
        kwargs = {k: v for k, v in kwargs.items() if v != 'None'}
        response = openai.Completion.create(**kwargs)
        response = response["choices"][0]["text"]
        return response

    def movie(self, movie: str):
        response_name = 'movie'
        kwargs = {
            "engine": self.engine_to_use,
            "prompt": f'{self.personality.responses[response_name].context_doc}C: Movie:{movie}?\n',
            "temperature": self.personality.responses[response_name].temperature,
            "max_tokens": self.personality.responses[response_name].max_tokens,
            "top_p": self.personality.responses[response_name].top_p,
            "stop": ["C: ", "\n\n"]
        }
        kwargs = {k: v for k, v in kwargs.items() if v != 'None'}
        response = openai.Completion.create(**kwargs)
        possible_response = response["choices"][0]["text"]
        return possible_response