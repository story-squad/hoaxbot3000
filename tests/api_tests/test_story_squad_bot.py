import pytest
import shutil
from src.StorySquadAI.story_squad_ai import StorySquadAI, StorySquadAIException
import os
import spacy
from StSqLLMWrapper.llmwrapper import LLMWrapper, LLMResponse

nlp = spacy.load("en_core_web_md")

def test_bot_fact_recall_filter():
    """
    test that the bot does not re iterate the known definition
    """
    this_dir = os.getenv("STORYSQUADAI_PATH")
    this_data_dir = os.path.join(this_dir, "data")
    hoax_api = StorySquadAI(data_dir=this_data_dir, llm_provider_str='openai')
    bubble_testbot = hoax_api.create_bot_with_personality("bubblebot_v7")

    result = bubble_testbot.thing("apple")

    p_nlp = nlp("apple")
    r_nlp = nlp(result[0])
    similarity = p_nlp.similarity(r_nlp)
    print(result)
    assert similarity < 0.4

def test_short_length_filter():
    # TODO: create test LLM in LLMWrapper
    this_dir = os.getenv("STORYSQUADAI_PATH")
    this_data_dir = os.path.join(this_dir, "data")

    def test_response_creator(prompt, req):
        # yield responses that are too short 9 times and then yield a long response
        for i in range(9):
            yield LLMResponse(text=[f"short {i}"])
        yield LLMResponse(text=["This is a sentence that is long enough to pass."])

    test_llm_wrapper = LLMWrapper('test',
                                  completion_test_generator=test_response_creator(None, None),
                                  )
    api = StorySquadAI(data_dir=this_data_dir, llm_provider_str="test", llmwrapper=test_llm_wrapper)
    bubble_testbot = api.create_bot_with_personality("bubblebot_v1")
    result = bubble_testbot.thing("apple")
    result = result[0]
    assert len(result) > 10


def test_thing():
    this_dir = os.getenv("STORYSQUADAI_PATH")
    this_data_dir = os.path.join(this_dir, "data")
    hoax_api = StorySquadAI(data_dir=this_data_dir, llm_provider_str='openai')
    bubble_testbot = hoax_api.create_bot_with_personality("bubblebot_v1")
    result = bubble_testbot.thing("apple")
    assert len(result) > 0


def test_unsupported_bot_context_type_should_fail():
    old = os.environ["STORYSQUADAI_PATH"]
    this_test_file_path, _ = os.path.split(__file__)
    test_fixture_path = os.path.join(this_test_file_path,
                                     "test_fixtures",
                                     "unsupported_bot_context_type_should_fail",
                                     "data"
                                     )
    # assert that the path is valid
    assert os.path.exists(test_fixture_path)

    # set the environment variable to the test fixture path
    os.environ["STORYSQUADAI_PATH"] = test_fixture_path

    # create a new StorySquadAI instance with the test fixture path

    with pytest.raises(StorySquadAIException) as e_info:
        try:
            StorySquadAI(data_dir=test_fixture_path, llm_provider_str='openai')
        except Exception as e:
            if "unsupported context type" in str(e):
                raise Exception(e)
            else:
                raise e

    # reset the environment variable to the old value
    os.environ["STORYSQUADAI_PATH"] = old


def test_llm_wrapper_install():
    llmw = LLMWrapper('openai')
    response = llmw.completion('what is a snuffleupagus?')
    assert type(response) is LLMResponse
    assert type(response.text[0]) is str

def test_movie():
    this_dir = os.getenv("STORYSQUADAI_PATH")
    this_data_dir = os.path.join(this_dir, "data")
    hoax_api = StorySquadAI(data_dir=this_data_dir, llm_provider_str='openai')
    bubble_testbot = hoax_api.create_bot_with_personality("bubblebot_v1")
    result = bubble_testbot.movie("The Matrix")
    assert len(result) > 0


def test_person():
    this_dir = os.getenv("STORYSQUADAI_PATH")
    this_data_dir = os.path.join(this_dir, "data")
    hoax_api = StorySquadAI(data_dir=this_data_dir, llm_provider_str='openai')
    bubble_testbot = hoax_api.create_bot_with_personality("bubblebot_v1")
    result = bubble_testbot.person("Bob")
    assert len(result) > 0


