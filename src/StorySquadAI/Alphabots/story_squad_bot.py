import pandas as pd
import openai
import spacy
import numpy as np
from numpy.linalg import norm
from StSqLLMWrapper.llmwrapper import LLMWrapper, LLMResponse, LLMRequest


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

    def moderate_maybe(self, data_in):
        if not self.moderate:
            return data_in
        else:
            if data_in.__class__ == LLMRequest:
                content_to_classify = data_in.prompt

                def data_setter(x):
                    setattr(data_in, "prompt", x)

            elif data_in.__class__ == LLMResponse:
                if data_in.completion:
                    content_to_classify = data_in.completion
                else:
                    content_to_classify = data_in.raw_response

                def data_setter(x):
                    setattr(data_in, "response", x)

            response = openai.Completion.create(
                engine="content-filter-alpha",
                prompt="<|endoftext|>" + content_to_classify + "\n--\nLabel:",
                temperature=0,
                max_tokens=1,
                top_p=0,
                logprobs=10
            )
            output_label = response["choices"][0]["text"]

            # This is the probability at which we evaluate that a "2" is likely real
            # vs. should be discarded as a false positive
            toxic_threshold = -0.355

            if output_label == "2":
                # If the model returns "2", return its confidence in 2 or other output-labels
                logprobs = response["choices"][0]["logprobs"]["top_logprobs"][0]

                # If the model is not sufficiently confident in "2",
                # choose the most probable of "0" or "1"
                # Guaranteed to have a confidence for 2 since this was the selected token.
                if logprobs["2"] < toxic_threshold:
                    logprob_0 = logprobs.get("0", None)
                    logprob_1 = logprobs.get("1", None)

                    # If both "0" and "1" have probabilities, set the output label
                    # to whichever is most probable
                    if logprob_0 is not None and logprob_1 is not None:
                        if logprob_0 >= logprob_1:
                            output_label = "0"
                        else:
                            output_label = "1"
                    # If only one of them is found, set output label to that one
                    elif logprob_0 is not None:
                        output_label = "0"
                    elif logprob_1 is not None:
                        output_label = "1"

                    # If neither "0" or "1" are available, stick with "2"
                    # by leaving output_label unchanged.

            # if the most probable token is none of "0", "1", or "2"
            # this should be set as unsafe
            if output_label not in ["0", "1", "2"]:
                output_label = "2"

            if output_label != "2":
                return data_in
            else:
                data_setter("non moderate response or reqeust")
                return data_in


    def filter_factual(self, prompt: LLMRequest, response: LLMResponse = None):
        """
        returns -1 if the response is likely too factual, otherwise returns 0

        """

        doc_a = prompt.prompt
        doc_b = response.completion
        # calculate similarity between prompt and response
        doc_a = self.nlp_eng_med(doc_a)
        doc_b = self.nlp_eng_med(doc_b)
        sim = doc_a.similarity(doc_b)
        print(f'sim: {sim}')

        # find the similarity between the prompt and the document for "is a"
        base_doc = self.nlp_eng_med("is")
        definition_similarity_a = base_doc.similarity(doc_a)
        definition_similarity_b = base_doc.similarity(doc_b)

        print(f'Definition similarity: {definition_similarity_a} {definition_similarity_b}')

        if sim > 0.4:
            return -1*sim
        return response

    def nlp_pre_process(self, request: LLMRequest):
        """
        apply all processing steps to requests

        """
        result = self.moderate_maybe(request)

        return result

    def nlp_post_process(self, request: LLMRequest, response: LLMResponse):
        """
        apply all processing steps to requests

        """
        result = self.moderate_maybe(request)
        result = self.filter_factual(request, response)

        return result

    # TODO: make sure to tie bot personality to choices
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
        response = self.nlp_process(
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
        # response = self.wrapped_completion()
        # return response

        return f'{prompt} :: {response}.'

    def get_response_and_score(self,checked):
        found = False
        for _ in range(3):
            response = self.llm.completion(kwargs=checked)
            score = self.nlp_post_process(checked, response)
            if score.__class__ == float:
                if score < 0:
                    yield score, response
            else:
                found = True
                break
        if found:
            yield score, response

    def thing(self, prompt: str):
        response_name = "thing"

        kwargs = LLMRequest(
            context=self.personality.responses[response_name].context_doc,
            prompt=f'C: what is {prompt}?\n',
            temperature=self.personality.responses[response_name].temperature,
            max_tokens=self.personality.responses[response_name].max_tokens,
            top_p=self.personality.responses[response_name].top_p,
            stop=["C: ", "\n\n"]
        )

        checked = self.nlp_pre_process(kwargs)
        a = [(score, result) for score, result in self.get_response_and_score(checked)]
        a.sort(key=lambda x: x[0], reverse=True)
        r_checked = a[0][1]

        return r_checked.completion

    def movie(self, movie: str):
        response_name = 'movie'
        kwargs = LLMRequest(
            context=self.personality.responses[response_name].context_doc,
            prompt=f'C: Movie: {movie}?\n',
            temperature=self.personality.responses[response_name].temperature,
            max_tokens=self.personality.responses[response_name].max_tokens,
            top_p=self.personality.responses[response_name].top_p,
            stop=["C: ", "\n\n"]
        )

        checked = self.nlp_pre_process(kwargs)
        a = [(score, result) for score, result in self.get_response_and_score(checked)]
        a.sort(key=lambda x: x[0], reverse=True)
        r_checked = a[0][1]

        return r_checked.completion

    def person(self, person: str):
        response_name = "person"
        kwargs = LLMRequest(
            context=self.personality.responses[response_name].context_doc,
            prompt=f'C: Who is/was {person}?\n',
            temperature=self.personality.responses[response_name].temperature,
            max_tokens=self.personality.responses[response_name].max_tokens,
            top_p=self.personality.responses[response_name].top_p,
            stop=["C: ", "\n\n"]
        )

        checked = self.nlp_pre_process(kwargs)
        a = [(score, result) for score, result in self.get_response_and_score(checked)]
        a.sort(key=lambda x: x[0], reverse=True)
        r_checked = a[0][1]

        return r_checked.completion