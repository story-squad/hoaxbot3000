import pandas as pd

from src.StorySquadAI.story_squad_ai import StorySquadAI
import matplotlib.pyplot as plt


def print_basic_offline_diagnoses(bot: str, verbose=0):
    _hoax_ai = StorySquadAI(data_dir="../../Alphabots/data//")
    _bot = _hoax_ai.create_bot_with_personality(bot)

    ## context doc diagnostics

    for response_type, data in _bot.personality.responses.items():
        print(f'\t{response_type}')

        # print(f'\t{}')
        lines = [line for line in data.context_doc.splitlines() if line.__len__() > 1]
        prompts = [line for line in lines if line[0:2] == "C:"]
        responses = [line for line in lines if line[0:2] != "C:"]
        if verbose >=1:
            print("\t\tlines")
            print_stats_about_list_of_strings(lines,f"context_doc {bot}-{response_type}-lines")
            print("\t\tprompts")
            print_stats_about_list_of_strings(prompts,f"context_doc {bot}-{response_type}-prompts")

        print("\t\tresponses")
        print_stats_about_list_of_strings(responses,f"context_doc {bot}-{response_type}-responses")

        if verbose == 2:
            for line in lines:
                print(f'\t\t{line}')

            for prompt in prompts:
                print(f'\t\t{prompt}')

            for response in responses:
                print(f'\t\t{response}')

def print_stats_about_list_of_strings(list_of_strings:[str],title:str):
    df = pd.DataFrame()
    df["text"]= list_of_strings
    ##df["test"].str.
    df["chrs"] = df.apply(lambda x: x.str.len())
    df["words"] = df['text'].str.count(' ').add(1)

    #print(df.head())
    #ser = pd.Series(list_of_strings)

    length_of_list = len(list_of_strings)
    mean_chr_count = df["chrs"].mean()
    mean_word_count = df["words"].mean()

    print(f'\t\t\tEntries: {length_of_list}')
    print(f'\t\t\tmean chr length: {mean_chr_count}')
    print(f'\t\t\tmean word count: {mean_word_count}')
    print(f'\t\t\tchrs/word : {mean_chr_count/mean_word_count}')
    df["words"].plot(kind="hist",bins=5,title =title)
    plt.xlabel("word count")


    plt.show()


for bot_name in ["buzzkillbot_v2","bubblebot_v5"]:
    print(bot_name)
    print_basic_offline_diagnoses(bot_name)