def test_guess():
    this_dir = os.getenv("STORYSQUADAI_PATH")
    this_data_dir = os.path.join(this_dir, "data")
    hoax_api = StorySquadAI(data_dir=this_data_dir, llm_provider_str='openai')
    bubble_testbot = hoax_api.create_bot_with_personality("bubblebot_v1")
    result = bubble_testbot.guess("what is an apple?", ["a juicy red or green fruit",
                                                        "a type of werewolf",
                                                        "something in the center of my eye",
                                                        "a type of animal"])
    assert len(result) > 0


def test_invalid_STORYSQUADAI_PATH():
    old = os.environ["STORYSQUADAI_PATH"]
    os.environ["STORYSQUADAI_PATH"] = os.path.join("invalid_dir")
    dir = os.getenv("STORYSQUADAI_PATH")
    pytest.raises(Exception, test_guess)
    os.environ["STORYSQUADAI_PATH"] = old


def test_missing_context_txt():
    old = os.environ["STORYSQUADAI_PATH"]
    this_test_file_path, _ = os.path.split(__file__)
    test_fixture_path = os.path.join(this_test_file_path,
                                     "test_fixtures",
                                     "missing_context_txt",
                                     "data"
                                     )
    # assert that the path is valid
    assert os.path.exists(test_fixture_path)

    # set the environment variable to the test fixture path
    os.environ["STORYSQUADAI_PATH"] = test_fixture_path

    # create a new StorySquadAI instance with the test fixture path

    with pytest.raises(Exception) as e_info:
        StorySquadAI(data_dir=test_fixture_path)
    # reset the environment variable to the old value
    os.environ["STORYSQUADAI_PATH"] = old


def test_extra_file_in_personality_dir():
    old = os.environ["STORYSQUADAI_PATH"]
    this_test_file_path, _ = os.path.split(__file__)
    test_fixture_path = os.path.join(this_test_file_path,
                                     "test_fixtures",
                                     "extra_file_in_personality_dir",
                                     "data"
                                     )
    # assert that the path is valid
    assert os.path.exists(test_fixture_path)

    # set the environment variable to the test fixture path
    os.environ["STORYSQUADAI_PATH"] = test_fixture_path

    # create a new StorySquadAI instance with the test fixture path

    with pytest.raises(Exception) as e_info:
        StorySquadAI(data_dir=test_fixture_path)
    # reset the environment variable to the old value
    os.environ["STORYSQUADAI_PATH"] = old


def test_missing_bot_yaml():
    old = os.environ["STORYSQUADAI_PATH"]
    this_test_file_path, _ = os.path.split(__file__)
    test_fixture_path = os.path.join(this_test_file_path,
                                     "test_fixtures",
                                     "missing_bot_yaml",
                                     "data"
                                     )
    # assert that the path is valid
    assert os.path.exists(test_fixture_path)

    # set the environment variable to the test fixture path
    os.environ["STORYSQUADAI_PATH"] = test_fixture_path

    # create a new StorySquadAI instance with the test fixture path

    with pytest.raises(Exception) as e_info:
        StorySquadAI(data_dir=test_fixture_path)
    # reset the environment variable to the old value
    os.environ["STORYSQUADAI_PATH"] = old


# test StorySquadAI.save_bot()
def test_save_bot():
    this_dir = os.getenv("STORYSQUADAI_PATH")
    this_data_dir = os.path.join(this_dir, "data")
    hoax_api = StorySquadAI(data_dir=this_data_dir, llm_provider_str='openai')
    bubble_testbot = hoax_api.create_bot_with_personality("bubblebot_v1")
    bubble_testbot.name = "test_save_bot"
    hoax_api.save_bot(bubble_testbot)
    # create a new instance of StorySquadAI to test loading the bot
    hoax_api = StorySquadAI(data_dir=this_data_dir, llm_provider_str='openai')
    bubble_testbot = hoax_api.create_bot_with_personality("test_save_bot")
    # delete the bot from the directory using shutil.rmtree
    shutil.rmtree(os.path.join(this_data_dir, "personalities", "test_save_bot"))
