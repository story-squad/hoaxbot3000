# HoaxBot3000

HoaxBot3000 is an advanced AI framework designed to provide interactive and engaging content using varied AI personalities. It's built on top of state-of-the-art machine learning algorithms and is perfect for applications in content creation, user interaction, and more.

## Installation

Ensure you have Python 3.8 or later installed on your system.

```bash
git clone https://github.com/story-squad/hoaxbot3000.git
cd hoaxbot3000
pip install -r requirements.txt
```

## Usage

HoaxBot3000 integrates several components for seamless AI operations:

- `LLMWrapper`: Manages communication with OpenAI's language models, essential for the `StorySquadBot` functionality.
- `StorySquadBot`: Orchestrates the AI personalities.
- `StorySquadAI`: The backbone of AI functionalities and is intended for use as a foundation for Story Squad's AI projects.
- `WebApi`: Provides a web interface for interacting with the AI.
- `Experiments`: Facilitates the structuring of data science and ML experiments.

To utilize the `StorySquadBot` and `LLMWrapper`, follow the steps below:

```python
from StSqLLMWrapper.llmwrapper import LLMWrapper, LLMResponse, LLMRequest
from StorySquadAI.Alphabots.story_squad_bot import StorySquadBot

# Initialize the LLMWrapper with your API key
llmwrapper = LLMWrapper(api_key='your-openai-api-key')

# Create a StorySquadBot instance with a personality and the LLMWrapper
bot = StorySquadBot(personality=your_personality, llmwrapper_for_bot=llmwrapper)

# Use the bot's methods to engage in conversations
response = bot.thing(prompt='Tell me about the Eiffel Tower.')
print(response)
```
### Testing

Unit tests and fixtures are located in /tests

### Starting the Web API

Navigate to the `src/StorySquadAI/WebApi` directory:

```bash
uvicorn app:app --reload
```

## Experiments
The `src/StorySquadAI/experiments` directory provides a structured approach for data science and ML experiments, ensuring reproducibility and systematic analysis.
### Bot Improvement Utilities

Within the `src/StorySquadAI/experiments/bot_improvement_utilities`, there is a script `generate_responses_to_grade.py` which is essential for evaluating and improving the performance of StorySquad's AI bots.

#### generate_responses_to_grade.py

This script generates responses from a specified bot for a predefined list of queries. The queries are divided into three categories: things, people, and movies. Each response is then converted into an embedding using OpenAI's similarity engine, which allows for a numerical representation of the response's content that can be used for further analysis.

##### Features

- **Response Generation**: It fetches responses from the bot for a given set of queries.
- **Embedding Extraction**: It computes embeddings for each response to facilitate quantitative analysis.
- **Result Categorization**: The responses and embeddings are categorized by query type for organized analysis.
- **Output Storage**: Results are saved into text files for subsequent grading and evaluation.

##### Workflow

1. Create an instance of `StorySquadAI` and use it to instantiate a `StorySquadBot` with a specific personality.
2. Generate responses for a list of queries by calling the bot's `thing`, `person`, and `movie` methods.
3. Retrieve and store the embeddings of these responses.
4. Save the generated responses and their embeddings into text files.
5. Print completion status for each category of queries.

##### Usage

Run the script and input the desired bot's name when prompted. Specify the number of queries to process and the engine to be used (default is "curie"). The script will output text files containing the responses and their embeddings.

This utility is a vital part of the continuous improvement cycle for the AI models, ensuring that the bots become more effective and accurate over time.

For more information about how to use this script, refer to the `/src/StorySquadAI/experiments/bot_improvement_utilities/generate_responses_to_grade.py` in the repository.




## No License Granted

### :warning: IMPORTANT :warning:

This repository is made publicly available for the purposes of portfolio review and personal reference by potential employers or collaborators. **No license is granted for any other use.** This means you may not use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the software or any derivative works without express written permission from the author.

If you are interested in using any parts of this work for purposes other than what is explicitly allowed above, please contact me directly to discuss licensing.


## Contact

For questions or support, please open an issue in the GitHub repository.

For detailed instructions on how to interact with `StorySquadBot` and utilize the `LLMWrapper`, refer to the implementation details in the `/src/Alphabots/story_squad_bot.py` module.
