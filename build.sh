#!/usr/bin/env sh
echo "Builds the deployment docker container for StorySquadAI"
export STORY_SQUAD_AI_PORT=3002
docker build --build-arg OPENAI_API_KEY=${OPENAI_API_KEY} --build-arg STORY_SQUAD_AI_PORT=${STORY_SQUAD_AI_PORT} --force-rm -t story-squad-ai:latest .