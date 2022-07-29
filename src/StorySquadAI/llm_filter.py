from StSqLLMWrapper.llmwrapper import LLMWrapper, LLMResponse, LLMRequest, LLMProcessor
import openai


class ModerateProcessor(LLMProcessor):
    """provides _processed_data of the form {'moderation_processor':[(score,text), ...]}"""
    def __init__(self, name: str):
        self.name = name

    def get_moderation(content_to_classify:str):
        r = openai.Completion.create(
            engine="content-filter-alpha",
            prompt="<|endoftext|>" + content_to_classify + "\n--\nLabel:",
            temperature=0,
            max_tokens=1,
            top_p=0,
            logprobs=10
        )
        return r

    def __call__(self, request: LLMRequest, response: LLMResponse):
        """ gets moderation data on each document and response"""
        for doc in request.documents:
            moderation = self.get_moderation(doc)
            logprobs = moderation["choices"][0]["logprobs"]["top_logprobs"][0]
            output_label = moderation["choices"][0]["text"]
            request.documents_processed_data.append((moderation_score(moderation, logprobs, output_label),doc))


        for doc in response.completion:
            moderation = self.get_moderation(doc)
            logprobs = moderation["choices"][0]["logprobs"]["top_logprobs"][0]
            output_label = moderation["choices"][0]["text"]
            response.completion_processed_data.append((moderation_score(moderation, logprobs, output_label),doc))




class ModerateProcessorOld(LLMProcessor):
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
                setattr(data_in, "prompt", x[0])

        elif data_in.query:
            content_to_classify_list = data_in.documents

            def data_setter(x):
                setattr(data_in, "documents", x)
    elif data_in is None:
        return 0

    elif data_in.__class__ == LLMResponse:
        if data_in.completion is not None:
            content_to_classify_list = [i.text for i in data_in.completion]
        else:
            content_to_classify_list = [data_in.raw_response]

        def data_setter(x):
            setattr(data_in, "completion", x)
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

    if False: # not len(label_content_tuples) > 1:
        output_label = label_content_tuples[0][0]
        if output_label != "2":
            return 0
        else:
            data_setter("non moderate response or reqeust")
            return -1
    else:

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


class MinimumLengthProcessor(LLMProcessor):
    def apply(self, request: LLMRequest, response: LLMResponse):
        return filter_response_for_minimum_length(response)


class FactualProcessor(LLMProcessor):
    """provides completion_processed_data of the form {factual_processor: [(score, completion), ...]} and
     sorts it by score"""

    def __init__(self, name: str = "unnamed filter",similarity_provider="spacy"):
        super().__init__(name)
        self.similarity_provider = similarity_provider

        if self.similarity_provider == "spacy":
            import spacy
            self.similarity_provider_spacey = spacy.load("en_core_web_md")
            self.similarity_provider_func = lambda x,y: \
                self.similarity_provider_spacey(x).similarity(self.similarity_provider_spacey(y))

    def apply(self, request: LLMRequest, response: LLMResponse):
        response.completion_processed_data["factual_processor"] = [(filter_factual(self.similarity_provider_func,
                                                                                  request.prompt,
                                                                                  c),c) for c in response.completion]
        response.completion_processed_data["factual_processor"] = sorted(response.completion_processed_data["factual_processor"], key=lambda x: x[0], reverse=True)

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


def filter_factual(sim_func, prompt: str, response: str ):

    sim = sim_func(prompt, response)
    print(f'sim: {sim} for {prompt.prompt} and {response.completion}')

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
