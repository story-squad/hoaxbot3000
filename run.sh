echo "starts the docker ccontainer on STORY_SQUAD_AI_PORT"
export STORY_SQUAD_AI_PORT=4564
docker run -p $STORY_SQUAD_AI_PORT:80 -t story-squad-ai