from StSqLLMWrapper.llmwrapper import LLMWrapper, LLMResponse, LLMRequest, \
    LLMReqResProcessor, LLMResProcessor, LLMReqResProcessor
import openai


class ModerateProcessor(LLMReqResProcessor):
    """provides _processed_data of the form {'moderation_processor':[(score,text), ...]}"""

    def get_moderation(self, content_to_classify: str):
        moderation = openai.Completion.create(
            engine="content-filter-alpha",
            prompt="<|endoftext|>" + content_to_classify + "\n--\nLabel:",
            temperature=0,
            max_tokens=1,
            top_p=0,
            logprobs=10
        )
        logprobs = moderation["choices"][0]["logprobs"]["top_logprobs"][0]
        output_label = moderation["choices"][0]["text"]
        r = moderation_score(logprobs, output_label)
        return r

    def apply(self, modify_list: [[]], report_list: [[]]):
        """
        :param modify_list: list of lists of strings to be modified
        :param report_list: list of lists of strings to be reported
        :return:
        """
        for i in range(len(modify_list)):
            report_list[i][0] = (self.get_moderation(modify_list[i][0]), modify_list[i][0])
        return min([i[0] for i in report_list])

class MinimumLengthProcessor(LLMReqResProcessor):
    def apply(self, modify_list: [[]], report_list: [[]]):
        """
        :param modify_list: list of lists of strings to be modified
        :param report_list: where to store the results
        :return: None
        """
        for i in range(len(modify_list)):
            if len(modify_list[i][0]) < 10:
                report_list[i][0] = (0, modify_list[i][0])
            else:
                report_list[i][0] = (-1, modify_list[i][0])

        return min([i[0][0] for i in report_list])

class FactualProcessor(LLMReqResProcessor):
    """provides text_processed_data of the form {factual_processor: [(score, text_a,text_b), ...]} and
     sorts it by score"""
    ## todo: change the output to be a dict of dicts ie. "factual_processor": {"apple":{"banna":0.5}, ...}
    ## will enable acess as request.<whatever>.<whatever>["<name given to this>"]["apple"]["banna"] for similarity

    def __init__(self, name: str = "unnamed filter", similarity_provider="spacy"):
        super().__init__(name)
        self.similarity_provider = similarity_provider

        if self.similarity_provider == "spacy":
            import spacy
            self.similarity_provider_spacey = spacy.load("en_core_web_md")
            self.similarity_provider_func = lambda x, y: \
                self.similarity_provider_spacey(x).similarity(self.similarity_provider_spacey(y))

    def processor_func(self, data_to_modify: list[list], report_to_list: list[list]):
        pass

    def apply(self, modify_list: [[]], report_list: [[]]):
        """
        :param modify_list: list of lists of strings to be modified
        :param report_list: where to store the results
        :return: None
        """

        for i in range(len(modify_list)):
            report_list[i][0] = (filter_factual(self.similarity_provider_func,
                                                modify_list[0][0],
                                                modify_list[i][0]),
                                 modify_list[0][0],
                                 modify_list[i][0])

        return min([i[0][0] for i in report_list])

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


def filter_factual(sim_func, prompt: str, response: str):
    sim = sim_func(prompt, response)
    print(f'sim: {sim} for {prompt} and {response}')

    if sim > 0.4:
        return -1 * sim
    return 1
