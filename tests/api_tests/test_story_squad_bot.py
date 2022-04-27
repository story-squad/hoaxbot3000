from  src.StorySquadAI.story_squad_bot import StorySquadBot
from  src.StorySquadAI.story_squad_ai import StorySquadAI
import os

def test_guess():
    this_dir = os.getenv("STORYSQUADAI_PATH")
    this_data_dir = os.path.join(this_dir, "data")
    hoax_api = StorySquadAI(data_dir=this_data_dir)
    bubble_testbot = hoax_api.create_bot_with_personality("bubblebot_v1")
    result = bubble_testbot.guess("what is a snuffleupagus?",["dfasfasd","werewqrwe","werwr"])
    assert len(result) > 0
