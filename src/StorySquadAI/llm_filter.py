from StSqLLMWrapper.llmwrapper import LLMWrapper, LLMResponse, LLMRequest, LLMFilter
import openai


class ModerateFilter(LLMFilter):
    def apply(self, request: LLMRequest, response: LLMResponse):
        return min(
            moderate_maybe(request),
            moderate_maybe(response)
        )


def moderate_maybe(data_in):
    """given an LLMRequest or LLMResponse, moderate the response and return -1 if it has been moderated"""

    if data_in.__class__ == LLMRequest:
        if data_in.prompt:
            content_to_classify_list = [data_in.prompt]

            def data_setter(x):
                setattr(data_in, "prompt", x)

        elif data_in.query:
            content_to_classify_list = data_in.documents

            def data_setter(x):
                setattr(data_in, "documents", x)
    elif data_in is None:
        return 0

    elif data_in.__class__ == LLMResponse:
        if data_in.completion is not None:
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
        output_label = moderation_score(logprobs, output_label)
        label_content_tuples.append((output_label, content_to_classify))

    if not len(label_content_tuples) > 1:
        output_label = label_content_tuples[0][0]
        if output_label != "2":
            return 0
        else:
            data_setter("non moderate response or reqeust")
            return -1
    else:
        # TODO: finish this so requests that have documents can be moderated or is done?

        outlist = []
        danger=0
        for score, content in label_content_tuples:
            if score == "2":
                outlist.append("-= non moderate =-")
                danger = danger-1
            else:
                outlist.append(content)
        data_setter(outlist)
        return danger


class MinimumLengthFilter(LLMFilter):
    def apply(self, request: LLMRequest, response: LLMResponse):
        return filter_response_for_minimum_length(response)


class FactualFilter(LLMFilter):

    def __init__(self, name: str = "unnamed filter",similarity_provider="spacy"):
        super().__init__(name)
        self.similarity_provider = similarity_provider

        if self.similarity_provider == "spacy":
            import spacy
            self.similarity_provider_spacey = spacy.load("en_core_web_md")
            self.similarity_provider_func = lambda x,y: \
                self.similarity_provider_spacey(x).similarity(self.similarity_provider_spacey(y))

    def apply(self, request: LLMRequest, response: LLMResponse):

        return filter_factual(self.similarity_provider_func,request, response)


def moderation_score(logprobs, output_label):
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


def filter_factual(sim_func,prompt: LLMRequest, response: LLMResponse = None):
    """
    filter factual responses
    :param prompt: the prompt that was used to generate the response
    :param response: the response to filter
    :return: negative score if the response is factual, otherwise a positive score
    """

    #doc_a = prompt.prompt
    #doc_b = response.completion
    # calculate similarity between prompt and response
    #doc_a_vec = self.nlp_eng_med(doc_a)
    #doc_b_vec = self.nlp_eng_med(doc_b)
    sim = sim_func(prompt.prompt, response.completion)
    if 'prompt' in prompt.__dict__:
        if prompt.prompt is not None:
            if response.completion is not None:
                print(f'sim: {sim} for {prompt.prompt} and {response.completion}')

    # find the similarity between the prompt and the document for "is a"
    #base_doc = self.nlp_eng_med("is")
    #definition_similarity_a = base_doc.similarity(doc_a_vec)
    #definition_similarity_b = base_doc.similarity(doc_b_vec)

    #print(f'Definition similarity: {definition_similarity_a} {definition_similarity_b}')

    if sim > 0.4:
        return -1 * sim
    return 1


def filter_response_for_minimum_length(response: LLMResponse):
    """
    filter responses that are too short
    :param response: the response to filter
    :return: negative score if the response is too short, otherwise a positive score
    """
    if len(response.completion) < 20:
        return -1
    return 1
