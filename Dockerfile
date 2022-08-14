FROM python:slim
ARG OPENAI_API_KEY
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

ENV DATABASE_FILE=/src/StorySquadAI/WebApi/sql_app.db
ENV STORYSQUADAI_PATH=/src/StorySquadAI/
ENV OPENAI_API_KEY=${OPENAI_API_KEY}

WORKDIR /
COPY ./src /src
COPY ./submodules /submodules
COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir --upgrade -r /requirements.txt
CMD ["uvicorn", "src.StorySquadAI.WebApi.app:app", "--host", "0.0.0.0", "--port", "4564"]
# uvicorn src.StorySquadAI.WebApi.app:app --host 0.0.0.0 --port 80