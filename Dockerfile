#FROM python:3.9
#FROM alpine
FROM python:slim
#ENV PYTHONUNBUFFERED=1
#ADD http://dl-cdn.alpinelinux.org/alpine/latest-stable/main/ /etc/apk/repositories
#RUN apk add --update python python-dev gfortran py-pip build-base py-numpy@community

#RUN apk add --update --no-cache python3 musl-dev
#RUN apk add --update --no-cache git linux-headers g++
#RUN ln -sf python3 /usr/bin/python

RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

ENV STORYSQUADAI_PATH=/src/StorySquadAI/
ENV OPENAI_API_KEY=%OPENAI_API_KEY%

WORKDIR /
COPY ./src /src
COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir --upgrade -r /requirements.txt
CMD ["uvicorn", "src.StorySquadAI.WebApi.app:app", "--host", "0.0.0.0", "--port", "80"]
# uvicorn src.StorySquadAI.WebApi.app:app --host 0.0.0.0 --port 80