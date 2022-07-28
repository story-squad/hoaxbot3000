import os
import yaml
from yaml import Loader as loader

from StorySquadAI.Alphabots.exceptions import StorySquadAIException


class DefaultContextLoader:
    """ parent class for all context loaders"""
    supports = -1

    def __init__(self, yaml_path: str):
        self.config = yaml.load(open(yaml_path, encoding="utf-8", mode="r"), loader)
        self.personalities_dir = yaml_path.split("bot.yaml")[0]
        if "name" in self.config:
            self.name = self.config["name"]
        else:
            self.name = yaml_path.split(os.sep)[-1].split(".")[0]

        self.context = self.load_context()

    def load_context(self):
        raise NotImplementedError("load_context() must be implemented by a child class")


class TextContextLoaderV0(DefaultContextLoader):
    """
    loads context for StorySqaudAI personality from a text file
    """

    # the param ai_general.context_loader_type in bot.yaml files is used to
    # determine which context loader to use

    supports = 0

    def load_context(self):
        print(f'Loading {self.name}..')

        # results in dict of stucture like {"movie":context_doc_contents}}
        response_contexts = {
            response: open(os.path.join(self.personalities_dir, f"{response}.context.txt"),
                           encoding="utf-8").read()
            for response in self.config if response != "ai_general"}

        responses = {}
        for response_key, response_dict in self.config.items():
            if response_key != "ai_general":
                responses[response_key] = {
                    "context_doc": response_contexts[response_key],
                    "temperature": response_dict["temperature"],
                    "max_tokens": response_dict["max_tokens"],
                    "top_p": response_dict["top_p"],
                    "logit_bias": response_dict["logit_bias"]}

        return responses


class TextContextLoaderV1(DefaultContextLoader):
    """
    loads context for StorySqaudAI personality from a text file
    this version reshapes the context docs form the old format to the new format before
    returning the context
    """

    # the param ai_general.context_loader_type in bot.yaml files is used to
    # determine which context loader to use

    supports = 1

    def reshape_context_doc(self, context_doc):
        sections = context_doc.split("\n\n")
        out = []
        for section in sections:
            lines = section.splitlines()
            if len(lines) != 3:
                raise StorySquadAIException(f"Invalid context doc format: {context_doc}")
            out.append("C: " + "[CONTEXT_PROMPT_TOKEN]")
            out.append(lines[1])
        return "\n".join(out)

    def load_context(self):
        responses = TextContextLoaderV0(self.yaml_path).load_context()
        for response_key, response_dict in responses.items():
            response_dict["context_doc"] = self.reshape_context_doc(response_dict["context_doc"])

        return responses


def load_context_doc(yaml_path: str):
    """
    loads a context doc using the correct loader
    """

    config = yaml.load(open(yaml_path, encoding="utf-8", mode="r"), loader)
    if "ai_general" not in config:
        raise StorySquadAIException(f"ai_general section not found in {yaml_path}")

    if config["ai_general"] == None:
        use_type_code = 0
    elif type(config["ai_general"]) == dict:
        use_type_code = config["ai_general"]["context_loader_type"]
    else:
        raise StorySquadAIException(f"ai_general section must be a dict in {yaml_path}")

    if not is_context_loader_supported(use_type_code):
        raise StorySquadAIException(f"context_loader_type {use_type_code} not supported")

    # find the correct loader class in globals()
    list_of_loaders = [l for l in globals() if "Loader" in l]
    supported = {
        getattr(globals()[l], "supports"): globals()[l]
        for l in list_of_loaders}

    loader_class = supported[use_type_code]
    return loader_class(yaml_path).load_context()


def is_context_loader_supported(type_code_int):
    list_of_loaders = [l for l in globals() if "Loader" in l]
    supported = [
        getattr(globals()[l], "supports")
        for l in list_of_loaders]
    if type_code_int in supported:
        return True
