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
                if data_in.prompt:
                    content_to_classify_list = [data_in.prompt]

                    def data_setter(x):
                        setattr(data_in, "prompt", x)

                elif data_in.query:
                    content_to_classify_list = data_in.documents

                    def data_setter(x):
                        setattr(data_in, "documents", x)

            elif data_in.__class__ == LLMResponse:
                if data_in.completion:
                    content_to_classify_list = [data_in.completion]
                else:
                    content_to_classify_list = [data_in.raw_response]

                def data_setter(x):
                    setattr(data_in, "response", x)
            else:
                print("Error: data_in is not a LLMRequest or LLMResponse")

            label_content_tuples = []
            for content_to_classify in content_to_classify_list:
                response = openai.Completion.create(
                    engine="content-filter-alpha",
                    prompt="<|endoftext|>" + content_to_classify + "\n--\nLabel:",
                    temperature=0,
                    max_tokens=1,
                    top_p=0,
                    logprobs=10
                )

                output_label = response["choices"][0]["text"]
                logprobs = response["choices"][0]["logprobs"]["top_logprobs"][0]
                output_label = self.moderation_score(logprobs, output_label)
                label_content_tuples.append((output_label, content_to_classify))
            if not len(label_content_tuples) > 1:
                output_label = label_content_tuples[0][0]
                if output_label != "2":
                    return data_in
                else:
                    data_setter("non moderate response or reqeust")
                    return data_in
            else:
                outlist = [tuples[1] for tuples in label_content_tuples]
                data_setter(outlist)
                return data_in

    def moderation_score(self, logprobs, output_label):
        # This is the probability at which we evaluate that a "2" is likely real
        # vs. should be discarded as a false positive
        toxic_threshold = -0.355
        if output_label == "2":
            # If the model returns "2", return its confidence in 2 or other output-labels

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
        return output_label

    def filter_factual(self, prompt: LLMRequest, response: LLMResponse = None):
        """
        filter factual responses
        :param prompt: the prompt that was used to generate the response
        :param response: the response to filter
        :return: negative score if the response is factual, otherwise a positive score
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
            return -1 * sim
        return 1

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
        """
        structured as {search pick} because {completion result}
        :param prompt:
        :param choices:
        :return:
        """

        checked = self.nlp_pre_process(LLMRequest(documents=choices, query=prompt))
        result = self.llm.search(checked)

        preferred_place = 1  # index 0 is the highest similarity
        pick = result[min(preferred_place, len(result) - 1)]

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
        request = LLMRequest(**kwargs)
        checked = self.nlp_pre_process(request)

        a = [(score, result) for score, result in self.get_response_and_score(checked)]
        a.sort(key=lambda x: x[0], reverse=True)
        r_checked = a[0][1]

        return f'{prompt} :: {r_checked.completion}.'

    def get_response_and_score(self, checked):
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
