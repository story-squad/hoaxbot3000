#!/usr/bin/env sh
echo "Builds the deployment docker container for StorySquadAI"
docker build --build-arg OPENAI_API_KEY=${OPENAI_API_KEY} --force-rm -t story-squad-ai:latest .