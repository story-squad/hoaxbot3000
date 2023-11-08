import StorySquadAI
import pytest
import shutil
from src.StorySquadAI.story_squad_ai import StorySquadAI, StorySquadAIException
import os
import spacy
import sys
import trace

# create a Trace object, telling it what to ignore, and whether to
# do tracing or line-counting or both.
tracer = trace.Trace(
    ignoredirs=[sys.prefix, sys.exec_prefix],
    trace=0,
    count=1)


this_dir = os.getenv("STORYSQUADAI_PATH")
this_data_dir = os.path.join(this_dir, "data")
hoax_api = StorySquadAI(data_dir=this_data_dir, llm_provider_str='openai')
tracer.runfunc(hoax_api.create_bot_with_personality,"bubblebot_v7")
r = tracer.results()
print(r.write_results(show_missing=True, coverdir=__file__.split(".")[0]))