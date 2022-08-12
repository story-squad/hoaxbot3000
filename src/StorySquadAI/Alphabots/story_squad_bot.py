import numbers

import pandas as pd
import openai
import spacy
import numpy as np
from numpy.linalg import norm
from StSqLLMWrapper.llmwrapper import LLMWrapper, LLMResponse, LLMRequest
from StorySquadAI import filters
from StorySquadAI.Alphabots.bot_context_processors import get_processor

# TODO: make StorySquadBot as a composable class, composed of the bots context, filters, and individual endpoints
class StorySquadBot:
    def __init__(self, personality, llmwrapper_for_bot: LLMWrapper, data_dir: str = "data",
                 engine='curie', moderate: bool = True):
        self.llm = llmwrapper_for_bot
        self.moderate = moderate
        self.name = personality.name
        self.personality = personality
        self.context_dir = data_dir
        self.engine_to_use = engine
        self.nlp_eng_med = spacy.load("en_core_web_md")
        self.assign_context_providers()

    def assign_context_providers(self):
        """
        process the context docs for the bot
        :return:
        """
        # process personality context docs
        # self.personality.context_docs = {}
        for name, doc in self.personality.responses.items():
            f = get_processor(self.personality.context_doc_format_ver)(doc.context_doc).processor
            self.personality.responses[name].context_doc = f

    # TODO: make sure to tie bot personality params to choices
    def guess(self, prompt: str, choices: list,correct_defenition: str=None):
        """
        structured as {search pick} because {text result}
        :param prompt:
        :param choices:
        :return:
        """

        proc_list_search = [
            filters.ModerateProcessor(name='moderate')
        ]

        proc_list_completion = [
            filters.MinimumLengthProcessor(name="length"),
            filters.ModerateProcessor(name='moderate'),
        ]

        search_req = LLMRequest(documents=choices, query=prompt)
        search_results = [(score, result) for score, result
                          in self.get_response_and_score(processor_list=proc_list_search,
                                                         request=search_req,
                                                         req_modification_callback=self.increase_top_p_callback)]

        search_results.sort(key=lambda x: x[0], reverse=True)
        search_chosen_response = search_results[0][1]

        preferred_place = 1  # index 0 is the highest similarity
        pick = search_chosen_response.text[min(preferred_place, len(search_chosen_response.text) - 1)]

        context = ".".join(choices)
        prompt = f"I'm going to go with {pick} because"

        kwargs = {
            "prompt": prompt,
            "context": context,
            "temperature": 1,
            "max_tokens": 40,
            "top_p": .7,
            "best_of": 1,
            "frequency_penalty": .2,
            "presence_penalty": 0,
            "stop": "."
        }
        completion_request = LLMRequest(**kwargs)

        #completion_request = LLMRequest(documents=choices, query=prompt)
        completion_results = [(score, result) for score, result
                              in self.get_response_and_score(processor_list=proc_list_completion,
                                                             request=completion_request,
                                                             req_modification_callback=self.increase_top_p_callback)]


        completion_results.sort(key=lambda x: x[0], reverse=True)
        search_chosen_response = completion_results[0][1]

        return f'{prompt} {search_chosen_response.text[0]}.'

    def get_response_and_score(self, request, processor_list, req_modification_callback=None):
        """
         an iterator that will get a response and score it
        :param request: the request to get the response for
        :param req_modification_callback: a callback to modify the request before scoring
        :return: a list of tuples of (score, response)
        """
        found = False
        for _ in range(10):
            if len(request.prompt) != 0:
                response = self.llm.completion(req=request)
            elif len(request.query) != 0:
                response = self.llm.search(request)
            # list of tuples of (name_of_filter, score)

            score_sources = [
                i(request, response) for i in processor_list
                if i.will_handle(request, response)
            ]
            score_sources += [i(request) for i in processor_list if i.will_handle(request)]
            score_sources += [i(response) for i in processor_list if i.will_handle(response)]

            score_sources.sort()
            score_val = score_sources[0]

            if score_val.__class__ == int or score_val.__class__ == float:
                if score_val < 0:
                    if req_modification_callback is not None:
                        req_modification_callback(score_val, request)
                    yield score_val, response
                else:
                    found = True
                    break
        if found:
            yield score_val, response

    def increase_temperature_callback(self, score, request):
        request.top_p = None
        request.temperature += 0.1
        request.temperature = min(request.temperature, 1.0)
        print(f'Temperature increased to {request.temperature}')

    def increase_top_p_callback(self, score, request):
        # request.temperature = None
        if request.top_p is None:
            request.top_p = 0.9
        else:
            request.top_p += 0.1
        request.top_p = min(1, request.top_p)
        print(f'top_p increased to {request.top_p}')


    def thing(self, prompt: str,correct_definition: str=None):
        response_name = "thing"

        proc_list = [
            filters.FactualProcessor(name='factual', correct_definition=correct_definition),
            filters.MinimumLengthProcessor(name="length"),
            filters.ModerateProcessor(name='moderate'),
        ]

        req = LLMRequest(
            context=self.personality.responses[response_name].context_doc(prompt),
            prompt=f'C: what is {prompt}?\n',
            temperature=self.personality.responses[response_name].temperature,
            max_tokens=self.personality.responses[response_name].max_tokens,
            top_p=self.personality.responses[response_name].top_p,
            stop=["C:"]
        )

        a = [(score, result) for score, result
             in self.get_response_and_score(processor_list=proc_list,
                                            request=req,
                                            req_modification_callback=self.increase_top_p_callback)]
        a.sort(key=lambda x: x[0], reverse=True)
        r_checked = a[0][1]

        return r_checked.text

    def movie(self, movie: str,correct_definition: str=None):
        response_name = 'movie'

        proc_list = [
            filters.FactualProcessor(name='factual',correct_definition=correct_definition),
            filters.MinimumLengthProcessor(name="length"),
            filters.ModerateProcessor(name='moderate'),
        ]

        req = LLMRequest(
            context=self.personality.responses[response_name].context_doc(movie),
            prompt=f'C: Movie: {movie}?\n',
            temperature=self.personality.responses[response_name].temperature,
            max_tokens=self.personality.responses[response_name].max_tokens,
            top_p=self.personality.responses[response_name].top_p,
            stop=["C:"]
        )

        a = [(score, result) for score, result
             in self.get_response_and_score(processor_list=proc_list,
                                            request=req,
                                            req_modification_callback=self.increase_top_p_callback)]
        a.sort(key=lambda x: x[0], reverse=True)
        r_checked = a[0][1]

        return r_checked.text

    def person(self, person: str,correct_definition: str=None):
        response_name = "person"

        proc_list = [
            filters.FactualProcessor(name='factual',correct_definition=correct_definition),
            filters.MinimumLengthProcessor(name="length"),
            filters.ModerateProcessor(name='moderate'),
        ]

        req = LLMRequest(
            context=self.personality.responses[response_name].context_doc(person),
            prompt=f'C: Who is/was {person}?\n',
            temperature=self.personality.responses[response_name].temperature,
            max_tokens=self.personality.responses[response_name].max_tokens,
            top_p=self.personality.responses[response_name].top_p,
            stop=["C:"]
        )

        a = [(score, result) for score, result
             in self.get_response_and_score(processor_list=proc_list,
                                            request=req,
                                            req_modification_callback=self.increase_top_p_callback)]
        a.sort(key=lambda x: x[0], reverse=True)
        r_checked = a[0][1]

        return r_checked.text
