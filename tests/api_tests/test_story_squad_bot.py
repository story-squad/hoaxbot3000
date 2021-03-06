import pytest
import shutil
from src.StorySquadAI.Alphabots.story_squad_ai import StorySquadAI
import os


def test_guess():
    this_dir = os.getenv("STORYSQUADAI_PATH")
    this_data_dir = os.path.join(this_dir, "Alphabots", "data")
    hoax_api = StorySquadAI(data_dir=this_data_dir)
    bubble_testbot = hoax_api.create_bot_with_personality("bubblebot_v1")
    result = bubble_testbot.guess("what is a snuffleupagus?", ["dfasfasd", "werewqrwe", "werwr"])
    assert len(result) > 0


def test_person():
    this_dir = os.getenv("STORYSQUADAI_PATH")
    this_data_dir = os.path.join(this_dir, "Alphabots", "data")
    hoax_api = StorySquadAI(data_dir=this_data_dir)
    bubble_testbot = hoax_api.create_bot_with_personality("bubblebot_v1")
    result = bubble_testbot.person("Bob")
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
                                     "Alphabots",
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
                                     "Alphabots",
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
                                     "Alphabots",
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
    this_data_dir = os.path.join(this_dir, "Alphabots", "data")
    hoax_api = StorySquadAI(data_dir=this_data_dir)
    bubble_testbot = hoax_api.create_bot_with_personality("bubblebot_v1")
    bubble_testbot.name = "test_save_bot"
    hoax_api.save_bot(bubble_testbot)
    # create a new instance of StorySquadAI to test loading the bot
    hoax_api = StorySquadAI(data_dir=this_data_dir)
    bubble_testbot = hoax_api.create_bot_with_personality("test_save_bot")
    # delete the bot from the directory using shutil.rmtree
    shutil.rmtree(os.path.join(this_data_dir, "personalities","test_save_bot"))


