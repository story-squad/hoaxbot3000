# coding=utf8
# from __future__ import annotations
from dataclasses import dataclass
import glob
import os
import openai
import yaml
from StorySquadAI.story_squad_bot import StorySquadBot

from yaml import CLoader as Loader, CDumper as Dumper

openai.api_key = os.getenv("OPENAI_API_KEY")

start_sequence = "The answer is:"
hoax = "apple"
choices_default = ["1) squishy fruit",
                   "2) square vegetable",
                   "3) purple integrated circuit"]
prompt_default = "apple"
engine_to_use = 'curie'


class StorySquadAI:
    """
    Class which manages the word hoax AI environment and provides access to AI
    """
    default_yaml = """
                      ai_general:
                      movie:
                         logit_bias: None
                         max_tokens: 80
                         temperature: 0.75
                         top_p: None
                      person:
                         logit_bias: None
                         max_tokens: 80
                         temperature: 0.75
                         top_p: None
                      thing:
                         logit_bias: None
                         max_tokens: 80
                         temperature: 0.75
                         top_p: None
                       """

    @dataclass
    class PersonalityRequestData:
        """
               The following is a list of recommended args to pass to the openai api, you can however pass any of the other
               args supported by openai as kwargs

               temperature:
                   What sampling temperature to use. Higher values means the model will take more risks. Try 0.9 for more
                   creative applications, and 0 (argmax sampling) for ones with a well-defined answer.
                       We generally recommend altering this or top_p but not both.
               max_tokens:
                   The maximum number of tokens to generate in the completion.
                   The token count of your prompt plus max_tokens cannot exceed the model's context length. Most models
                   have a context length of 2048 tokens (except davinci-codex, which supports 4096).
               top_p:
                   An alternative to sampling with temperature, called nucleus sampling, where the model considers the
                   results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10%
                   probability mass are considered.
                       We generally recommend altering this or temperature but not both.
               logit_bias:
                   Modify the likelihood of specified tokens appearing in the completion.
                   Accepts a json object that maps tokens (specified by their token ID in the GPT tokenizer) to an
                   associated bias value from -100 to 100. You can use this tokenizer tool
                   (which works for both GPT-2 and GPT-3) to convert text to token IDs. Mathematically, the bias is added
                   to the logits generated by the model prior to sampling. The exact effect will vary per model, but
                   values between -1 and 1 should decrease or increase likelihood of selection; values like -100 or 100
                   should result in a ban or exclusive selection of the relevant token.
                   As an example, you can pass {"50256": -100} to prevent the <|endoftext|> token from being generated.

               """
        temperature: float
        max_tokens: float
        top_p: float
        logit_bias: dict
        context_doc: str

    @dataclass
    class Personality:
        """
        A personality for a StorySquadAI

        responses:
            a dict of PersonalityRequestData objects
        """
        responses: dict[str, 'StorySquadAI.PersonalityRequestData']

    def init_error(self, e):
        raise Exception(e)

    def __init__(self, data_dir=f"./data", **kwargs):
        self.data_dir = os.path.realpath(data_dir)
        self.personalities_dir = os.path.realpath(os.path.join(data_dir, "personalities"))

        self.data_dir_glob_str = os.path.join(self.data_dir, "*")
        self.data_dir_glob = glob.glob(self.data_dir_glob_str)

        self.personalities_dir_str = os.path.join(self.personalities_dir, "*")
        self.personalities_dir_glob = glob.glob(self.personalities_dir_str)

        self.data_dir_glob = glob.glob(self.data_dir_glob_str)
        self.personalities = self.list_personalities()

        True if self.personalities_dir in self.data_dir_glob else self.init_error(
            f"invalid data dir {self.personalities_dir} does not exist inside ({os.path.realpath(self.data_dir)})")

    def list_personalities(self):
        self.check_personalities()
        return [os.path.basename(personality) for personality in self.personalities_dir_glob]

    def check_personalities(self):
        for personality in self.personalities_dir_glob:
            personality = os.path.basename(personality)
            personality_glob = glob.glob(os.path.join(self.personalities_dir, personality, "*"))
            personality_glob = {os.path.basename(p): p for p in personality_glob}
            if 'bot.yaml' in personality_glob:
                yaml_contents = yaml.load(open(personality_glob["bot.yaml"], "r"), Loader)
                for item in yaml_contents:
                    if item != "ai_general":
                        if item + '.context.txt' not in personality_glob:
                            raise Exception(f"Error in ai structure -> missing {item}.context.txt for {personality}")
                pass
                if len(personality_glob) > len(yaml_contents):
                    raise Exception(f"Extra files in {personality} personality directory")

            else:
                raise Exception(f"Directory without bot.yaml: {personality}")

    def create_bot_with_personality(self, personality, personality_data=None) -> StorySquadBot:
        if type(personality) is str:
            # if the personality exists
            if personality in self.personalities:
                ctx_dir = os.path.join(self.personalities_dir, personality)
                personality = self.load_personality_from_data_dir(personality, create_new=True)
                return StorySquadBot(data_dir=ctx_dir, personality=personality, name=personality)

        if personality_data:
            ctx_dir = os.path.join(self.personalities_dir, personality)
            return StorySquadAI.StorySquadBot(data_dir=ctx_dir, personality=personality_data, name=personality)

    def load_or_create_bot_yaml(self, personality):
        try:
            # details = .read()
            yaml_file_path = os.path.join(self.personalities_dir, personality, "bot.yaml")
            details = yaml.load(open(yaml_file_path, encoding="utf-8", mode="r"), Loader)
        except FileNotFoundError as e:
            new_yaml = yaml.load(self.default_yaml, Loader)
            yaml.dump(new_yaml, open(e.filename, "w"))
            details = yaml.load(self.default_yaml, Loader)
        return details

    def load_personality_from_data_dir(self, personality: str, create_new=False) -> 'StorySquadAI.Personality':
        print(f'Loading {personality}..')
        bot_config_yaml = self.load_or_create_bot_yaml(personality)

        # results in dict of stucture like {"movie":context_doc_contents}}
        response_contexts = {
            response: open(os.path.join(self.personalities_dir, personality, f"{response}.context.txt"),
                           encoding="utf-8").read()
            for response in bot_config_yaml if response != "ai_general"}

        responses = {}
        for response_key, response_dict in bot_config_yaml.items():
            if response_key != "ai_general":
                responses[response_key] = StorySquadAI.PersonalityRequestData(
                    context_doc=response_contexts[response_key],
                    temperature=response_dict["temperature"],
                    max_tokens=response_dict["max_tokens"],
                    top_p=response_dict["top_p"],
                    logit_bias=response_dict["logit_bias"])

            if response_key == 'ai_general':
                pass

        return StorySquadAI.Personality(responses)

    def save_bot(self, bot: StorySquadBot, overwrite: bool = False):
        # create directory
        os.mkdir(os.path.join(self.data_dir, "personalities", bot.name))

        # create bot.yaml
        yaml_file_name = os.path.join(self.data_dir, "personalities", bot.name, "bot.yaml")
        print(yaml_file_name)
        for k, v in bot.personality.responses.items():
            yaml_params = yaml.load(StorySquadAI.default_yaml, Loader)
            yaml_params[k]["logit_bias"] = v.logit_bias
            yaml_params[k]["max_tokens"] = v.max_tokens
            yaml_params[k]["temperature"] = v.temperature
            yaml_params[k]["top_p"] = v.top_p
        yaml.dump(yaml_params, open(yaml_file_name, "w"))

        # create context docs
        for k, v in bot.personality.responses.items():
            context_file_name = os.path.join(self.data_dir, "personalities", bot.name, f"{k}.context.txt")
            print(context_file_name)
            with open(context_file_name, "w") as f:
                f.write(v.context_doc)


if __name__ == "__main__":
    HoaxAI = StorySquadAI()
    print(HoaxAI.list_personalities())

    bubble_testbot = HoaxAI.create_bot_with_personality("bubblebot_v1")
    buzzkill_testbot = HoaxAI.create_bot_with_personality("buzzkillbot_v1")
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
