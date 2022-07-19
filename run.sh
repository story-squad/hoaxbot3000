echo "starts the docker ccontainer on STORY_SQUAD_AI_PORT"
export STORY_SQUAD_AI_PORT=3002
# -p = outside:inside
docker run -p 127.0.0.1:$STORY_SQUAD_AI_PORT:4564 -t story-squad-ai